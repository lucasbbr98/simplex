from models.function import ObjectiveFunction, Constraint
from models.variable import Variable, SlackVariable, ExcessVariable


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
        self.next_index = len(self.fo.variables)

        for index, v in enumerate(self.fo.variables):
            v.internal_initial_index = index

        for v in self.fo.variables:
            for c in self.constraints:
                if v not in c.variables:
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
        for index, c in enumerate(self.constraints):
            c.name = 'R{0}'.format(index + 1)
            if c.equality_operator == '<=':
                s_var = SlackVariable(name='s{0}'.format(self.next_index + 1), initial_index=self.next_index)
                self.fo.variables.append(s_var)
                self.fo.coefficients.append(0)
                self.next_index = self.next_index + 1
                for _c in self.constraints:
                    _c.variables.append(s_var)
                    if _c == c:
                        _c.coefficients.append(1)
                    else:
                        _c.coefficients.append(0)

            elif c.equality_operator == '>=':
                e_var = ExcessVariable(name='e{0}'.format(self.next_index + 1), initial_index=self.next_index)
                self.fo.variables.append(e_var)
                self.fo.coefficients.append(0)
                self.next_index = self.next_index + 1
                for _c in self.constraints:
                    _c.variables.append(e_var)
                    if _c == c:
                        _c.coefficients.append(-1)
                    else:
                        _c.coefficients.append(0)

            elif c.equality_operator == '=':
                pass
            else:
                raise ValueError("Equality operator must be either: '<=' or '=' or '>='")

        self.is_standard = True

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
    x2 = Variable(name='x2')
    fo = ObjectiveFunction('min', [(80, x1), (60, x2)])
    c1 = Constraint([(1, x1), (1, x2)], '>=', 1)
    c2 = Constraint([(-0.05, x1), (0.07, x2)], '<=', 0)
    model = LinearModel(objective_function=fo, constraints_list=[c1, c2])
    model.standard_form()
    print('Linear Model unit test passed')
