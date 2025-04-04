import uuid
import sympy
from pint import Quantity
from theoris import BaseSymbol, SymbolCodeCtx, Section
from theoris.utils.ordered_set import OrderedSet


class ArraySymbol(BaseSymbol):
    def __new__(cls,
                name: str,
                array: list[BaseSymbol],
                section=None,
                description: str = None,
                latex: str = None,
                units: Quantity = None):
        return sympy.Symbol.__new__(cls, str(uuid.uuid4())+name)

    def __init__(self,
                 name: str,
                 array: list[BaseSymbol],
                 section: Section = None,
                 description: str = None,
                 latex: str = None,
                 units: Quantity = None) -> None:
        super().__init__(name, section, description, latex, units)
        self.array = array

    def get_dependencies(self):
        dependencies = OrderedSet()
        for element in self.array:
            if isinstance(element, BaseSymbol):
                dependencies = dependencies.union(
                    OrderedSet(element.atoms(BaseSymbol))
                )
        return dependencies

    def is_assigned(self):
        return True

    @property
    def external_modules(self) -> list[str]:
        return ["from theoris.utils.numpy import create_array"]

    def _repr_latex_(self):
        return "{name} = [{elements}]".format(
            name=self.latex,
            elements=",".join(
                map(lambda element: str(element), self.array)
            )
        )

    def _repr_code_(self, ctx: SymbolCodeCtx):
        return (
            "{name} = create_array({elements})"
            .format(
                name=self.name,
                elements=",".join(
                    map(lambda element: str(element), self.array)
                )
            )
        )
