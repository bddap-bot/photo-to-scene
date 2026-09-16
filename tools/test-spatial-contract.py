import unittest
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('spatial_contract', Path(__file__).with_name('spatial-contract.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
polygon_distance = module.polygon_distance
check_observed = module.check_observed


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


if __name__ == '__main__':
    unittest.main()
