import numpy as np


def _np_array(x):
    """Convert C-array or sequence to numpy array"""
    return np.array(x, dtype=np.float64)

def _is_uproot(obj):
    return hasattr(obj, "classname")

def _get_array_centers(array, round: int = 2):
    array = np.array(array, dtype=np.float64)
    return np.round(0.5 * (array[:-1] + array[1:]), round)
