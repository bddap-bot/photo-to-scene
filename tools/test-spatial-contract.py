import json
import subprocess
import sys
import tempfile
import unittest
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('spatial_contract', Path(__file__).with_name('spatial-contract.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
polygon_distance = module.polygon_distance
check_observed = module.check_observed
check_contract = module.check_contract


class PolygonDistanceTest(unittest.TestCase):
    def test_low_confidence_region_uses_wider_tolerance(self):
        contract = {"footprint_xy": [[0, 0], [1, 0], [1, 1], [0, 1]], "front_xy": [0, 1], "regions": [{"id": "hidden", "bbox": {"min": [0, 0, 0], "max": [1, 1, 1]}, "confidence": .25}], "relationships": [], "ownership": {"children": "external"}}
        entries = {"one": {"id": "one", "spatial_contract": contract}}
        observed = {"one": {"footprint_xy": contract["footprint_xy"], "front_xy": [0, 1], "regions": [{"id": "hidden", "bbox": {"min": [0, 0, 0], "max": [1.3, 1, 1]}}], "owned_ids": ["one"]}}
        errors = []
        check_observed(entries, observed, ["one"], .1, errors)
        self.assertEqual(errors, [])

    def test_separated_collinear_edges(self):
        left = [[0, 0], [1, 0], [1, 1], [0, 1]]
        right = [[2, 0], [3, 0], [3, 1], [2, 1]]
        self.assertAlmostEqual(polygon_distance(left, right), 1)

    def test_touching(self):
        left = [[0, 0], [1, 0], [1, 1], [0, 1]]
        right = [[1, 0], [2, 0], [2, 1], [1, 1]]
        self.assertEqual(polygon_distance(left, right), 0)

    def test_containment(self):
        outer = [[0, 0], [3, 0], [3, 3], [0, 3]]
        inner = [[1, 1], [2, 1], [2, 2], [1, 2]]
        self.assertEqual(polygon_distance(outer, inner), 0)


def box_entry(ident, lo, hi, relationships=()):
    footprint = [[lo[0], lo[1]], [hi[0], lo[1]], [hi[0], hi[1]], [lo[0], hi[1]]]
    contract = {
        "source_evidence": {"synthetic": True},
        "frame": {"origin_xyz": [(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]], "x_axis_xy": [1, 0], "y_axis_xy": [0, 1], "size_xyz": [hi[i] - lo[i] for i in range(3)]},
        "footprint_xy": footprint,
        "front_xy": [0, 1],
        "regions": [{"id": "body", "bbox": {"min": list(lo), "max": list(hi)}}],
        "relationships": list(relationships),
        "ownership": {"children": "external"},
    }
    return {"id": ident, "bbox": {"min": list(lo), "max": list(hi)}, "spatial_contract": contract}


def resting(bottom, x=1.0, **relation):
    support = {"type": "supported_by", "with": "floor", "region": "body", "support_region": "body", **relation}
    return {"floor": box_entry("floor", [0, 0, -.1], [4, 4, 0]), "item": box_entry("item", [x, 1, bottom], [x + .5, 1.5, bottom + .5], [support])}


def declaration_errors(entries, tolerance=.03):
    errors = []
    check_contract(entries["item"], entries, tolerance, errors)
    return errors


def observed_errors(entries):
    observed = {ident: {**entry["spatial_contract"], "owned_ids": [ident]} for ident, entry in entries.items()}
    errors = []
    check_observed(entries, observed, list(entries), .03, errors)
    return errors


class SupportDeclarationTest(unittest.TestCase):
    def test_resting_on_support_top_is_accepted(self):
        self.assertEqual(declaration_errors(resting(0)), [])

    def test_gap_within_tolerance_is_accepted(self):
        self.assertEqual(declaration_errors(resting(.02)), [])

    def test_gap_beyond_given_tolerance_is_rejected(self):
        self.assertEqual(len(declaration_errors(resting(.02), tolerance=.01)), 1)

    def test_raised_region_is_rejected_with_measured_gap(self):
        errors = declaration_errors(resting(.06))
        self.assertEqual(len(errors), 1)
        self.assertIn("item: declared supported_by floor", errors[0])
        self.assertIn("+0.060 m", errors[0])

    def test_region_sunk_into_support_is_rejected(self):
        self.assertEqual(len(declaration_errors(resting(-.06))), 1)

    def test_footprint_beside_support_is_rejected(self):
        errors = declaration_errors(resting(0, x=4.5))
        self.assertEqual(len(errors), 1)
        self.assertIn("footprints are 0.500 m apart", errors[0])

    def test_missing_region_identifiers_are_rejected_with_choices(self):
        entries = resting(0)
        relation = entries["item"]["spatial_contract"]["relationships"][0]
        del relation["region"], relation["support_region"]
        errors = declaration_errors(entries)
        self.assertEqual(len(errors), 1)
        self.assertIn("region must name one of ['body'] and support_region one of ['body']", errors[0])

    def test_unresolvable_support_region_is_rejected(self):
        errors = declaration_errors(resting(0, support_region="top"))
        self.assertEqual(len(errors), 1)
        self.assertIn("support_region='top'", errors[0])

    def test_target_without_contract_is_rejected(self):
        for missing in (None, "absent"):
            with self.subTest(missing=missing):
                entries = resting(0)
                if missing:
                    del entries["floor"]["spatial_contract"]
                else:
                    entries["floor"]["spatial_contract"] = None
                errors = declaration_errors(entries)
                self.assertEqual(len(errors), 1)
                self.assertIn("relationship target floor has an invalid contract: floor: missing spatial_contract", errors[0])

    def test_malformed_target_footprint_is_rejected(self):
        entries = resting(0)
        entries["floor"]["spatial_contract"]["footprint_xy"][0] = [0]
        errors = declaration_errors(entries)
        self.assertEqual(len(errors), 1)
        self.assertIn("footprint_xy", errors[0])

    def test_observed_gate_applies_the_same_rule(self):
        self.assertEqual(observed_errors(resting(0)), [])
        errors = observed_errors(resting(.06))
        self.assertEqual(len(errors), 1)
        self.assertIn("item: observed supported_by floor", errors[0])


def validate(objects, observed=None):
    with tempfile.TemporaryDirectory() as directory:
        path, output = Path(directory, 'objects.json'), Path(directory, 'validation.json')
        path.write_text(objects if isinstance(objects, str) else json.dumps(objects))
        extra = []
        if observed is not None:
            Path(directory, 'observed.json').write_text(json.dumps(observed))
            extra = ['--observed', str(Path(directory, 'observed.json'))]
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('spatial-contract.py')), str(path), '--output', str(output), *extra], capture_output=True, text=True)
        return result, json.loads(output.read_text()) if output.exists() else None


