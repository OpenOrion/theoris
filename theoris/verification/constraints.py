"""
Constraints for proof verification.

This module defines the Constraint class and its subclasses, which represent
mathematical properties and constraints that can be verified using SMT solvers.
"""

import sympy
import time
from typing import Dict, Any, Optional, Union, List, Tuple
from theoris.base_symbol import BaseSymbol
from theoris.verification.pysmt_interface import (
    verify_property,
    check_equivalence,
    check_implication,
    SymbolicExpression
)


class ProofResult:
    """
    Result of a proof verification.

    Attributes:
        is_satisfied: Whether the constraint is satisfied.
        counterexample: If not satisfied, a counterexample that violates the constraint.
        proof_time: Time taken to verify the constraint.
        description: Description of the constraint.
    """

    def __init__(self,
                 is_satisfied: bool,
                 counterexample: Optional[Dict[str, Any]] = None,
                 proof_time: float = 0.0,
                 description: str = ""):
        """
        Initialize a ProofResult.

        Args:
            is_satisfied: Whether the constraint is satisfied.
            counterexample: If not satisfied, a counterexample that violates the constraint.
            proof_time: Time taken to verify the constraint.
            description: Description of the constraint.
        """
        self.is_satisfied = is_satisfied
        self.counterexample = counterexample
        self.proof_time = proof_time
        self.description = description

    def __str__(self) -> str:
        """Return a string representation of the proof result."""
        result = f"Constraint '{self.description}': "
        if self.is_satisfied:
            result += f"SATISFIED (verified in {self.proof_time:.3f}s)"
        else:
            result += f"VIOLATED (counterexample found in {self.proof_time:.3f}s)"
            if self.counterexample:
                result += "\nCounterexample:"
                for symbol, value in self.counterexample.items():
                    result += f"\n  {symbol} = {value}"
        return result

    def _repr_latex_(self) -> str:
        """Return a LaTeX representation of the proof result."""
        if self.is_satisfied:
            return f"${{\color{{green}}\\checkmark}}$ {self.description} (verified in {self.proof_time:.3f}s)"
        else:
            latex = f"${{\color{{red}}\\times}}$ {self.description} (counterexample found in {self.proof_time:.3f}s)"
            if self.counterexample:
                latex += "\n\nCounterexample:\n\\begin{align}\n"
                for symbol, value in self.counterexample.items():
                    latex += f"{symbol} &= {value} \\\\\n"
                latex += "\\end{align}"
            return latex


class Constraint:
    """
    Base class for constraints that can be verified.

    Attributes:
        expression: The symbolic expression representing the constraint.
        description: Human-readable description of the constraint.
        assumptions: List of assumptions for the constraint.
    """

    def __init__(self,
                 expression: SymbolicExpression,
                 description: str = "",
                 assumptions: Optional[List[SymbolicExpression]] = None):
        """
        Initialize a Constraint.

        Args:
            expression: The symbolic expression representing the constraint.
            description: Human-readable description of the constraint.
            assumptions: List of assumptions for the constraint.
        """
        self.expression = expression
        self.description = description
        self.assumptions = assumptions or []

    def verify(self) -> ProofResult:
        """
        Verify the constraint.

        Returns:
            A ProofResult indicating whether the constraint is satisfied.
        """
        start_time = time.time()
        is_satisfied, counterexample = verify_property(
            self.expression, self.assumptions)
        proof_time = time.time() - start_time

        return ProofResult(
            is_satisfied=is_satisfied,
            counterexample=counterexample,
            proof_time=proof_time,
            description=self.description
        )

    def __str__(self) -> str:
        """Return a string representation of the constraint."""
        return f"Constraint: {self.description}"


class PropertyConstraint(Constraint):
    """
    A constraint representing a property that should hold for a symbol.

    This is a convenience subclass for constraints that represent properties
    of symbols, such as bounds, monotonicity, etc.
    """

    def __init__(self,
                 symbol: BaseSymbol,
                 property_expr: SymbolicExpression,
                 description: str = "",
                 assumptions: Optional[List[SymbolicExpression]] = None):
        """
        Initialize a PropertyConstraint.

        Args:
            symbol: The symbol to which the property applies.
            property_expr: The symbolic expression representing the property.
            description: Human-readable description of the property.
            assumptions: List of assumptions for the property.
        """
        super().__init__(property_expr, description, assumptions)
        self.symbol = symbol


class EquivalenceConstraint(Constraint):
    """
    A constraint representing the equivalence of two expressions.

    This is a convenience subclass for constraints that represent the
    equivalence of two expressions.
    """

    def __init__(self,
                 expr1: SymbolicExpression,
                 expr2: SymbolicExpression,
                 description: str = "",
                 assumptions: Optional[List[SymbolicExpression]] = None):
        """
        Initialize an EquivalenceConstraint.

        Args:
            expr1: The first expression.
            expr2: The second expression.
            description: Human-readable description of the equivalence.
            assumptions: List of assumptions for the equivalence.
        """
        super().__init__(sympy.Eq(expr1, expr2), description, assumptions)
        self.expr1 = expr1
        self.expr2 = expr2

    def verify(self) -> ProofResult:
        """
        Verify the equivalence constraint.

        Returns:
            A ProofResult indicating whether the expressions are equivalent.
        """
        start_time = time.time()
        is_satisfied, counterexample = check_equivalence(
            self.expr1, self.expr2, self.assumptions)
        proof_time = time.time() - start_time

        return ProofResult(
            is_satisfied=is_satisfied,
            counterexample=counterexample,
            proof_time=proof_time,
            description=self.description
        )


class ImplicationConstraint(Constraint):
    """
    A constraint representing an implication between two properties.

    This is a convenience subclass for constraints that represent implications,
    such as "if A then B".
    """

    def __init__(self,
                 antecedent: SymbolicExpression,
                 consequent: SymbolicExpression,
                 description: str = "",
                 assumptions: Optional[List[SymbolicExpression]] = None):
        """
        Initialize an ImplicationConstraint.

        Args:
            antecedent: The antecedent property.
            consequent: The consequent property.
            description: Human-readable description of the implication.
            assumptions: List of assumptions for the implication.
        """
        super().__init__(sympy.Implies(antecedent, consequent), description, assumptions)
        self.antecedent = antecedent
        self.consequent = consequent

    def verify(self) -> ProofResult:
        """
        Verify the implication constraint.

        Returns:
            A ProofResult indicating whether the implication is valid.
        """
        start_time = time.time()
        is_satisfied, counterexample = check_implication(
            self.antecedent, self.consequent, self.assumptions
        )
        proof_time = time.time() - start_time

        return ProofResult(
            is_satisfied=is_satisfied,
            counterexample=counterexample,
            proof_time=proof_time,
            description=self.description
        )
