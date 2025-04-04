"""
Proof verification module for Codegen Library.

This module provides tools for verifying mathematical properties and constraints
of symbolic expressions using SMT solvers through PySMT.
"""

from theoris.verification.constraints import Constraint, PropertyConstraint, EquivalenceConstraint, ImplicationConstraint, ProofResult
from theoris.verification.verification import verify, implies, forall, exists

__all__ = [
    'Constraint',
    'PropertyConstraint',
    'EquivalenceConstraint',
    'ImplicationConstraint',
    'ProofResult',
    'verify',
    'implies',
    'forall',
    'exists',
]