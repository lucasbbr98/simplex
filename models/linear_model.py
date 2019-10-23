import numpy as np
from models.function import ObjectiveFunction, Constraint
from models.variable import Variable, SlackVariable, ExcessVariable, FreeVariable


class LinearModel:
    def __init__(self, objective_function: ObjectiveFunction, constraints_list: list, name='Example Model'):

        self.name = name
        if not isinstance(objective_function, ObjectiveFunction):
            raise TypeError("The objective function must be of type ObjectiveFunction()")
        self.fo = objective_function

        if not all([isinstance(c, Constraint) for c in constraints_list]):
            raise TypeError("The constraint list must only contain items of type Constraint()")

        self.constraints = constraints_list
        self.is_standard = False

        for index, v in enumerate(self.fo.variables):
            v.internal_initial_index = index
        for v in self.fo.variables:
            for c in self.constraints:
                internal_names = [n.internal_name for n in c.variables]
                if v not in c.variables and v.internal_name not in internal_names:
                    c.variables.insert(v.id, v)
                    c.coefficients.insert(v.id, 0)

    def standard_form(self):
        if self.is_standard:
            return

        # FO: Max -> Min
        if self.fo.function_type == 'max':
            print("[WARNING]: Transforming 'max' objective function to 'min'")
            for index, c in enumerate(self.fo.coefficients):
                self.fo.coefficients[index] = -1 * c
            self.fo.function_type = 'min'

        # Constraints -> Standard form
        index_has_changed = False
        for index, c in enumerate(self.constraints):
            c.name = 'R{0}'.format(index + 1)

            # Asserting positive right hand side
            if c.right_side < 0:
                print('[WARNING]: Changing constraint {0} due to negative right side'.format(c.name))
                c.right_side = -1 * c.right_side

                for i, _c in enumerate(c.coefficients):
                    c.coefficients[i] = -1*_c

                if c.equality_operator == '<=':
                    c.equality_operator = '>='
                elif c.equality_operator == '>=':
                    c.equality_operator = '<='
                else:
                    pass

            # Slack variables
            if c.equality_operator == '<=':
                s_var = SlackVariable(name='s{0}'.format(self.next_index + 1), initial_index=self.next_index)
                self.fo.variables.append(s_var)
                self.fo.coefficients.append(0)
                for _c in self.constraints:
                    _c.variables.append(s_var)
                    if _c == c:
                        _c.coefficients.append(1)
                    else:
                        _c.coefficients.append(0)

            # Excess variables
            elif c.equality_operator == '>=':
                e_var = ExcessVariable(name='e{0}'.format(self.next_index + 1), initial_index=self.next_index)
                self.fo.variables.append(e_var)
                self.fo.coefficients.append(0)
                for _c in self.constraints:
                    _c.variables.append(e_var)
                    if _c == c:
                        _c.coefficients.append(-1)
                    else:
                        _c.coefficients.append(0)

            # Ignoring '='
            elif c.equality_operator == '=':
                pass
            else:
                raise ValueError("Equality operator must be either: '<=' or '=' or '>='")

            # Finding if there are any non positive or free variables
            for i, v in enumerate(c.variables):
                if v.non_positive:
                    c.coefficients[i] = -1 * c.coefficients[i]

                elif v.free:
                    fv_p = FreeVariable(positive=True, parent_index=v.id, name=v.name + 'p', initial_index=v.id)
                    fv_n = FreeVariable(positive=False, parent_index=v.id, name=v.name + 'n', initial_index=v.id + 1)
                    self.fo.variables[v.id] = fv_p
                    self.fo.variables.insert(v.id + 1, fv_n)
                    self.fo.coefficients.insert(v.id + 1, -1*self.fo.coefficients[v.id])
                    for _id, _v in enumerate(self.fo.variables):
                        v.internal_initial_index = _id

                    for tmp_c in self.constraints:
                        tmp_c.variables[i] = fv_p
                        tmp_c.variables.insert(i+1, fv_n)
                        tmp_c.coefficients.insert(i+1, -1*tmp_c.coefficients[i])

                    # Updating internal indexes
                    for __i, __v in enumerate(self.fo.variables):
                        __v.internal_initial_index = __i

                    for __c in self.constraints:
                        for __v in __c.variables:
                            __v.internal_initial_index = self.fo.variables.index(__v)


        self.is_standard = True

    @property
    def next_index(self):
        return len(self.fo.variables)

    @property
    def m(self):
        return len(self.constraints)

    @property
    def n(self):
        return len(self.fo.variables)

    @property
    def fix_variables(self):
        return self.n - self.m

    @property
    def A(self):
        _A = np.zeros(shape=(self.m, self.n))
        for index, c in enumerate(self.constraints):
            _A[index] = c.coefficients

        return _A

    @property
    def b(self):
        _b = np.zeros(shape=(self.m, 1))
        for index, c in enumerate(self.constraints):
            _b[index] = c.right_side
        return _b

    def __repr__(self):
        m = '\nModel {0}:\n'.format(self.name)
        m = m + 'min Fo(x)= '
        for index, v in enumerate(self.fo.variables):
            m = m + str(self.fo.coefficients[index]) + '*' + str(v) + ' '
        m = m + '\n\n'
        for r in self.constraints:
            m = m + str(r) + '\n'
        return m


if __name__ == '__main__':
    x1 = Variable(name='x1')
    x2 = Variable(name='x2', negative=True)
    x3 = Variable(name='x3', free=True)
    x4 = Variable(name='x4', free=True)
    fo = ObjectiveFunction('max', [(3, x1), (2, x2), (-1, x3), (1, x4)])
    c1 = Constraint([(1, x1), (2, x2), (1, x3), (-1, x4)], '<=', 5)
    c2 = Constraint([(-2, x1), (-4, x2), (1, x3), (1, x4)], '<=', -1)
    model = LinearModel(objective_function=fo, constraints_list=[c1, c2])
    model.standard_form()
    print('Linear Model unit test passed')