class InventoryShapeTest(unittest.TestCase):
    def test_malformed_inventory_writes_shape_error(self):
        cases = (
            ('[{"id": "floor"', "not valid JSON"),
            ({"objects": [{"id": "floor"}]}, "top level must be a nonempty array"),
            ([], "got []"),
            ([{"id": "floor"}, "floor"], "objects.json[1]: entry must be an object"),
            ([{"label": "floor"}], "objects.json[0]: entry must be an object with a string id"),
            ([{"id": "floor"}, {"id": "floor"}], "duplicate id floor"),
        )
        for objects, message in cases:
            with self.subTest(objects=objects):
                result, validation = validate(objects)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(validation["valid"])
                self.assertTrue(any(message in error for error in validation["errors"]), validation["errors"])

    def test_declaration_errors_skip_the_observed_round_trip(self):
        result, validation = validate([{"id": "floor"}], observed={})
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(validation["errors"], ["floor: missing spatial_contract"])

    def test_every_entry_is_checked(self):
        result, validation = validate(list(resting(0).values()))
        self.assertEqual(result.returncode, 0, validation)
        self.assertEqual(validation["ids"], ["floor", "item"])


class ClosedContractTest(unittest.TestCase):
    def test_unchecked_appearance_fields_are_rejected_by_name(self):
        for field, value in (("line_width_m", .008), ("detail_correction", {"request": "Preserve the 0.008 m width"}), ("material_note", "plaster")):
            with self.subTest(field=field):
                entries = resting(0)
                entries["item"]["spatial_contract"]["appearance"] = {field: value}
                errors = declaration_errors(entries)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(f"item: spatial_contract.appearance.{field} is not a machine-checked appearance field", errors[0])

    def test_unknown_contract_field_is_rejected_by_name(self):
        entries = resting(0)
        entries["item"]["spatial_contract"]["blockout_shell_override"] = {"ceiling_z_m": 4.5}
        errors = declaration_errors(entries)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("item: spatial_contract.blockout_shell_override is not a contract field", errors[0])

    def test_source_visible_aperture_is_the_whole_appearance_contract(self):
        cases = (
            ({"aperture_background": "source_visible", "minimum_luminance": .2}, None),
            ({}, None),
            ({"aperture_background": "source_visible"}, "appearance must be"),
            ({"aperture_background": {"visibility": "not_observed"}, "minimum_luminance": .2}, "appearance must be"),
            ({"aperture_background": "source_visible", "minimum_luminance": 2}, "appearance must be"),
            ("source_visible", "appearance must be an object"),
        )
        for appearance, message in cases:
            with self.subTest(appearance=appearance):
                entries = resting(0)
                entries["item"]["spatial_contract"]["appearance"] = appearance
                errors = declaration_errors(entries)
                if message is None:
                    self.assertEqual(errors, [])
                else:
                    self.assertEqual(len(errors), 1, errors)
                    self.assertIn(message, errors[0])


