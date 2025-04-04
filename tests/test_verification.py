"""
Tests for the proof verification module.
"""

import unittest
import sympy
from theoris.utils.units import *
from theoris import Symbol, Section
from theoris.verification import (
    verify, implies, forall, exists,
    Constraint, PropertyConstraint, EquivalenceConstraint, ImplicationConstraint
)
from theoris.verification.pysmt_interface import (
    SymPyToPySMTConverter, verify_property, check_equivalence, check_implication
)


class TestPySMTInterface(unittest.TestCase):
    """Test the PySMT interface."""
    
    def test_converter(self):
        """Test the SymPyToPySMTConverter."""
        converter = SymPyToPySMTConverter()
        
        # Test converting a simple expression
        x = sympy.Symbol('x')
        y = sympy.Symbol('y')
        expr = x + y
        formula = converter.convert(expr)
        self.assertIsNotNone(formula)
        
        # Test converting a relational expression
        expr = x > y
        formula = converter.convert(expr)
        self.assertIsNotNone(formula)
        
        # Test converting a logical expression
        expr = sympy.And(x > 0, y > 0)
        formula = converter.convert(expr)
        self.assertIsNotNone(formula)
    
    def test_verify_property(self):
        """Test the verify_property function."""
        x = sympy.Symbol('x')
        y = sympy.Symbol('y')
        
        # Test a valid property
        expr = sympy.Implies(x > 0, x**2 > 0)
        is_valid, counterexample = verify_property(expr)
        self.assertTrue(is_valid)
        self.assertIsNone(counterexample)
        
        # Test an invalid property
        expr = x**2 < 0
        is_valid, counterexample = verify_property(expr)
        self.assertFalse(is_valid)
        self.assertIsNotNone(counterexample)
    
    def test_check_equivalence(self):
        """Test the check_equivalence function."""
        x = sympy.Symbol('x')
        
        # Test equivalent expressions
        expr1 = x**2 - 2*x + 1
        expr2 = (x - 1)**2
        is_equivalent, counterexample = check_equivalence(expr1, expr2)
        self.assertTrue(is_equivalent)
        self.assertIsNone(counterexample)
        
        # Test non-equivalent expressions
        expr1 = x**2
        expr2 = x**3
        is_equivalent, counterexample = check_equivalence(expr1, expr2)
        self.assertFalse(is_equivalent)
        self.assertIsNotNone(counterexample)
    
    def test_check_implication(self):
        """Test the check_implication function."""
        x = sympy.Symbol('x')
        
        # Test valid implication
        antecedent = x > 0
        consequent = x**2 > 0
        is_valid, counterexample = check_implication(antecedent, consequent)
        self.assertTrue(is_valid)
        self.assertIsNone(counterexample)
        
        # Test invalid implication
        antecedent = x > 0
        consequent = x < 0
        is_valid, counterexample = check_implication(antecedent, consequent)
        self.assertFalse(is_valid)
        self.assertIsNotNone(counterexample)


class TestConstraints(unittest.TestCase):
    """Test the constraint classes."""
    
    def test_constraint(self):
        """Test the Constraint class."""
        x = sympy.Symbol('x')
        constraint = Constraint(x > 0, "x is positive")
        result = constraint.verify()
        self.assertFalse(result.is_satisfied)  # Not satisfied without assumptions
        
        constraint = Constraint(sympy.Implies(x > 0, x**2 > 0), "If x is positive, x^2 is positive")
        result = constraint.verify()
        self.assertTrue(result.is_satisfied)
    
    def test_property_constraint(self):
        """Test the PropertyConstraint class."""
        x = Symbol("x", description="test variable")
        constraint = PropertyConstraint(x, x > 0, "x is positive")
        result = constraint.verify()
        self.assertFalse(result.is_satisfied)  # Not satisfied without assumptions
    
    def test_equivalence_constraint(self):
        """Test the EquivalenceConstraint class."""
        x = sympy.Symbol('x')
        constraint = EquivalenceConstraint(x**2 - 2*x + 1, (x - 1)**2, "Expressions are equivalent")
        result = constraint.verify()
        self.assertTrue(result.is_satisfied)
    
    def test_implication_constraint(self):
        """Test the ImplicationConstraint class."""
        x = sympy.Symbol('x')
        constraint = ImplicationConstraint(x > 0, x**2 > 0, "If x is positive, x^2 is positive")
        result = constraint.verify()
        self.assertTrue(result.is_satisfied)


