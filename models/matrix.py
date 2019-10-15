import numpy as np
from controllers.converters import cast_to_numpy_array


class Matrix:
    def __init__(self, values: np.ndarray):
        self.values = cast_to_numpy_array(values)
        self.lines = self.values.shape[0]
        self.columns = self.values.shape[1]

    def __setitem__(self, key, value):
        self.values[key] = value

    def __getitem__(self, item):
        return self.values[item]

    def __mul__(self, other):  # self * 2
        if not isinstance(other, Matrix):
            other = Matrix(other)

        return Matrix(np.dot(self.values, other.values))

    def __rmul__(self, other):  # 2 * self
        if not isinstance(other, Matrix):
            other = Matrix(other)

        return Matrix(np.dot(other.values, self.values))

    @property
    def m(self):
        return self.columns

    @property
    def n(self):
        return self.lines

    @property
    def inverse(self):
        return Matrix(np.linalg.inv(self.values))

    @property
    def _1(self):
        return self.inverse

    def __repr__(self):
        return repr(self.values)


if __name__ == '__main__':
    test_np = np.array([[1, 0, 1], [0, 1, 0], [1, 0 ,0]])
    test_matrix = Matrix(test_np)
    t_1 = test_matrix.inverse
    identity = test_matrix * t_1
    n = identity.lines
    m = identity.columns
    print('Matrix unit test passed')