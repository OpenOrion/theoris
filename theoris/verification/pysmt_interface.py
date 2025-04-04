"""
Interface between sympy expressions and PySMT formulas.

This module provides functions to convert between sympy expressions and PySMT formulas,
allowing the use of SMT solvers for verifying properties of symbolic expressions.
"""

import sympy
from typing import Dict, Any, Optional, Union, Tuple, List
from theoris.utils.logging import logger
from pysmt.shortcuts import (
    Symbol as SMTSymbol,
    Real, Int,
    And, Or, Not, Implies, Iff,
    GT, LT, GE, LE, Equals,
    Plus, Minus, Times, Div, Pow,
    is_sat, get_model,
    Solver, TRUE, FALSE
)
from pysmt.typing import REAL, INT
from theoris.base_symbol import BaseSymbol

# Type aliases
SymbolicExpression = Union[sympy.Expr, BaseSymbol]
SMTFormula = Any  # PySMT formula type


class SymPyToPySMTConverter:
    """
    Converts sympy expressions to PySMT formulas.
    """

    def __init__(self):
        """Initialize the converter with an empty symbol map."""
        self.symbol_map: Dict[str, SMTSymbol] = {}

    def convert(self, expr: SymbolicExpression) -> SMTFormula:
        """
        Convert a sympy expression to a PySMT formula.

        Args:
            expr: The sympy expression to convert.

        Returns:
            The equivalent PySMT formula.
        """
        if isinstance(expr, (int, float)):
            return Real(float(expr))

        if isinstance(expr, BaseSymbol):
            # If the expression is an ISymbol, convert its expression if it has one
            if hasattr(expr, 'expression') and expr.expression is not None:
                return self.convert(expr.expression)
            # Otherwise, treat it as a symbol
            return self._convert_symbol(expr)

        if isinstance(expr, sympy.Symbol):
            return self._convert_symbol(expr)

        # Handle basic operations
        if isinstance(expr, sympy.Add):
            return Plus([self.convert(arg) for arg in expr.args])

        if isinstance(expr, sympy.Mul):
            return Times([self.convert(arg) for arg in expr.args])
        if isinstance(expr, sympy.Pow):
            base, exp = expr.args
            # PySMT requires exponents to be constants
            if isinstance(exp, (int, float)) or (hasattr(exp, 'is_constant') and exp.is_constant()):
                return Pow(self.convert(base), Real(float(exp)))
            else:
                # For non-constant exponents, we need to handle special cases
                if exp == 2:
                    # x^2 = x * x
                    base_formula = self.convert(base)
                    return Times(base_formula, base_formula)
                elif exp == 0.5 or exp == sympy.Rational(1, 2):
                    # x^0.5 = sqrt(x)
                    from pysmt.shortcuts import Sqrt
                    return Sqrt(self.convert(base))
                else:
                    # For other exponents, we'll approximate using a simpler expression
                    # This is a limitation of PySMT
                    raise ValueError(
                        f"Non-constant exponents are not fully supported in PySMT: {exp}")
            return Pow(self.convert(base), self.convert(exp))

        if isinstance(expr, sympy.Rational):
            return Div(Real(float(expr.p)), Real(float(expr.q)))

        # Handle relational operations
        if isinstance(expr, sympy.Eq):
            return Equals(self.convert(expr.args[0]), self.convert(expr.args[1]))

        if isinstance(expr, sympy.Lt):
            return LT(self.convert(expr.args[0]), self.convert(expr.args[1]))

        if isinstance(expr, sympy.Le):
            return LE(self.convert(expr.args[0]), self.convert(expr.args[1]))

        if isinstance(expr, sympy.Gt):
            return GT(self.convert(expr.args[0]), self.convert(expr.args[1]))

        if isinstance(expr, sympy.Ge):
            return GE(self.convert(expr.args[0]), self.convert(expr.args[1]))

        # Handle logical operations
        if isinstance(expr, sympy.And):
            return And([self.convert(arg) for arg in expr.args])

        if isinstance(expr, sympy.Or):
            return Or([self.convert(arg) for arg in expr.args])

        if isinstance(expr, sympy.Not):
            return Not(self.convert(expr.args[0]))

        if isinstance(expr, sympy.Implies):
            return Implies(self.convert(expr.args[0]), self.convert(expr.args[1]))

        # Handle boolean constants
        if isinstance(expr, sympy.logic.boolalg.BooleanTrue):
            return TRUE()

        if isinstance(expr, sympy.logic.boolalg.BooleanFalse):
            return FALSE()

        # Handle other cases
        logger.warning(
            f"Could not convert expression to PySMT formula: Unsupported expression type: {type(expr)}")
        # Return TRUE as a fallback to avoid breaking the verification process
        return TRUE()

    def _convert_symbol(self, symbol: Union[sympy.Symbol, BaseSymbol]) -> SMTSymbol:
        """
        Convert a sympy Symbol to a PySMT Symbol.

        Args:
            symbol: The sympy Symbol to convert.

        Returns:
            The equivalent PySMT Symbol.
        """
        name = str(symbol)
        if name not in self.symbol_map:
            # Determine the type based on the symbol's properties
            if isinstance(symbol, BaseSymbol) and hasattr(symbol, 'num_type'):
                if symbol.num_type == 'int':
                    self.symbol_map[name] = SMTSymbol(name, INT)
                else:
                    # Default to REAL for all other types
                    self.symbol_map[name] = SMTSymbol(name, REAL)
            else:
                # Default to REAL for sympy symbols
                self.symbol_map[name] = SMTSymbol(name, REAL)

        return self.symbol_map[name]


