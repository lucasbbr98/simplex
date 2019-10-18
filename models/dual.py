from copy import deepcopy
from models.variable import Variable, VariableConstraint
from models.function import ObjectiveFunction, Constraint
from models.linear_model import LinearModel


class Dual:
    def __init__(self, primal: LinearModel):
        if not isinstance(primal, LinearModel):
            raise TypeError("Primal must be a LinearModel() object")
        if primal.is_standard:
            raise InterruptedError("Primal can't be on standard form to build it's dual")

        self.primal = deepcopy(primal)
        self.dual = None

        self.fo_min_or_max = ''
        if self.primal.fo.function_type == 'min':
            self.build_dual_from_min_primal()
        else:
            self.build_dual_from_max_primal()

    def build_dual_from_min_primal(self):
        # Building FO
        variables = []
        fo_coefficients = [i[0] for i in self.primal.b]
        fo_coefficients_variables = []
        for index, c in enumerate(primal.constraints):
            var = None
            if c.equality_operator == '<=':
                var = Variable(name='y{0}'.format(index + 1), initial_index=index, constraint=VariableConstraint.Negative)
            elif c.equality_operator == '>=':
                var = Variable(name='y{0}'.format(index + 1), initial_index=index)
            elif c.equality_operator == '=':
                var = Variable(name='y{0}'.format(index + 1), initial_index=index, constraint=VariableConstraint.Unrestricted)
            variables.append(var)
            fo_coefficients_variables.append((fo_coefficients[index], var))

        fo = ObjectiveFunction('max', fo_coefficients_variables)

        # Building Constraints
        constraints_inequalities = []
        for v in primal.fo.variables:
            if v.non_positive:
                constraints_inequalities.append('>=')
            elif v.free:
                constraints_inequalities.append('=')
            else:
                constraints_inequalities.append('<=')

        constraints = []
        At = primal.A.transpose()
        right_side = primal.fo.coefficients
        _i = 0
        for row in At:
            const_coefficients_variables = []
            for index, v in enumerate(variables):
                const_coefficients_variables.append((row[index], v))
            constraint = Constraint(name='R{0}'.format(_i + 1), coefficients_variables=const_coefficients_variables,
                                    equality_operator=constraints_inequalities[_i], right_side=right_side[_i])
            constraints.append(constraint)
            _i = _i + 1

        self.dual = LinearModel(objective_function=fo, constraints_list=constraints, name=primal.name + '- Dual')

    def build_dual_from_max_primal(self):
        # Building FO
        variables = []
        fo_coefficients = [i[0] for i in self.primal.b]
        fo_coefficients_variables = []
        for index, c in enumerate(primal.constraints):
            var = None
            if c.equality_operator == '<=':
                var = Variable(name='y{0}'.format(index + 1), initial_index=index)
            elif c.equality_operator == '>=':
                var = Variable(name='y{0}'.format(index + 1), initial_index=index, constraint=VariableConstraint.Negative)
            elif c.equality_operator == '=':
                var = Variable(name='y{0}'.format(index + 1), initial_index=index, constraint=VariableConstraint.Unrestricted)
            variables.append(var)
            fo_coefficients_variables.append((fo_coefficients[index], var))

        fo = ObjectiveFunction('min', fo_coefficients_variables)

        # Building Constraints
        constraints_inequalities = []
        for v in primal.fo.variables:
            if v.non_positive:
                constraints_inequalities.append('<=')
            elif v.free:
                constraints_inequalities.append('=')
            else:
                constraints_inequalities.append('>=')

        constraints = []
        At = primal.A.transpose()
        right_side = primal.fo.coefficients
        _i = 0
        for row in At:
            const_coefficients_variables = []
            for index, v in enumerate(variables):
                const_coefficients_variables.append((row[index], v))
            constraint = Constraint(name='R{0}'.format(_i + 1), coefficients_variables=const_coefficients_variables,
                                    equality_operator=constraints_inequalities[_i], right_side=right_side[_i])
            constraints.append(constraint)
            _i = _i + 1

        self.dual = LinearModel(objective_function=fo, constraints_list=constraints, name=primal.name + '- Dual')


if __name__ == '__main__':
    x1 = Variable(name='x1')
    x2 = Variable(name='x2', constraint=VariableConstraint.Unrestricted)
    x3 = Variable(name='x3', constraint=VariableConstraint.Negative)
    fo = ObjectiveFunction('max', [(1, x1), (2, x2), (0, x3)])
    c1 = Constraint([(-2, x1), (1, x2), (1, x3)], '>=', 3)
    c2 = Constraint([(3, x1), (4, x2)], '<=', 5)

    primal = LinearModel(objective_function=fo, constraints_list=[c1, c2])
    dual_transformation = Dual(primal=primal)
    dual = dual_transformation.dual
    print('Dual unit test passed')



