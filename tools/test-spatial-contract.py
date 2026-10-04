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
                self.assertIn("support_region one of []", errors[0])

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


if __name__ == '__main__':
    unittest.main()
