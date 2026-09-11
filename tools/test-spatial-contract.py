import unittest
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('spatial_contract', Path(__file__).with_name('spatial-contract.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
polygon_distance = module.polygon_distance


class PolygonDistanceTest(unittest.TestCase):
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
