from models_old.variable import Variable
from models_old.linear_model import LinearModel
from models_old.internal.simplex_solver import SimplexSolver
import numpy as np


class InitialBaseFinder:
    def __init__(self, linear_model: LinearModel):
        self.artificial_lm = LinearModel()
        self.artificial_variables = []
        self.artificial_lm.restrictions = linear_model.restrictions.copy()
        self.artificial_lm.next_var_index = linear_model.next_var_index

        # Internal Helper
        self.simplex_solver = None

        # Artificial Solution
        self.solution_N_vars = []
        self.solution_N_vars_indexes = []
        self.solution_B_vars = []
        self.solution_B_vars_indexes = []
        self.solution_FO_value = None
        self.solution_success = False

        for r in self.artificial_lm.restrictions:
            if r.equality_type == 0: #<=
                for c, v in r.coefficients:
                    if v.type == 'Slack' or v.type == 'Artificial':
                        v.fo_coefficient = 1
                    else:
                        v.fo_coefficient = 0
                    if v not in self.artificial_variables:
                        self.artificial_variables.append(v)

            elif r.equality_type == 1 or r.equality_type == 2:  # >= or =
                artificial_var = Variable(fo_coefficient=1, v_type='Artificial')
                artificial_var.internal_initial_index = self.artificial_lm.next_var_index
                artificial_var.internal_name = 'a{0}'.format(self.artificial_lm.next_var_index + 1)
                self.artificial_variables.append(artificial_var)

                for _r in self.artificial_lm.restrictions:
                    if r == _r:
                        _r.coefficients.append((1, artificial_var))
                    else:
                        _r.coefficients.append((0, artificial_var))

                self.artificial_lm.next_var_index = self.artificial_lm.next_var_index + 1
            else:
                raise IndexError("A fatal error ocurred. Equality type must be 0 '<=', 1 '>=' or 2 '=' ")

        self.artificial_lm.build_objective_function(fo_type='min', variables=self.artificial_variables, __do_not_rename__=True)
        self.artificial_lm.autobuild_matrices()
        start_base = [i.internal_initial_index for i in self.artificial_variables if i.fo_coefficient == 1]
        self.simplex_solver = SimplexSolver(linear_model=self.artificial_lm, start_base=start_base)

    def find_base(self, max_iterations=1000, __iteration__=1):
        if __iteration__ > max_iterations:
            raise TimeoutError("Max iterations were made: {0}".format(max_iterations))

        # Who should join the base?
        B_inv = np.linalg.inv(self.simplex_solver.B)
        simplex_multiplierT = np.dot(self.simplex_solver.CbT, B_inv)
        relative_costs = [v.fo_coefficient - np.dot(simplex_multiplierT, self.simplex_solver.N[:, index]) for index, v in
                          enumerate(self.simplex_solver.N_variables)]
        negative_relative_costs = [i for i in relative_costs if i < 0]
        variable_join_N_index = None
        if len(negative_relative_costs) > 0:
            variable_join_N_index = relative_costs.index(min(negative_relative_costs))

        # Is my base optimal?
        if variable_join_N_index is None:
            sol = []
            _xb = np.dot(B_inv, self.artificial_lm.b)
            for v in self.artificial_lm.objective_function:
                if v in self.simplex_solver.B_variables:
                    v_B_index = self.simplex_solver.B_variables.index(v)
                    sol.append((v, _xb[v_B_index][0]))
                elif v in self.simplex_solver.N_variables:
                    sol.append((v, 0))
            self.simplex_solver.solution = sol
            self.solution_B_vars = self.simplex_solver.B_variables
            self.solution_B_vars_indexes = [i.internal_initial_index for i in self.simplex_solver.B_variables]
            self.solution_N_vars = self.simplex_solver.N_variables
            self.solution_N_vars_indexes = [i.internal_initial_index for i in self.simplex_solver.N_variables]
            self.solution_FO_value = np.dot(self.simplex_solver.CbT, _xb)
            if self.solution_FO_value == 0:
                self.solution_success = True
            else:
                raise InterruptedError("InitialBaseFinder could not find a feasible initial solution set to your problem")
            can_be_multiple = False
            for k in relative_costs:
                if k == 0:
                    self.simplex_solver.status = 'Solution might have multiple other solutions, because a relative cost was 0'
                    can_be_multiple = True
                    break
            if not can_be_multiple:
                self.simplex_solver.status = 'Optimal'
            return

        # Who should I take out from base?
        simplex_direction = np.dot(B_inv, self.simplex_solver.N[:, [variable_join_N_index]])
        y = [i for i in simplex_direction]
        y_sanity_check = [i for i in simplex_direction if i > 0]
        if not y_sanity_check or len(y_sanity_check) <= 0:
            raise InterruptedError("The model has unlimited solutions")

        xb = np.dot(B_inv, self.artificial_lm.b)
        steps = [item/y[index] if y[index] != 0 else -1 for index, item in enumerate(xb)]
        steps_excluding_negative = [i for i in steps if i >= 0]
        variable_leave_B_index = np.where(steps == min(steps_excluding_negative))[0][0]

        variable_leave_B = self.simplex_solver.B_variables[variable_leave_B_index]
        variable_join_N = self.simplex_solver.N_variables[variable_join_N_index]

        # Setting up new base (tmp to avoid Python allocation by memory)
        self.simplex_solver.B_variables[variable_leave_B_index] = variable_join_N
        self.simplex_solver.N_variables[variable_join_N_index] = variable_leave_B

        self.simplex_solver.build_base()
        self.find_base(__iteration__=__iteration__ + 1)