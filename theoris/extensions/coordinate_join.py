import uuid
from theoris.utils.ordered_set import OrderedSet
import sympy
from pint import Quantity
from theoris import BaseSymbol, Section, SymbolCodeCtx
from theoris.utils.ordered_set import OrderedSet


class CoordinateJoin(BaseSymbol):
    def __new__(cls,
                name: str,
                coordinates: list[BaseSymbol],
                section: Section = None,
                description: str = None,
                latex: str = None,
                units: Quantity = None):
        return sympy.Symbol.__new__(cls, str(uuid.uuid4())+name)

    def __init__(self,
                 name: str,
                 coordinates: list[BaseSymbol],
                 section: Section = None,
                 description: str = None,
                 latex: str = None,
                 units: Quantity = None) -> None:
        super().__init__(name, section, description, latex, units)
        assert (len(coordinates) == 2)
        self.coordinates = coordinates

    def is_assigned(self):
        return True

    def get_dependencies(self) -> OrderedSet[BaseSymbol]:
        return OrderedSet(self.coordinates)

    def _repr_latex_(self):
        return "${name} = [...{append_1}, \\ ...flip({append_2})]$".format(
            name=self.latex,
            append_1=self.coordinates[0].latex,
            append_2=self.coordinates[1].latex
        )

    @property
    def external_modules(self) -> list[str]:
        return ["from theoris.utils.numpy import create_array"]

    def _repr_code_(self, ctx: SymbolCodeCtx):
        return (
            "{name} = create_array({arr1_symbol_name}, np.flip({arr2_symbol_name}))"
            .format(
                name=self.name,
                arr1_symbol_name=self.coordinates[0].name,
                arr2_symbol_name=self.coordinates[1].name
            )
        )