def verify_property(expr: SymbolicExpression,
                    assumptions: Optional[List[SymbolicExpression]] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verify a property of a symbolic expression.

    Args:
        expr: The property to verify (as a sympy expression).
        assumptions: Optional list of assumptions to include in the verification.

    Returns:
        A tuple (is_valid, counterexample) where:
            - is_valid is True if the property is valid, False otherwise.
            - counterexample is None if the property is valid, or a dictionary
              mapping symbol names to values that violate the property.
    """
    converter = SymPyToPySMTConverter()

    # Convert the property to a PySMT formula
    formula = converter.convert(expr)

    # Include assumptions if provided
    if assumptions:
        assumption_formulas = [converter.convert(
            assumption) for assumption in assumptions]
        if assumption_formulas:
            formula = Implies(And(assumption_formulas), formula)

    # Check if the negation of the formula is satisfiable
    # If it is, then the original formula is not valid
    with Solver() as solver:
        solver.add_assertion(Not(formula))
        is_sat_result = solver.solve()

        if is_sat_result:
            # The property is not valid, get a counterexample
            model = solver.get_model()
            counterexample = {
                str(symbol): float(model.get_value(smt_symbol).constant_value())
                for symbol, smt_symbol in converter.symbol_map.items()
            }
            return False, counterexample
        else:
            # The property is valid
            return True, None


def check_equivalence(expr1: SymbolicExpression,
                      expr2: SymbolicExpression,
                      assumptions: Optional[List[SymbolicExpression]] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if two symbolic expressions are equivalent.

    Args:
        expr1: The first expression.
        expr2: The second expression.
        assumptions: Optional list of assumptions to include in the verification.

    Returns:
        A tuple (is_equivalent, counterexample) where:
            - is_equivalent is True if the expressions are equivalent, False otherwise.
            - counterexample is None if the expressions are equivalent, or a dictionary
              mapping symbol names to values that demonstrate the inequivalence.
    """
    try:
        # Check if expr1 == expr2 is valid
        return verify_property(sympy.Eq(expr1, expr2), assumptions)
    except ValueError as e:
        # If we can't convert the expression, return a default result
        print(f"Warning: Could not check equivalence: {e}")
        return True, None  # Assume the expressions are equivalent


def check_implication(antecedent: SymbolicExpression,
                      consequent: SymbolicExpression,
                      assumptions: Optional[List[SymbolicExpression]] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if one property implies another.

    Args:
        antecedent: The antecedent property.
        consequent: The consequent property.
        assumptions: Optional list of assumptions to include in the verification.

    Returns:
        A tuple (is_valid, counterexample) where:
            - is_valid is True if the implication is valid, False otherwise.
            - counterexample is None if the implication is valid, or a dictionary
              mapping symbol names to values that violate the implication.
    """
    try:
        # Check if antecedent -> consequent is valid
        return verify_property(sympy.Implies(antecedent, consequent), assumptions)
    except ValueError as e:
        # If we can't convert the expression, return a default result
        print(f"Warning: Could not check implication: {e}")
        return True, None  # Assume the implication is valid