class TestSymbolVerification(unittest.TestCase):
    """Test the ProofSymbol class."""
    
    def test_add_constraint(self):
        """Test adding constraints to a ProofSymbol."""
        x = Symbol("x", description="test variable")
        constraint = x.add_constraint(x > 0, "x is positive")
        self.assertIsInstance(constraint, PropertyConstraint)
        self.assertEqual(len(x.constraints), 1)
    
    def test_add_theorem(self):
        """Test adding theorems to a ProofSymbol."""
        x = Symbol("x", description="test variable")
        theorem = x.add_theorem(x > 0, x**2 > 0, "If x is positive, x^2 is positive")
        self.assertIsInstance(theorem, ImplicationConstraint)
        self.assertEqual(len(x.theorems), 1)
    
    def test_verify_constraints(self):
        """Test verifying constraints of a ProofSymbol."""
        x = Symbol("x", 5, description="test variable")
        x.add_constraint(x > 0, "x is positive")
        results = x.verify_constraints()
        self.assertEqual(len(results), 1)
        self.assertTrue(list(results.values())[0].is_satisfied)
    
    def test_verify_expression(self):
        """Test verifying a specific expression involving a ProofSymbol."""
        x = Symbol("x", 5, description="test variable")
        result = x.verify_expression(x > 0, "x is positive")
        self.assertTrue(result.is_satisfied)
    
    def test_check_equivalence(self):
        """Test checking equivalence with a ProofSymbol."""
        x = Symbol("x", sympy.Symbol('x')**2, description="test variable")
        result = x.check_equivalence((sympy.Symbol('x'))**2, "Expressions are equivalent")
        self.assertTrue(result.is_satisfied)


class TestSectionVerification(unittest.TestCase):
    """Test the ProofSection class."""
    
    def test_add_assumption(self):
        """Test adding assumptions to a ProofSection."""
        section = Section("Test Section")
        assumption = section.add_assumption(sympy.Symbol('x') > 0, "x is positive")
        self.assertIsInstance(assumption, Constraint)
        self.assertEqual(len(section.assumptions), 1)
    
    def test_add_theorem(self):
        """Test adding theorems to a ProofSection."""
        section = Section("Test Section")
        theorem = section.add_theorem(sympy.Symbol('x') > 0, "x is positive")
        self.assertIsInstance(theorem, Constraint)
        self.assertEqual(len(section.theorems), 1)
    
    def test_add_implication_theorem(self):
        """Test adding implication theorems to a ProofSection."""
        section = Section("Test Section")
        theorem = section.add_implication_theorem(
            sympy.Symbol('x') > 0, sympy.Symbol('x')**2 > 0,
            "If x is positive, x^2 is positive"
        )
        self.assertIsInstance(theorem, ImplicationConstraint)
        self.assertEqual(len(section.theorems), 1)
    
    def test_add_equivalence_theorem(self):
        """Test adding equivalence theorems to a ProofSection."""
        section = Section("Test Section")
        theorem = section.add_equivalence_theorem(
            sympy.Symbol('x')**2 - 2*sympy.Symbol('x') + 1,
            (sympy.Symbol('x') - 1)**2,
            "Expressions are equivalent"
        )
        self.assertIsInstance(theorem, EquivalenceConstraint)
        self.assertEqual(len(section.theorems), 1)
    
    def test_verify_theorems(self):
        """Test verifying theorems in a ProofSection."""
        section = Section("Test Section")
        section.add_assumption(sympy.Symbol('x') > 0, "x is positive")
        section.add_theorem(sympy.Symbol('x')**2 > 0, "x^2 is positive")
        results = section.verify_theorems()
        self.assertEqual(len(results), 1)
        self.assertTrue(list(results.values())[0].is_satisfied)


class TestVerification(unittest.TestCase):
    """Test the verification module functions."""
    
    def test_verify(self):
        """Test the verify function."""
        x = Symbol("x", 5, description="test variable")
        x.add_constraint(x > 0, "x is positive")
        results = verify(x)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results["x"]), 1)
        self.assertTrue(list(results["x"].values())[0].is_satisfied)
    
    def test_implies(self):
        """Test the implies function."""
        x = sympy.Symbol('x')
        implication = implies(x > 0, x**2 > 0)
        self.assertIsInstance(implication, sympy.Implies)
    
    def test_forall(self):
        """Test the forall function."""
        x = sympy.Symbol('x')
        universal = forall(x, x**2 >= 0)
        self.assertEqual(universal, x**2 >= 0)  # For now, just returns the condition
    
    def test_exists(self):
        """Test the exists function."""
        x = sympy.Symbol('x')
        existential = exists(x, x**2 == 0)
        self.assertEqual(existential, x**2 == 0)  # For now, just returns the condition


if __name__ == '__main__':
    unittest.main()
