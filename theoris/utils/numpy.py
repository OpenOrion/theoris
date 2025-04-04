from typing import Iterable
import numpy as np
from quantities.quantity import Quantity


def isiterable(i: Iterable):
    try:
        i.__iter__()
        return True
    except:
        return False


def get_array_units(np_array: np.ndarray):
    if not isinstance(np_array, np.ndarray):
        raise ValueError("not an numpy array")
    quantity = np_array[0]
    if not isinstance(quantity, Quantity):
        raise ValueError("not a numpy array of Quantity")
    units = quantity.units
    for quantity in np_array:
        if quantity.units != units:
            raise ValueError("all elements in array must be the same type")
    return units


def create_array(*args):
    np_arrays: list[np.array] = []

    for np_array in args:
        if isinstance(np_array, float):
            np_arrays.append(np.array([np_array]))
        elif isinstance(np_array, Quantity):
            if isiterable(np_array):
                np_arrays.append(np_array)
            else:
                np_arrays.append(np.array([np_array])*np_array.units)
        elif isinstance(np_array, np.ndarray):
            np_arrays.append(np_array)
        elif isinstance(np_array, list):
            units = None
            for quantity in np_array:
                if not isinstance(quantity, Quantity):
                    raise Exception("list must contain Quantity")
                else:
                    if units is None or units == quantity.units:
                        units = quantity.units
                    else:
                        raise Exception(
                            "list must contain Quantity of same units")
            np_arrays.append(np.array(np_array)*units)

    array_units = None
    curr_array = np.array([])

    try:
        array_units = get_array_units(np_arrays[0])
        curr_array = curr_array * array_units
    except ValueError:
        pass

    for np_array in np_arrays:

        if (len(curr_array) > 0 and np_array[0] == curr_array[-1]):
            np_array[0] = np_array[0] + (0.0001/1000)*np_array[0].units

        if (array_units and get_array_units(np_array) != array_units):
            raise ValueError("units of all subarrays must be the same")
        curr_array = np.append(
            curr_array, np_array)*array_units if array_units else np.append(curr_array, np_array)
    return curr_array