class FieldShapeTest(unittest.TestCase):
    def test_malformed_entry_fields_write_named_errors(self):
        def mutated(change):
            entries = resting(0)
            change(entries["item"], entries["item"]["spatial_contract"])
            return list(entries.values())
        cases = (
            (lambda e, c: e.pop("bbox"), "item: bbox must be"),
            (lambda e, c: e.update(bbox=[0, 1]), "item: bbox must be"),
            (lambda e, c: e.update(spatial_contract={"x": 1}), "item: missing spatial_contract.frame"),
            (lambda e, c: e.update(spatial_contract=[1]), "item: spatial_contract must be an object"),
            (lambda e, c: c.update(footprint_xy={"a": 1}), "item: spatial_contract.footprint_xy must be"),
            (lambda e, c: c.update(front_xy="north"), "item: spatial_contract.front_xy must be"),
            (lambda e, c: c.update(frame=[0, 0, 0]), "item: spatial_contract.frame must be"),
            (lambda e, c: c["frame"].update(size_xyz=[1, "1", 1]), "item: spatial_contract.frame must be"),
            (lambda e, c: c.update(regions=["body"]), "item: spatial_contract.regions must be"),
            (lambda e, c: c["regions"][0].update(bbox={"min": [0, 0], "max": [1, 1]}), "item: spatial_contract.regions must be"),
            (lambda e, c: c.update(relationships={"with": "floor"}), "item: spatial_contract.relationships must be"),
            (lambda e, c: c.update(relationships=[{"type": "minimum_xy_clearance", "with": "floor"}]), "item: spatial_contract.relationships must be"),
            (lambda e, c: c.update(ownership="external"), "item: spatial_contract.ownership.children must be"),
            (lambda e, c: c.update(source_evidence="photo"), "item: spatial_contract.source_evidence must be"),
        )
        for change, message in cases:
            with self.subTest(message=message):
                result, validation = validate(mutated(change))
                self.assertEqual(result.returncode, 1)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(validation["valid"])
                self.assertTrue(any(message in error for error in validation["errors"]), validation["errors"])

    def test_malformed_observed_file_writes_named_error(self):
        entries = list(resting(0).values())
        good = {entry["id"]: {**entry["spatial_contract"], "owned_ids": [entry["id"]]} for entry in entries}
        cases = (
            (None, "observed.json: not valid JSON"),
            ("{", "observed.json: not valid JSON"),
            ([], "observed.json: top level must be an object keyed by object id, got list"),
            (dict(good, item=[1]), "item: observed record must be an object"),
            (dict(good, item=dict(good["item"], footprint_xy=5)), "item: observed record needs footprint_xy"),
            (dict(good, item=dict(good["item"], regions=[{"id": "body"}])), "item: observed regions must be"),
            (dict(good, item=dict(good["item"], owned_ids="item")), "item: observed owned_ids must be"),
            (dict(good, floor=dict(good["floor"], front_xy=None)), "floor: observed record needs"),
        )
        for observed, message in cases:
            with self.subTest(observed=observed):
                with tempfile.TemporaryDirectory() as directory:
                    objects, output, path = Path(directory, 'objects.json'), Path(directory, 'validation.json'), Path(directory, 'observed.json')
                    objects.write_text(json.dumps(entries))
                    if observed is not None:
                        path.write_text(observed if isinstance(observed, str) else json.dumps(observed))
                    result = subprocess.run([sys.executable, str(Path(__file__).with_name('spatial-contract.py')), str(objects), '--observed', str(path), '--output', str(output)], capture_output=True, text=True)
                    validation = json.loads(output.read_text()) if output.exists() else None
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertTrue(any(message in error for error in validation["errors"]), validation["errors"])

    def test_well_formed_observed_round_trip_passes(self):
        entries = list(resting(0).values())
        observed = {entry["id"]: {**entry["spatial_contract"], "owned_ids": [entry["id"]]} for entry in entries}
        result, validation = validate(entries, observed=observed)
        self.assertEqual(result.returncode, 0, validation)


if __name__ == '__main__':
    unittest.main()
