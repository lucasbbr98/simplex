from models.linear_model import LinearModel
import numpy as np


class Simplex:
    def __init__(self, linear_model: LinearModel, start_base=None):
        self.lm = linear_model
        self.fix_variables = self.lm.n - self.lm.m
        self.B_variables = []
        self.B = np.zeros(shape=(self.lm.m, self.lm.m))
        self.B_history = {}
        self.N_variables = []
        self.N = np.zeros(shape=(self.lm.m, self.fix_variables))
        self.N_history = {}
        self.CbT = []
        self.CnT = []

        # Matrix partition
        self.build_base(start_base=start_base)

        # Final solution
        self.solution = []
        self.status = ''
        self.can_have_multiple_solutions = False
        self.infeasible = False

    def build_base(self, start_base=None):
        # Setups initial base
        if not start_base and not self.B_variables:
            self.B_variables = self.lm.objective_function[0:self.lm.m]
            self.B_history[0] = self.B_variables
        elif start_base and not self.B_variables:
            start_base = list(set(start_base))
            if not isinstance(start_base, list) or len(start_base) != self.lm.m:
                raise ValueError("Start base argument must be a list with a length of {0}".format(self.lm.m))
            max_index = self.lm.n - 1
            if any(not isinstance(item, int) or item < 0 or item > max_index for item in start_base):
                raise ValueError("Start base argument must be a list of positive integers indexes of the variables")

            self.B_variables = [item for item in self.lm.objective_function if item.internal_initial_index in start_base]

        self.N_variables = [item for item in self.lm.objective_function if item not in self.B_variables]
        self.N_history[0] = self.N_variables
        self.B = self.lm.A[:, [i.internal_initial_index for i in self.B_variables]]
        self.N = self.lm.A[:, [i.internal_initial_index for i in self.N_variables]]
        self.CbT = [item.fo_coefficient for item in self.B_variables]
        self.CnT = [item.fo_coefficient for item in self.N_variables]

    # Actual simplex algorithm
    def solve(self, max_iterations=1000, __iteration__=1):

        if __iteration__ > max_iterations:
            raise TimeoutError("Max iterations were made: {0}".format(max_iterations))

        # Who should join the base?
        B_inv = np.linalg.inv(self.B)
        simplex_multiplierT = np.dot(self.CbT, B_inv)
        relative_costs = [v.fo_coefficient - np.dot(simplex_multiplierT, self.N[:, index]) for index, v in
                          enumerate(self.N_variables)]
        negative_relative_costs = [i for i in relative_costs if i < 0]
        variable_join_N_index = None
        if len(negative_relative_costs) > 0:
            variable_join_N_index = relative_costs.index(min(negative_relative_costs))

        # Is my base optimal?
        if variable_join_N_index is None:
            sol = []
            _xb = np.dot(B_inv, self.lm.b)
            for v in self.lm.objective_function:
                if v in self.B_variables:
                    v_B_index = self.B_variables.index(v)
                    sol.append((v, _xb[v_B_index][0]))
                elif v in self.N_variables:
                    sol.append((v, 0))
            self.solution = sol

            can_be_multiple = False
            for k in relative_costs:
                if k == 0:
                    self.status = 'Solution might have multiple other solutions, because a relative cost was 0'
                    can_be_multiple = True
                    break

            if not can_be_multiple:
                self.status = 'Optimal'
            return

        # Who should I take out from base?
        simplex_direction = np.dot(B_inv, self.N[:, [variable_join_N_index]])
        y = [i for i in simplex_direction]
        y_sanity_check = [i for i in simplex_direction if i > 0]
        if not y_sanity_check or len(y_sanity_check) <= 0:
            raise InterruptedError("The model has unlimited solutions")

        xb = np.dot(B_inv, self.lm.b)
        steps = [item/y[index] if y[index] != 0 else -1 for index, item in enumerate(xb)]
        steps_excluding_negative = [i for i in steps if i > 0]
        variable_leave_B_index = np.where(steps == min(steps_excluding_negative))[0][0]

        variable_leave_B = self.B_variables[variable_leave_B_index]
        variable_join_N = self.N_variables[variable_join_N_index]

        # Setting up new base (tmp to avoid Python allocation by memory)
        self.B_variables[variable_leave_B_index] = variable_join_N
        self.N_variables[variable_join_N_index] = variable_leave_B

        self.build_base()
        self.solve(__iteration__=__iteration__ + 1)






