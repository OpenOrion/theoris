import unittest
from pint import Quantity
from theoris.utils.units import ureg
from theoris.base_symbol import BaseSymbol
from theoris.symbol import Symbol


class TestBaseSymbol(unittest.TestCase):
    def test_isymbol_initialization(self):
        symbol = BaseSymbol(name="TestSymbol", description="A test symbol")

        self.assertEqual(symbol.name, "TestSymbol")
        self.assertEqual(symbol.description, "A test symbol")
        self.assertEqual(symbol.units, ureg.dimensionless)  # Default is dimensionless


class TestSymbol(unittest.TestCase):
    def test_symbol_initialization(self):
        symbol = Symbol(name="TestSymbol", description="A test symbol")

        self.assertEqual(symbol.name, "TestSymbol")
        self.assertEqual(symbol.description, "A test symbol")
        self.assertEqual(symbol.units, ureg.dimensionless)  # Default is dimensionless


if __name__ == '__main__':
    unittest.main()
