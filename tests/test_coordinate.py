import unittest
from sympy import Matrix
from pint import Quantity
from theoris.coordinate import Coordinate
from theoris.symbol import Symbol

class TestCoordinate(unittest.TestCase):
    def test_coordinate_initialization(self):
        ref_matrix = Matrix([1, 2])
        coord = Coordinate(name="TestCoord", ref=ref_matrix)
        
        self.assertEqual(coord.name, "TestCoord")
        self.assertEqual(coord.ref, ref_matrix)
        self.assertIsInstance(coord.x, Symbol)
        self.assertIsInstance(coord.y, Symbol)
        self.assertEqual(coord.x.name, "TestCoord_x")
        self.assertEqual(coord.y.name, "TestCoord_y")

if __name__ == '__main__':
    unittest.main()