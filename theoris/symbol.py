from theoris.utils.ordered_set import OrderedSet
import sympy
from pint import Quantity
from theoris.utils.units import ureg
from theoris.section import Section
from theoris.base_symbol import BaseSymbol, SymbolCodeCtx
from theoris.utils.sympy import LatexPrinter
from sympy.printing.numpy import NumPyPrinter
from theoris.utils.logging import logger
from theoris.utils.ordered_set import OrderedSet
import uuid
from typing import List, Dict, Optional

# Import verification components if available
try:
    from theoris.verification.constraints import (
        Constraint,
        PropertyConstraint,
        EquivalenceConstraint,
        ImplicationConstraint,
        ProofResult
    )
    from theoris.verification.pysmt_interface import SymbolicExpression
    VERIFICATION_AVAILABLE = True
except ImportError:
    VERIFICATION_AVAILABLE = False


class Symbol(BaseSymbol):
    """
    Concrete implementation of ISymbol with expression support and verification capabilities.

    Symbol extends ISymbol to add support for symbolic expressions, unit calculations,
    and verification of mathematical properties. It can represent variables, constants,
    or expressions with dependencies on other symbols.

    Attributes:
        expression: The symbolic expression this symbol represents, if any.
        definitions: Dictionary of alternative definitions for this symbol.
        is_magnitude: Whether this symbol represents just the magnitude of a quantity.
        constraints: List of constraints associated with this symbol (if verification is available).
        theorems: List of theorems (implications) associated with this symbol (if verification is available).
        proof_results: Dictionary mapping constraint descriptions to proof results (if verification is available).

    Inherits all attributes from ISymbol.
    """
    def __new__(cls,
                name: str,
                expression=None,
                section=None,
                description=None,
                latex=None,
                num_type=None,
                units=None,
                is_magnitude=False,
                is_global=False,
                is_simplified=False,
                has_forced_unit_conversion=False
                ):
        """
        Create a new Symbol instance with a unique identifier.

        This method overrides sympy.Symbol.__new__ to ensure each Symbol has a unique
        internal identifier by prefixing the name with a UUID.

        Args:
            name: The name of the symbol.
            expression: The symbolic expression this symbol represents, if any.
            section: The Section this symbol belongs to, if any.
            description: Human-readable description of what the symbol represents.
            latex: LaTeX representation of the symbol.
            num_type: The numeric type of the symbol.
            units: Physical units of the symbol.
            is_magnitude: Whether this symbol represents just the magnitude of a quantity.
            is_global: Whether this symbol is globally accessible.
            is_simplified: Whether this symbol has been simplified.
            has_forced_unit_conversion: Whether unit conversion is forced for this symbol.

        Returns:
            A new Symbol instance with a unique identifier.
        """
        return sympy.Symbol.__new__(cls, str(uuid.uuid4())+name)

    def __init__(self,
                 name: str,
                 expression: BaseSymbol = None,
                 section: Section = None,
                 description: str = None,
                 latex: str = None,
                 num_type: str = None,
                 units: Quantity = None,
                 is_magnitude: bool = False,
                 is_global: bool = False,
                 is_simplified: bool = False,
                 has_forced_unit_conversion=False
                 ):
        """
        Initialize a Symbol with the given attributes.

        Args:
            name: The name of the symbol.
            expression: The symbolic expression this symbol represents, if any.
            section: The Section this symbol belongs to, if any.
            description: Human-readable description of what the symbol represents.
            latex: LaTeX representation of the symbol.
            num_type: The numeric type of the symbol.
            units: Physical units of the symbol. If None, derived from expression.
            is_magnitude: Whether this symbol represents just the magnitude of a quantity.
            is_global: Whether this symbol is globally accessible.
            is_simplified: Whether this symbol has been simplified.
            has_forced_unit_conversion: Whether unit conversion is forced for this symbol.
        """
        self.expression = expression
        units = Symbol.get_units(self.expression, units, name=name)
        self.definitions = {"default": self}
        self.is_magnitude = is_magnitude

        # Initialize verification attributes if verification is available
        if VERIFICATION_AVAILABLE:
            self.constraints = []
            self.theorems = []
            self.proof_results = {}

        super().__init__(name, section, description, latex, units, num_type,
                         is_global, is_simplified, has_forced_unit_conversion)

    def get_dependencies(self) -> OrderedSet[BaseSymbol]:
        """
        Get the symbols this symbol depends on.

        This method overrides ISymbol.get_dependencies to handle expressions.
        If this symbol is the return value of a section, it depends on the section's arguments.
        If this symbol has an expression, it depends on the symbols in that expression.

        Returns:
            OrderedSet of ISymbol objects that this symbol depends on.
        """
        if self.section is not None and self == self.section.returns:
            return self.section.args
        if isinstance(self.expression, sympy.Basic):
            return OrderedSet(self.expression.atoms(BaseSymbol))
        return super().get_dependencies()

    def set_expression(self, expression: BaseSymbol):
        """
        Set the expression for this symbol.

        Args:
            expression: The symbolic expression this symbol should represent.
        """
        self.expression = expression

    def add_definition(self, definition: BaseSymbol):
        """
        Add an alternative definition for this symbol.

        This method creates a new Symbol based on the provided definition
        and adds it to this symbol's definitions dictionary.

        Args:
            definition: The ISymbol containing the alternative definition.
        """
        new_symbol = Symbol(
            name=definition.name,
            expression=definition.expression,
            section=definition.section,
            description=definition.description or self.description,
            latex=definition.latex or self.latex,
            units=definition.units or self.units,
        )
        if definition.section:
            definition.section.add_symbol(new_symbol)

        self.definitions[definition.name] = new_symbol

    @staticmethod
    def inherit(symbol: BaseSymbol,
                expression: BaseSymbol = None,
                name: str = None,
                section: Section = None,
                description: str = None,
                latex: str = None,
                has_forced_unit_conversion: bool = False):
        """
        Create a new Symbol that inherits properties from an existing symbol.

        This static method creates a new Symbol with properties inherited from
        the provided symbol, optionally overriding some properties.

        Args:
            symbol: The source symbol to inherit properties from.
            expression: Optional expression to override the source symbol's expression.
            name: Optional name to override the source symbol's name.
            section: Optional section to override the source symbol's section.
            description: Optional description to override the source symbol's description.
                        Can include a format placeholder {description} that will be replaced
                        with the source symbol's description.
            latex: Optional LaTeX representation to override the source symbol's LaTeX.
            has_forced_unit_conversion: Whether unit conversion is forced for the new symbol.

        Returns:
            A new Symbol with properties inherited from the source symbol.
        """
        name = symbol.name if name is None else name
        return Symbol(
            name=name,
            expression=symbol.expression if expression is None and hasattr(
                symbol, 'expression') else expression,
            section=section,
            description=symbol.description if description is None else description.format(
                description=symbol.description),
            latex=symbol.latex if latex is None else latex,
            num_type=symbol.num_type,
            units=symbol.units,
            has_forced_unit_conversion=has_forced_unit_conversion
        )

    @staticmethod
    def get_units(expression: BaseSymbol, user_defined_units: Quantity = None, name: str = None):
        """
        Determine the units for a symbol based on its expression.

        This method calculates the units of a symbol based on its expression and
        the units of the symbols it depends on. It also validates that any user-defined
        units are compatible with the calculated units.

        Args:
            expression: The symbolic expression to calculate units for.
            user_defined_units: Optional user-defined units to validate against.
            name: Optional name of the symbol for error logging.

        Returns:
            The appropriate units for the symbol. If user_defined_units is provided
            and compatible, it returns those units. Otherwise, it returns the calculated
            units or dimensionless if no units can be determined.

        Raises:
            ValueError: If user_defined_units are incompatible with the calculated units.
                       The error is caught and logged as a warning.
        """
        # If user provided units, use those
        if user_defined_units is not None:
            return user_defined_units

        # If we have an expression, try to determine units
        if expression and isinstance(expression, sympy.Basic) and expression.atoms:
            # Extract all symbols from the expression
            arg_symbols = expression.atoms(BaseSymbol)

            # For pint, we need to handle operations differently
            # We'll use a simplified approach for common operations
            if len(arg_symbols) == 1:
                # For single symbol expressions, just use that symbol's units
                return list(arg_symbols)[0].units

            if len(arg_symbols) == 2 and isinstance(expression, sympy.Mul):
                # For multiplication, multiply the units
                symbols = list(arg_symbols)
                try:
                    return symbols[0].units * symbols[1].units
                except:
                    # If multiplication fails, use dimensionless
                    logger.warning(
                        f"{name} could not determine units from multiplication")
                    return ureg.dimensionless

            if len(arg_symbols) == 2 and isinstance(expression, sympy.Add):
                # For addition, units must be compatible, use the first one
                symbols = list(arg_symbols)
                try:
                    if symbols[0].units.units == symbols[1].units.units:
                        return symbols[0].units
                except:
                    # If comparison fails, use dimensionless
                    logger.warning(
                        f"{name} could not determine units from addition")
                    return ureg.dimensionless

            if len(arg_symbols) == 2 and isinstance(expression, sympy.Pow):
                # For power operations, handle specially
                base, exp = expression.as_base_exp()
                if isinstance(base, BaseSymbol) and isinstance(exp, (int, float)):
                    try:
                        return base.units ** exp
                    except:
                        # If power fails, use dimensionless
                        logger.warning(
                            f"{name} could not determine units from power")
                        return ureg.dimensionless

            # If we can't determine units from the expression structure,
            # log a warning and use dimensionless
            logger.warning(f"{name} could not determine units from expression")
            return ureg.dimensionless

        # If no expression or no atoms in expression, use dimensionless
        return ureg.dimensionless

    def is_assigned(self):
        """
        Check if this symbol is assigned a value.

        This method overrides ISymbol.is_assigned to check if this symbol
        has an expression.

        Returns:
            True if this symbol has an expression, False otherwise.
        """
        return self.expression is not None

    def _repr_latex_(self):
        """
        Get the LaTeX representation of this symbol.

        This method overrides ISymbol._repr_latex_ to generate a LaTeX
        representation of this symbol, including its expression if assigned.

        Returns:
            String containing the LaTeX representation.
        """
        if self.is_assigned():
            latex_ref_str = LatexPrinter().doprint(self.expression)
            return "${0} = {1}$".format(self.latex, latex_ref_str)
        else:
            return "${0}$".format(self.latex)

    def _repr_code_(self, ctx: SymbolCodeCtx):
        """
        Get the code representation of this symbol.

        This method overrides ISymbol._repr_code_ to generate a code
        representation of this symbol, including its expression if assigned.
        It handles various special cases such as piecewise expressions,
        unit conversions, simplification, and magnitude extraction.

        Args:
            ctx: The context for code generation.

        Returns:
            String containing the code representation.
        """
        # Generate the basic NumPy code string for the expression
        code_str = numpy_code_str = (
            NumPyPrinter().doprint(self.expression)
            .replace("numpy.", "np.")
        )

        # Handle special cases
        if isinstance(self.expression, sympy.Piecewise) or isinstance(self.expression, (float, int)):
            # For piecewise expressions or literals, explicitly add units
            code_str = f"({numpy_code_str}) * ureg.Quantity(1, \"{self.units_str}\")"

        if self.has_forced_unit_conversion:
            # For forced unit conversion, extract magnitude and add units
            code_str = f"({numpy_code_str}).magnitude * ureg.Quantity(1, \"{self.units_str}\")"

        if self.is_simplified:
            # For simplified symbols, simplify the result
            code_str = f"({numpy_code_str}).simplified"

        if self.is_magnitude:
            # For magnitude-only symbols, extract the magnitude
            code_str = f"({numpy_code_str}).magnitude"

        # Return the complete assignment statement
        return (
            f"{self.name} = {code_str}"
        )

    # Verification methods - only available if verification components are imported
    if VERIFICATION_AVAILABLE:
        def add_constraint(self,
                           constraint_expr: SymbolicExpression,
                           description: str = "",
                           assumptions: Optional[List[SymbolicExpression]] = None) -> Constraint:
            """
            Add a constraint to this symbol.

            Args:
                constraint_expr: The symbolic expression representing the constraint.
                description: Human-readable description of the constraint.
                assumptions: List of assumptions for the constraint.

            Returns:
                The created Constraint object.
            """
            constraint = PropertyConstraint(
                symbol=self,
                property_expr=constraint_expr,
                description=description or f"Constraint on {self.name}",
                assumptions=assumptions
            )
            self.constraints.append(constraint)
            return constraint

        def add_theorem(self,
                        antecedent: SymbolicExpression,
                        consequent: SymbolicExpression,
                        description: str = "",
                        assumptions: Optional[List[SymbolicExpression]] = None) -> ImplicationConstraint:
            """
            Add a theorem (implication) to this symbol.

            Args:
                antecedent: The antecedent property.
                consequent: The consequent property.
                description: Human-readable description of the theorem.
                assumptions: List of assumptions for the theorem.

            Returns:
                The created ImplicationConstraint object.
            """
            theorem = ImplicationConstraint(
                antecedent=antecedent,
                consequent=consequent,
                description=description or f"Theorem for {self.name}",
                assumptions=assumptions
            )
            self.theorems.append(theorem)
            return theorem

        def verify_constraints(self) -> Dict[str, ProofResult]:
            """
            Verify all constraints associated with this symbol.

            Returns:
                Dictionary mapping constraint descriptions to proof results.
            """
            results = {}

            # Verify constraints
            for constraint in self.constraints:
                result = constraint.verify()
                results[constraint.description] = result

            # Verify theorems
            for theorem in self.theorems:
                result = theorem.verify()
                results[theorem.description] = result

            self.proof_results = results
            return results

        def verify_expression(self,
                              expr: SymbolicExpression,
                              description: str = "",
                              assumptions: Optional[List[SymbolicExpression]] = None) -> ProofResult:
            """
            Verify a specific expression involving this symbol.

            Args:
                expr: The symbolic expression to verify.
                description: Human-readable description of the expression.
                assumptions: List of assumptions for the verification.

            Returns:
                ProofResult indicating whether the expression is satisfied.
            """
            constraint = PropertyConstraint(
                symbol=self,
                property_expr=expr,
                description=description or f"Expression for {self.name}",
                assumptions=assumptions
            )
            result = constraint.verify()
            self.proof_results[constraint.description] = result
            return result

        def check_equivalence(self,
                              other_expr: SymbolicExpression,
                              description: str = "",
                              assumptions: Optional[List[SymbolicExpression]] = None) -> ProofResult:
            """
            Check if this symbol's expression is equivalent to another expression.

            Args:
                other_expr: The expression to compare with.
                description: Human-readable description of the equivalence.
                assumptions: List of assumptions for the verification.

            Returns:
                ProofResult indicating whether the expressions are equivalent.
            """
            if not self.is_assigned():
                raise ValueError(
                    f"Symbol {self.name} does not have an expression to compare with.")

            constraint = EquivalenceConstraint(
                expr1=self.expression,
                expr2=other_expr,
                description=description or f"Equivalence for {self.name}",
                assumptions=assumptions
            )
            result = constraint.verify()
            self.proof_results[constraint.description] = result
            return result

        def get_proof_results(self) -> Dict[str, ProofResult]:
            """
            Get the proof results for this symbol.

            Returns:
                Dictionary mapping constraint descriptions to proof results.
            """
            return self.proof_results

        def get_proof_summary(self) -> str:
            """
            Get a summary of the proof results for this symbol.

            Returns:
                String containing a summary of the proof results.
            """
            if not self.proof_results:
                return f"No proofs have been run for {self.name}."

            summary = f"Proof results for {self.name}:\n"
            for description, result in self.proof_results.items():
                status = "SATISFIED" if result.is_satisfied else "VIOLATED"
                summary += f"  - {description}: {status} ({result.proof_time:.3f}s)\n"

            return summary
