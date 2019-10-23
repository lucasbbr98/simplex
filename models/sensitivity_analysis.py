import numpy as np
from numbers import Number
from models.solution import Solution
from models.function import Constraint


class SensitivityAnalysis:
    def __init__(self, solution: Solution):
        self.solution = solution
        self.n_variables_max_fo_perturbations = []
        self.n_variables_max_fo_coefficients = []
        self.max_fo_change_N_variables()
        self.b_variables_min_max_fo_perturbations = []
        self.b_variables_min_max_fo_coefficients = []
        self.min_max_change_B_variables()

    def max_fo_change_N_variables(self):
        solver = self.solution.model
        B_inv_A = np.dot(solver.B_inv, solver.N)
        for index, i in enumerate(self.solution.model.N_variables):
            max_cost = np.dot(solver.CbT, B_inv_A[:, index])
            current_cost = solver.model.fo.coefficients[i]
            perturbation = max_cost-current_cost
            self.n_variables_max_fo_perturbations.append((perturbation, solver.model.fo.variables[i]))
            current_coefficient = solver.model.fo.coefficients[i]
            self.n_variables_max_fo_coefficients.append((current_coefficient + perturbation, solver.model.fo.variables[i]))

    def min_max_change_B_variables(self):
        solver = self.solution.model
        B_inv_A = np.dot(solver.B_inv, solver.N)
        zero_perturbations = solver.CnT - np.dot(solver.CbT, B_inv_A)
        steps_min = []
        steps_max = []
        for index, v in enumerate(solver.B_variables):
            new_cbt = solver.CbT
            new_cbt[index] = new_cbt[index] - 1
            plus_one_perturbations = solver.CnT - np.dot(new_cbt, B_inv_A)
            delta_perturbations_change = zero_perturbations - plus_one_perturbations
            for i in delta_perturbations_change: # Avoids division by zero
                if i == 0:
                    i = i + 0.000000001
            actual_perturbations_change = [i/(delta_perturbations_change[index]) for index, i in enumerate(zero_perturbations)]
            negative_perturbations = [i for i in actual_perturbations_change if i < 0]
            if not negative_perturbations or len(negative_perturbations) <= 0:
                negative_perturbations = [0]
            left_bound = max(negative_perturbations)
            positive_perturbations = [i for i in actual_perturbations_change if i > 0]
            if not positive_perturbations or len(positive_perturbations) <= 0:
                positive_perturbations = [0]

            right_bound = min(positive_perturbations)
            self.b_variables_min_max_fo_perturbations.append((left_bound, solver.model.fo.variables[v], right_bound))
            v_coefficient = solver.model.fo.coefficients[v]
            min_coefficient = v_coefficient - left_bound
            max_coefficient = v_coefficient - right_bound
            self.b_variables_min_max_fo_coefficients.append((min_coefficient, solver.model.fo.variables[v], max_coefficient))

    def new_variable_column_change_fo(self, variable_id: int, new_column: np.ndarray) -> bool:
        if not isinstance(variable_id, int):
            raise ValueError('Variable id must be an integer')
        new_column = self.__cast_to_np_array__(new_column)

        solver = self.solution.model
        if variable_id not in solver.N_variables and variable_id not in solver.B_variables:
            raise ValueError('Index {0} was not found on non basic solution list'.format(variable_id))

        v_fo_value = solver.model.fo.coefficients[variable_id]
        simplex_lambda = np.dot(solver.CbT, solver.B_inv)
        current_value = np.dot(simplex_lambda, new_column)
        test = v_fo_value - current_value
        if test > 0:
            return False    # Still optimal
        else:
            return True     # Not optimal

    def add_new_variable_change_fo(self, fo_cost: Number, column_costs: np.ndarray) -> bool:
        if not isinstance(fo_cost, Number):
            raise ValueError('Fo cost must be a number')

        solver = self.solution.model
        column_costs = self.__cast_to_np_array__(column_costs)

        simplex_lambda = np.dot(solver.CbT, solver.B_inv)
        current_value = np.dot(simplex_lambda, column_costs)
        test = fo_cost - current_value
        if test > 0:
             return False   # Still optimal
        else:
            return True     # Not optimal
    # TODO
    def add_new_constraint_change_fo(self, constraint:Constraint) -> bool:
        pass




    @staticmethod
    def __cast_to_np_array__(arr) -> np.ndarray:
        if not isinstance(arr, np.ndarray):
            print('[WARNING]: New column should be a np.ndarray, trying to cast')
            new_arr = np.atleast_2d(arr)

        l, c = new_arr.shape
        if c > 1 and l == 1:
            new_arr = np.transpose(arr)
        elif l > 1 and c > 1:
            raise ValueError('You can only send one column at a time')

        return new_arr