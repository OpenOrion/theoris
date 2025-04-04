import logging
from mpmath.functions.functions import sec
from theoris.utils.ordered_set import OrderedSet
import sympy
from theoris import BaseSymbol, SymbolCodeCtx, Section
from theoris.section import SymbolMapping
from theoris.symbol import Symbol
from theoris.utils.ordered_set import OrderedSet
from theoris.utils.logging import logger
import uuid
from theoris.utils.symbols import get_code_name


class FunctionSymbol(BaseSymbol):
    def __new__(cls,
                function: Symbol,
                mappings: list[SymbolMapping] = None,
                name: str = None,
                section: Section = None,
                description: str = None,
                latex: str = None,
                is_magnitude=False):
        return sympy.Symbol.__new__(cls, f"{uuid.uuid4()}_func_{name if name is not None else function.name}")

    def __init__(self,
                 function: Symbol,
                 mappings: list[SymbolMapping] = None,
                 name: str = None,
                 section: Section = None,
                 description: str = None,
                 latex: str = None,
                 is_magnitude: bool = False) -> None:
        self.function = function
        self.mappings = [] if mappings is None else mappings
        self.arg_mapping = dict()
        for mapping in self.mappings:
            self.arg_mapping[mapping.from_symbol] = mapping.to_symbol
        self.section = section
        self.function_args = OrderedSet([])
        self.is_magnitude = is_magnitude
        super().__init__(name=name if name is not None else function.name,
                         section=section,
                         description=(description or "").format(
                             description=function.description),
                         latex=latex if latex is not None else name,
                         units=function.units)

    def is_assigned(self):
        return True

    def get_dependencies(self) -> OrderedSet[BaseSymbol]:
        function_args = OrderedSet([])
        # TODO: This seems like it will not stand true all the time
        if self.function.section:
            for arg in self.function.section.args:
                if (arg in self.arg_mapping):
                    function_args.add(self.arg_mapping[arg])
                else:
                    function_args.add(arg)
        else:
            logger.warning("Symbol Function section is undefined!!")
            function_args = OrderedSet(self.arg_mapping.values())

        return function_args

    def initialize(self):
        self.function_args = self.get_dependencies()

    def get_module_section(self):
        return self.function.section

    def _repr_latex_(self):
        name = self.latex
        func_name = self.function.section.returns.latex
        args = ",".join([arg.latex for arg in self.function_args])
        return f"${name} = {func_name}({args})$"

    def _repr_code_(self, ctx: SymbolCodeCtx):
        name = self.name
        func_name = get_code_name(
            self.function.section.name, ctx.func_start_name)
        args = ",".join([arg.name for arg in self.function_args])
        code_str = f"{name} = {func_name}({args})"
        if self.is_magnitude:
            return f"{code_str}.magnitude"
        return code_str
