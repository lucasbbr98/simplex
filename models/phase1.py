import numpy as np
from copy import deepcopy
from models.linear_model import LinearModel
from models.simplex_solver import SimplexSolver
from models.function import ObjectiveFunction, Constraint
from models.variable import SlackVariable, ArtificialVariable, Variable


class InfeasibleError(Exception):
    pass


class Phase1:
    def __init__(self, linear_model: LinearModel, max_iterations=1000):
        # Integrity check
        if not isinstance(linear_model, LinearModel):
            raise TypeError("Phase1 can only be applied on LinearModel() objects")

        # Guarantees standard_form
        self.model = deepcopy(linear_model)
        if not self.model.is_standard:
            self.model.standard_form()

        # Initialize variables
        self.initial_base = None
        self.current_iteration = 0
        self.max_iterations = max_iterations
        self.base_variables = []
        self.non_base_variables = []

        # Updating Constraints
        for c in self.model.constraints:
            if c.equality_operator == '>=' or c.equality_operator == '=':
                artificial_var = ArtificialVariable(name='a{0}'.format(self.model.next_index + 1), initial_index=self.model.next_index)
                self.model.fo.variables.append(artificial_var)
                self.model.fo.coefficients.append(1)
                for _c in self.model.constraints:
                    if _c == c:
                        _c.coefficients.append(1)
                        _c.variables.append(artificial_var)
                    else:
                        _c.coefficients.append(0)
                        _c.variables.append(artificial_var)

        # Updating FO
        for index, v in enumerate(self.model.fo.variables):
            if isinstance(v, ArtificialVariable):
                self.model.fo.coefficients[index] = 1
                self.base_variables.append(v.id)
            elif isinstance(v, SlackVariable):
                self.model.fo.coefficients[index] = 0
                self.base_variables.append(v.id)
            else:
                self.model.fo.coefficients[index] = 0
                self.non_base_variables.append(v.id)

    def find_base(self):
        self.__solve_lp__()
        return self.base_variables

    def __solve_lp__(self, __solver__=None):
        if self.current_iteration >= self.max_iterations:
            raise TimeoutError("Phase1 has reached the maximum number of {0} iterations".format(self.max_iterations))

        # Trick to speed things up and avoid calculating A, and b over and over again
        if __solver__ is None:
            solver = SimplexSolver(linear_model=self.model, base_variables=self.base_variables,non_base_variables=self.non_base_variables)
        else:
            solver = __solver__

        # Who should join the base?
        relative_costs = [self.model.fo.coefficients[i] - np.dot(solver.simplex_multiplierT, solver.N[:, index]) for index, i in enumerate(solver.N_variables)]
        negative_relative_costs = [i for i in relative_costs if i < 0]
        variable_join_N_index = None
        if len(negative_relative_costs) > 0:
            variable_join_N_index = relative_costs.index(min(negative_relative_costs))

        # Is my base optimal?
        if variable_join_N_index is None:
            if solver.fo_value != 0:
                raise InfeasibleError("Infeasible problem")

            return

        # Who should I take out from base?
        simplex_direction = np.dot(solver.B_inv, solver.N[:, [variable_join_N_index]])
        y = [i for i in simplex_direction]

        # Unlimited solutions check
        y_sanity_check = [i for i in simplex_direction if i > 0]
        if not y_sanity_check or len(y_sanity_check) <= 0:
            raise InterruptedError("The model has unlimited solutions")

        steps = [item / y[index] if y[index] != 0 else -1 for index, item in enumerate(solver.xb)]
        steps_excluding_negative = [i for i in steps if i >= 0]
        if len(steps_excluding_negative) <= 0:
            raise InterruptedError("Only negative steps...")
        min_step = min(steps_excluding_negative)
        variable_leave_B_index = steps.index(min_step)

        # Updating Base and Non Base
        variable_leave_B = solver.B_variables[variable_leave_B_index]
        variable_join_N = solver.N_variables[variable_join_N_index]

        solver.B_variables[variable_leave_B_index] = variable_join_N
        solver.N_variables[variable_join_N_index] = variable_leave_B
        self.current_iteration = self.current_iteration + 1

        self.__solve_lp__(__solver__=solver)








if __name__ == '__main__':
    x1 = Variable(name='x1')
    x2 = Variable(name='x2')
    x3 = Variable(name='x3')
    fo = ObjectiveFunction('min', [(1, x1), (-1, x2), (2, x3)])
    c1 = Constraint([(1, x1), (1, x2), (1, x3)], '=', 3)
    c2 = Constraint([(2, x1), (-1, x2), (3, x3)], '<=', 4)
    model = LinearModel(objective_function=fo, constraints_list=[c1, c2])
    p1 = Phase1(linear_model=model)
    initial_base = p1.find_base()
    print('Phase1 unit test passed')






