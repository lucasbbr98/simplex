from models.linear_model import LinearModel
from models.phase1 import Phase1, InfeasibleError
from models.phase2 import Phase2
from models.sensitivity_analysis import SensitivityAnalysis
from models.solution import Solution
from models.branch_bound import Branch
from models.function import Constraint
from math import floor, ceil
from copy import deepcopy


class LinearSolver:
    def __init__(self, linear_model: LinearModel):
        if not isinstance(linear_model, LinearModel):
            raise TypeError("linear_model must be a LinearModel() object.")

        self.model = linear_model
        self.method = 'Two Phase'
        if any([v.integer for v in linear_model.fo.variables]):
            self.method = 'Branch and Bound'

        if self.method == 'Two Phase':
            self.two_phase()
        elif self.method == 'Branch and Bound':
            self.branch_and_bound()

    def branch_and_bound(self):
        relaxed_solution = self.solve_two_phase(self.model)
        relaxed_branch = Branch(relaxed_solution)
        if relaxed_branch.has_only_integers:
            self.solution = relaxed_solution
            print('[WARNING]: Branch and Bound was not applied. Check your model and solution')

        possible_solutions = []
        global_fo = relaxed_solution.fo_value
        base_constraints = self.model.constraints
        iteration = 0
        for v in relaxed_branch.needs_branching:
            coefficients_variables = [(0, _v[1]) if _v[1] != v[1] else (1, _v[1]) for _v in relaxed_solution.decision_variables]
            lower_bound = floor(v[0])
            upper_bound = ceil(v[0])
            c_down = Constraint(coefficients_variables, '<=', lower_bound)
            c_up = Constraint(coefficients_variables, '>=', upper_bound)
            const_down = deepcopy(base_constraints)
            const_up = deepcopy(base_constraints)
            const_down.append(c_down)
            const_up.append(c_up)
            l_down = LinearModel(objective_function=self.model.fo, constraints_list=const_down, name='Branch {0}'.format(iteration))
            iteration = iteration + 1
            l_up = LinearModel(objective_function=self.model.fo, constraints_list=const_up, name='Branch {0}'.format(iteration))
            iteration = iteration + 1
            s_down = self.solve_two_phase(l_down)
            s_up = self.solve_two_phase(l_up)
            b_down = Branch(solution=s_down)
            b_up = Branch(solution=s_up)


            print(v)



    @staticmethod
    def solve_two_phase(model):
        try:
            p1 = Phase1(linear_model=model)
            p1.find_base()
            p2 = Phase2(linear_model=model, base_indexes=p1.base_variables)
            p2.solve()
            return p2.solution
        except InfeasibleError:
            return None


    def two_phase(self):
        try:
            self.p1 = Phase1(linear_model=self.model)
            self.initial_base = self.p1.find_base()
            self.p2 = Phase2(linear_model=self.model, base_indexes=self.p1.base_variables)
            self.p2.solve()
            self.solution = self.p2.solution
            self.analysis = SensitivityAnalysis(solution=self.p2.solution)
        except InfeasibleError:
            raise InterruptedError("Infeasible model")