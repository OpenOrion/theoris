from typing import Literal
from theoris.doc_object import DocObject
import sympy
from pint import Quantity
from theoris.utils.ordered_set import OrderedSet
from theoris.utils.units import ureg
from theoris.utils.logging import logger


class SymbolCodeCtx:
    """
    Context for code generation of symbols.

    This class provides context information for generating code representations
    of symbols, particularly the function name prefix to use.

    Attributes:
        func_start_name: The prefix to use for function names in generated code.
    """

    def __init__(self, func_start_name: str):
        """
        Initialize a SymbolCodeCtx with a function name prefix.

        Args:
            func_start_name: The prefix to use for function names in generated code.
        """
        self.func_start_name = func_start_name


NumType = Literal["real", "int"]


class BaseSymbol(sympy.Symbol, DocObject):
    """
    Interface for symbolic variables with additional metadata.

    ISymbol inherits from both sympy.Symbol for symbolic computation capabilities
    and DocObject for documentation capabilities. It represents a symbolic variable
    with additional metadata such as description, units, and LaTeX representation.

    Attributes:
        name: The name of the symbol.
        description: Human-readable description of what the symbol represents.
        latex: LaTeX representation of the symbol.
        units: Physical units of the symbol (using quantities library).
        num_type: The numeric type of the symbol (default: "Quantity").
        section: The Section this symbol belongs to, if any.
        is_global: Whether this symbol is globally accessible.
        is_simplified: Whether this symbol has been simplified.
        has_forced_unit_conversion: Whether unit conversion is forced for this symbol.
    """

    def __init__(self, name: str,
                 section=None,
                 description: str = None,
                 latex: str = None,
                 units: Quantity = None,
                 num_type: NumType = "real",
                 is_global: bool = False,
                 is_simplified: bool = False,
                 has_forced_unit_conversion: bool = False
                 ) -> None:
        """
        Initialize an ISymbol with the given attributes.

        Args:
            name: The name of the symbol.
            section: The Section this symbol belongs to, if any.
            description: Human-readable description of what the symbol represents.
                        Defaults to the symbol name if None.
            latex: LaTeX representation of the symbol. Defaults to the symbol name if None.
            units: Physical units of the symbol. Defaults to dimensionless if None.
            num_type: The numeric type of the symbol. Defaults to "Quantity" if None.
            is_global: Whether this symbol is globally accessible. Defaults to False.
            is_simplified: Whether this symbol has been simplified. Defaults to False.
            has_forced_unit_conversion: Whether unit conversion is forced for this symbol.
                                       Defaults to False. Not recommended for safety.
        """
        self.name = name
        self.description = description if description is not None else name
        self.latex = latex if latex is not None else name
        # Convert pint units to a format that can be used in sympy expressions
        if units is not None:
            # If it's already a Quantity, use it
            if isinstance(units, Quantity):
                self.units = units
            # If it's a string, parse it
            elif isinstance(units, str):
                self.units = ureg.parse_expression(units)
            # Otherwise, assume it's a valid unit expression
            else:
                try:
                    # Try to convert to a Quantity
                    self.units = ureg.Quantity(1, units)
                except:
                    # If that fails, use dimensionless
                    logger.warning(
                        f"{name} has invalid units {units}, using dimensionless")
                    self.units = ureg.dimensionless
        else:
            self.units = ureg.dimensionless
        self.num_type = num_type

        from theoris.section import Section
        self.section: Section = section
        if section:
            self.section.add_statement(self)
        self.is_global = is_global
        self.is_simplified = is_simplified
        self.has_forced_unit_conversion = has_forced_unit_conversion
        if has_forced_unit_conversion:
            logger.warning(
                f"{self.name} has has_forced_unit_conversion which is not advised for safety")

    def set_section(self, section):
        """
        Set the Section this symbol belongs to.

        Args:
            section: The Section object this symbol should belong to.
        """
        self.section = section

    def get_dependencies(self):
        """
        Get the symbols this symbol depends on.

        Returns:
            OrderedSet of ISymbol objects that this symbol depends on.
            Base implementation returns an empty set.
        """
        dependencies: OrderedSet[BaseSymbol] = OrderedSet()
        return dependencies

    def initialize(self):
        """
        Initialize this symbol.

        This method is called when the symbol is added to a Documentation object.
        Base implementation does nothing.
        """
        pass

    def get_module_section(self):
        """
        Get the Section this symbol belongs to.

        Returns:
            The Section object this symbol belongs to.
        """
        return self.section

    def is_assigned(self) -> bool:
        """
        Check if this symbol is assigned a value.

        Returns:
            True if this symbol is assigned a value, False otherwise.
            Base implementation is a placeholder.
        """
        pass

    def _repr_latex_(self) -> str:
        """
        Get the LaTeX representation of this symbol.

        Returns:
            String containing the LaTeX representation.
            Base implementation is a placeholder.
        """
        pass

    def _repr_code_(self, ctx: SymbolCodeCtx) -> str:
        """
        Get the code representation of this symbol.

        Args:
            ctx: The context for code generation.

        Returns:
            String containing the code representation.
            Base implementation is a placeholder.
        """
        pass

    @property
    def external_modules(self) -> list[str]:
        """
        Get the external modules required by this symbol.

        Returns:
            List of strings containing the names of required external modules.
            Base implementation returns an empty list.
        """
        return []

    @property
    def units_str(self) -> str:
        """
        Get a string representation of this symbol's units.

        Returns:
            String representation of the symbol's original units.
        """
        return str(self.units)

    @property
    def latex_str(self) -> str:
        """
        Get the LaTeX representation of this symbol.

        Returns:
            String containing the LaTeX representation.
        """
        return self._repr_latex_()
