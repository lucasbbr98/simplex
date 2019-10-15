import numpy as np


def cast_to_numpy_array(values):
    if values is None:
        raise ValueError("You must initialize a Matrix object with a numpy array. eg Matrix(values=[1, 2])")
    return np.atleast_2d(values)
