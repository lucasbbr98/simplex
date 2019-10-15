from itertools import chain
from models_old.variable import Variable
from models_old.restriction import Restriction
import numpy as np


class LinearModel:
    def __init__(self, is_standard_form=False):
        self.objective_function = None
        self.restrictions = None
        self.is_standard_form = is_standard_form

        # Ax = b -> populates on transform_to_standard_form()
        self.A = None
        self.x = None
        self.b = None

        self.m = None
        self.n = None

        self.next_var_index = 0

    def build_objective_function(self, fo_type: str, variables: list, __do_not_rename__=False):
        self.objective_function = []
        if fo_type != 'min' and fo_type != 'max':
            raise ValueError("Argument fo_type must be 'min' or 'max'")

        if fo_type == 'max':
            print('[WARNING] max problems will be converted to min')

        for index, v in enumerate(variables):
            if isinstance(v, Variable):
                if fo_type == 'max':
                    v.fo_coefficient = -1 * v.fo_coefficient
                if not __do_not_rename__:
                    v.internal_name = 'x{0}'.format(index + 1)
                    v.internal_initial_index = index
                self.objective_function.append(v)
            else:
                raise TypeError("Expected argument of type Variable() but found {0}".format(type(v)))

    def print_objective_function(self):
        fo = 'Objective Function:\n min Fo(x) = '
        if not self.objective_function:
            print('No variables were added to the objective function...')
            return

        for index, v in enumerate(self.objective_function):
            if v.fo_coefficient >= 0:
                fo = fo + ' + {0}*{1}'.format(v.fo_coefficient, v.internal_name)
            else:
                fo = fo + ' {0}*{1} '.format(v.fo_coefficient, v.internal_name)

        print(fo)

    def add_restrictions(self, restrictions:list):
        self.restrictions = []
        for index, r in enumerate(restrictions):
            if isinstance(r, Restriction):
                # Adds 0 where needed
                for v in self.objective_function:
                    if v not in chain(*r.coefficients):
                        r.coefficients.append((0, v))

                # Sorts to make sure variables are in the correct order (X1, X2..)
                r.coefficients = sorted(r.coefficients, key=Variable.get_key)
                r.internal_name = 'R{0}'.format(index + 1)
                r.internal_initial_index = index
                self.__add_restriction__(r)
            else:
                raise TypeError("Expected type of Restriction() but got {0}".format(type(r)))

    def __add_restriction__(self, restriction: Restriction):
        self.restrictions.append(restriction)

    # TODO: Implement '<=' and '='
    def transform_to_standard_form(self):
        if self.is_standard_form:
            return

        self.next_var_index = len(self.objective_function)
        for r in self.restrictions:
            if r.equality_type == 0:  # <=
                slack_var = Variable(fo_coefficient=0, v_type='Slack')
                slack_var.internal_initial_index = self.next_var_index
                slack_var.internal_name = 's{0}'.format(self.next_var_index + 1)
                self.objective_function.append(slack_var)

                for _r in self.restrictions:
                    if r == _r:
                        _r.coefficients.append((1, slack_var))
                    else:
                        _r.coefficients.append((0, slack_var))

                self.next_var_index = self.next_var_index + 1

            elif r.equality_type == 1:  # >=
                excess_var = Variable(fo_coefficient=0, v_type='Excess')
                excess_var.internal_initial_index = self.next_var_index
                excess_var.internal_name = 's{0}'.format(self.next_var_index + 1)
                self.objective_function.append(excess_var)

                for _r in self.restrictions:
                    if r == _r:
                        _r.coefficients.append((-1, excess_var))
                    else:
                        _r.coefficients.append((0, excess_var))

                self.next_var_index = self.next_var_index + 1
            elif r.equality_type == 2:  # =
                pass
            else:
                raise ValueError("Invalid Equality Type")

        self.autobuild_matrices()
        self.is_standard_form = True

    def autobuild_matrices(self):
        # lines, columns
        self.m = len(self.restrictions)
        self.n = len(self.objective_function)

        self.A = np.zeros(shape=(self.m, self.n))
        self.b = np.zeros(shape=(self.m, 1))

        for index, r in enumerate(self.restrictions):
            rc = []
            for c in r.coefficients:
                rc.append(c[0])
            self.A[index] = rc

            self.b[index] = r.restriction_value

    def __repr__(self):
        return str(self)

    def __str__(self):
        m = '\nModel:\n'
        m = m + 'min Fo(x)= '
        for v in self.objective_function:
            m = m + str(v.fo_coefficient) + '*' + str(v) + ' '
        m = m + '\n\n'
        for r in self.restrictions:
            m = m + str(r) + '\n'
        return m


if __name__ == '__main__':
    # Declaring Variables
    x1 = Variable(fo_coefficient=-2)
    x2 = Variable(fo_coefficient=-1)
    r1 = Restriction([(1, x1), (1, x2)], '<=', 4)
    r2 = Restriction([(1, x1)], '<=', 3)
    r3 = Restriction([(1, x2)], '<=', 7/2)
    # x1 >= 0 and x2 >= 0 are automatically assumed, so no need to worry :D

    # Building a LP Model
    model = LinearModel()
    model.build_objective_function([x1, x2])
    model.add_restrictions([r1, r2, r3])
    model.transform_to_standard_form()

    print('Linear Model test passed')
