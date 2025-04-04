from typing import Any, Callable, Dict
import numpy as np
from functools import wraps
from pint import UnitRegistry, Quantity

# Create a unit registry
ureg = UnitRegistry()


def validate_unit_from_arg_values(arg_values: Any, expected_units_values: list, rescaled_args: list):
    for i, arg_value in enumerate(arg_values):
        if not isinstance(arg_value, Quantity) and not isinstance(arg_value, Callable):
            raise ValueError("all args should be of type 'Quantity' or 'Callable'")
        expected_unit = expected_units_values[i]
        if isinstance(arg_value, Quantity):
            if arg_value.units != expected_unit:
                rescaled_args[i] = arg_value.to(expected_unit)
        elif isinstance(arg_value, Callable):
                #TODO: ensure external function had correct type output
                pass


def validate_units(**expected_units: str):
    def _validate_units(function: Callable[..., Quantity]):

        @wraps(function)
        def wrapper(*args, **kwargs):
            expected_units_arg_values = list(expected_units.values())
            arg_values = list(args)

            kwarg_dict = dict(filter(lambda kv: kv[0] != "units", kwargs.items()))
            kwarg_values = list(kwarg_dict.values())
            kwarg_keys = list(kwarg_dict.keys())
            expected_units_kwarg_values = [expected_units[key] for key in kwarg_dict.keys()]

            rescaled_args = arg_values
            rescaled_kwargs_values = kwarg_values

            validate_unit_from_arg_values(arg_values, expected_units_arg_values, rescaled_args)
            validate_unit_from_arg_values(kwarg_values, expected_units_kwarg_values, rescaled_kwargs_values)

            rescaled_kwargs = dict([(kwarg_keys[i], value) for (i, value) in enumerate(rescaled_kwargs_values)])

            function_output = function(*rescaled_args, **rescaled_kwargs)
            if "returns" in expected_units:
                return function_output.to(expected_units["returns"])
            elif "units" in kwargs:
                return function_output.to(kwargs["units"])

            return function_output
        return wrapper
    return _validate_units


def units_linspace(start: Quantity, stop: Quantity, steps: int, endpoint: bool = True):
    if isinstance(start, (float, int)) and isinstance(stop, Quantity):
        start = start * stop.units
    if isinstance(stop, (float, int)) and isinstance(start, Quantity):
        stop = stop * start.units

    if isinstance(start, (float, int)) and isinstance(stop, (float, int)):
        raise ValueError("either start or stop has to be Quantity")

    if isinstance(start, Quantity) and isinstance(stop, Quantity) and start.units != stop.units:
        raise ValueError("Quantity units have to be the same")

    return np.linspace(start.magnitude, stop.magnitude, steps, endpoint=endpoint) * start.units


def to_preferred_units(current_values: Dict, convert_units: Dict):
    updated_unit_values = current_values.copy()
    for current_value_key in current_values.keys():
        current_units = str(current_values[current_value_key].dimensionality)
        if current_units in convert_units:
            updated_unit_values[current_value_key] = current_values[current_value_key].to(
                convert_units[current_units]
            )

    return updated_unit_values

