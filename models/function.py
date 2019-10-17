from numbers import Number
from models.variable import Variable


class Function:
    def __init__(self, coefficients_variables: list, name='F(x)'):
        self.name = str(name)

        self.coefficients = []
        self.variables = []
        if not coefficients_variables or not all(isinstance(x, tuple) for x in coefficients_variables):
            raise ValueError("Coefficients variables list must be a list of tuples. Eg: [(1, x1), (2, x2)]")
        for c, v in coefficients_variables:
            if not isinstance(c, Number):
                raise TypeError("Coefficient must be a number")
            if not isinstance(v, Variable):
                raise TypeError("Variable must be a Variable() object")
            self.coefficients.append(c)
            self.variables.append(v)

    def __repr__(self):
        f_rep = '{0}:'.format(self.name)

        for index, c in enumerate(self.coefficients):
            if c >= 0:
                f_rep = f_rep + ' + {0}*{1}'.format(str(c), self.variables[index].internal_name)
            else:
                f_rep = f_rep + ' {0}*{1}'.format(str(c), self.variables[index].internal_name)

        return f_rep


class ObjectiveFunction(Function):
    def __init__(self, function_type: str, coefficients_variables: list, name='F(x)'):
        if function_type != 'min' and function_type != 'max':
            raise ValueError("ObjectiveFunction type must be either 'min' or 'max'.")

        self.function_type = function_type
        super().__init__(coefficients_variables, name)

    def __repr__(self):
        f_rep = '{0} {1}:'.format(self.function_type, self.name)

        for index, c in enumerate(self.coefficients):
            if c >= 0:
                f_rep = f_rep + ' + {0}*{1}'.format(str(c), self.variables[index].internal_name)
            else:
                f_rep = f_rep + ' {0}*{1}'.format(str(c), self.variables[index].internal_name)

        return f_rep


class Constraint:
    def __init__(self, coefficients_variables: list, equality_operator: str, right_side: Number, name='R(x)'):

        self.name = str(name)

        if equality_operator != '<=' and equality_operator != '=' and equality_operator != '>=':
            raise ValueError("Equality operator must be either '<=' or '=' or '>='")

        if coefficients_variables is None or not all(isinstance(x, tuple) for x in coefficients_variables):
            raise ValueError("Coefficients variables list must be a list of tuples. Eg: [(1, x1), (2, x2)]")

        if right_side is None or not isinstance(right_side, Number):
            raise TypeError("Right side must be a number")

        self.equality_operator = equality_operator
        self.right_side = right_side

        self.coefficients = []
        self.variables = []

        for c, v in coefficients_variables:
            if not isinstance(c, Number):
                raise TypeError("Coefficient must be a number")
            if not isinstance(v, Variable):
                raise TypeError("Variable must be a Variable() object")
            self.coefficients.append(c)
            self.variables.append(v)

    def __repr__(self):
        f_rep = '{0}:'.format(self.name)

        for index, c in enumerate(self.coefficients):
            if c >= 0:
                f_rep = f_rep + ' + {0}*{1}'.format(str(c), self.variables[index].internal_name)
            else:
                f_rep = f_rep + ' {0}*{1}'.format(str(c), self.variables[index].internal_name)

        f_rep = f_rep + ' {0} {1}'.format(self.equality_operator, self.right_side)

        return f_rep


if __name__ == '__main__':
    x1 = Variable()
    x2 = Variable()
    x3 = Variable()

    fo = ObjectiveFunction('min', [(1, x1), (2, x2)])
    c1 = Constraint([(-1, x1), (-2, x2)], '>=', -4)
    print('Function unit test passed')