import unittest
from pint import Quantity
from theoris.utils.units import ureg
from theoris.utils.units import validate_units


@validate_units(alpha="m", returns="m**2")
def calc_alpha_squared(alpha: Quantity, units="m**2"):
    return alpha * alpha


class CodegenValidateUnitsTest(unittest.TestCase):

    def test_validate_units_arg_input(self):
        alpha = 1000 * ureg.mm
        alpha_squared_actual = calc_alpha_squared(alpha)
        alpha_squared_expected = 1 * ureg.m**2
        self.assertEqual(alpha_squared_actual, alpha_squared_expected)

    def test_validate_units_kwarg_input(self):
        alpha = 1000 * ureg.mm
        alpha_squared_actual = calc_alpha_squared(alpha=alpha, units="m**2")
        alpha_squared_expected = 1 * ureg.m**2
        self.assertEqual(alpha_squared_actual, alpha_squared_expected)

    def test_validate_units_kwarg_input_ft2_output(self):
        alpha = 1000 * ureg.mm
        alpha_squared_actual = calc_alpha_squared(alpha=alpha, units="ft**2")
        alpha_squared_expected = 10.76391042 * ureg.ft**2
        self.assertAlmostEqual(alpha_squared_actual, alpha_squared_expected)


if __name__ == '__main__':
    unittest.main()
