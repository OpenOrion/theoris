from pint import Quantity
from theoris.utils.ordered_set import OrderedSet
import sympy
from theoris import BaseSymbol, SymbolCodeCtx
from theoris.section import SymbolMapping
from theoris.utils.ordered_set import OrderedSet
from theoris.utils.logging import logger
import uuid


class ExternalFunctionSymbol(BaseSymbol):
    def __new__(
        cls,
        name: str,
        description: str = None,
        latex: str = None,
        units: Quantity = None
    ):
        return sympy.Symbol.__new__(cls, f"{uuid.uuid4()}_ext_func_{name}")

    def __init__(self,
                 name: str,
                 description: str = None,
                 latex: str = None,
                 units: Quantity = None,
                 num_type: str = "real",
                 ) -> None:
        super().__init__(name=name,
                         section=None,
                         num_type=num_type,
                         description=description,
                         latex=latex if latex is not None else name,
                         units=units)

    @property
    def external_modules(self) -> list[str]:
        return ["from typing import Callable"]

    def is_assigned(self) -> bool:
        return True

    @property
    def type_hint(self) -> str:
        callable_arg_types = ",".join(
                ['Quantity']*len(self.section.args))
        return f"Callable[[{callable_arg_types}], Quantity]"


class ExternalFunctionCallerSymbol(BaseSymbol):
    def __new__(
        cls,
        external_function: ExternalFunctionSymbol,
        mappings: list[SymbolMapping],
        name: str,
        description: str = None,
        latex: str = None,
    ):
        return sympy.Symbol.__new__(cls, f"{uuid.uuid4()}_ext_func_caller_{name}")

    def __init__(
        self,
        external_function: ExternalFunctionSymbol,
        mappings: list[SymbolMapping],
        name: str,
        description: str,
        latex: str = None,
    ) -> None:
        self.mappings = mappings
        self.external_function = external_function
        self.arg_mapping = dict()
        for mapping in self.mappings:
            self.arg_mapping[mapping.from_symbol] = mapping.to_symbol
        self.function_args: OrderedSet[BaseSymbol] = OrderedSet([])

        super().__init__(name=name,
                         section=None,
                         description=(description or "").format(
                             description=self.external_function.description),
                         latex=latex if latex is not None else name,
                         units=self.external_function.units)

    def is_assigned(self):
        return True

    def get_dependencies(self) -> OrderedSet[BaseSymbol]:
        function_args = OrderedSet([self.external_function])
        if self.external_function.section:
            for arg in self.external_function.section.args:
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
        self.function_args.remove(self.external_function)

    def _repr_latex_(self):
        name = self.latex
        func_name = self.external_function.latex
        args = ",".join([arg.latex for arg in self.function_args])
        return f"${name} = {func_name}({args})$"

    def _repr_code_(self, ctx: SymbolCodeCtx):
        args = ",".join([arg.name for arg in self.function_args])
        code_str = f"{self.name} = {self.external_function.name}({args})"
        return code_str
