import numpy as np
from theoris.utils.ordered_set import OrderedSet
from theoris.base_symbol import BaseSymbol
from theoris.utils.ordered_set import OrderedSet

np.seterr(all='ignore')


def get_code_name(name: str, start_name: str = None, is_camel_case=True):
    cleaned_name = (
        name
        .replace("$", "")
        .replace("\\", "")
        .replace("_{", "")
        .replace("}", "")
    )

    code_name = (
        "_".join(
            cleaned_name
            .lower()
            .split()
        ) if is_camel_case else cleaned_name.replace(" ", "")
    )

    if start_name is not None:
        return "_".join([start_name, code_name])
    return code_name


def get_dependency_symbols(symbol: BaseSymbol) -> OrderedSet[BaseSymbol]:
    try:
        if isinstance(symbol.expression, (float, int)):
            return OrderedSet()
        return OrderedSet(symbol.expression.atoms(BaseSymbol))
    except:
        return OrderedSet()


def is_symbol_constant(symbol: BaseSymbol):
    if isinstance(symbol.expression, (float, int)):
        return True
    elif isinstance(symbol, BaseSymbol):
        arg_symbols = get_dependency_symbols(symbol)
        return len(arg_symbols) == 0
    else:
        return False


def resolve(expr: BaseSymbol, substitutions: dict = {}, no_resolve: list[BaseSymbol] = []) -> BaseSymbol:
    next_expr = expr
    dep_symbols = next_expr.atoms(BaseSymbol)

    for symbol in dep_symbols:
        if isinstance(symbol, BaseSymbol) and symbol not in no_resolve:
            if (symbol in substitutions):
                next_expr = next_expr.subs(symbol, substitutions[symbol])
            else:
                if hasattr(symbol, 'expression'):
                    next_expr = next_expr.subs(symbol, symbol.expression)
                    if symbol.is_assigned():
                        next_expr = resolve(
                            next_expr, substitutions, no_resolve)

    return next_expr


def resolve_symbols(expr: BaseSymbol, substitutions: dict = {}, no_resolve: list[BaseSymbol] = []):
    final_expr = resolve(expr, substitutions, no_resolve)
    dep_symbols = final_expr.atoms(BaseSymbol)
    return list(dep_symbols)
