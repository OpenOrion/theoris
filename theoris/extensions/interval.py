import uuid
import sympy
from pint import Quantity
from theoris import BaseSymbol, SymbolCodeCtx, Section
from theoris.utils.ordered_set import OrderedSet


class IntervalSymbol(BaseSymbol):
    def __new__(cls,
                name: str,
                range: list[BaseSymbol],
                size=20,
                is_range=False,
                section=None,
                description: str = None,
                latex: str = None,
                units: Quantity = None):
        return sympy.Symbol.__new__(cls, str(uuid.uuid4())+name)

    def __init__(self,
                 name: str,
                 range: list[BaseSymbol],
                 size: int = 20,
                 is_range=False,
                 section: Section = None,
                 description: str = None,
                 latex: str = None,
                 units: Quantity = None) -> None:
        super().__init__(name, section, description, latex, units)
        assert (len(range) == 2)
        self.start, self.end = range
        self.size = self.end if is_range else size

    def get_dependencies(self):
        dependencies = OrderedSet()
        if isinstance(self.start, BaseSymbol):
            dependencies = dependencies.union(
                OrderedSet(self.start.atoms(BaseSymbol))
            )
        if isinstance(self.end, BaseSymbol):
            dependencies = dependencies.union(
                OrderedSet(self.end.atoms(BaseSymbol))
            )

        return dependencies

    def is_assigned(self):
        return True

    def _repr_latex_(self):
        return "{name} = [{bound_1}, {bound_2}]".format(
            name=self.latex,
            bound_1=self.start,
            bound_2=self.end
        )

    def _repr_code_(self, ctx: SymbolCodeCtx):
        return (
            "{name} = np.linspace({start}, {end}, {size})"
            .format(name=self.name,
                    start=self.start,
                    end=self.end,
                    size=self.size)
        )
