from models.linear_model import LinearModel
from models.phase1 import Phase1, InfeasibleError
from models.phase2 import Phase2
from models.sensitivity_analysis import SensitivityAnalysis
from models.branch_bound import Branch, BranchTree
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
            self.branch_tree = None
            self.best_solution = None
            self.branch_and_bound()


    def branch_and_bound(self):
        relaxed_solution = self.solve_two_phase(self.model)
        relaxed_branch = Branch(relaxed_solution)
        if relaxed_branch.has_only_integers or not relaxed_branch.needs_branching or len(relaxed_branch.needs_branching) <= 0:
            self.solution = relaxed_solution
            self.best_solution = relaxed_solution
            print('[WARNING]: Branch and Bound relaxed solution only contained integers.')
            return

        # Global variables
        possible_solutions = []
        global_fo = 0
        best_solution = None
        base_constraints = self.model.constraints
        iteration = 0
        has_finished = False

        # Branch and Bound
        v = relaxed_branch.variable_to_branch
        needs_further_branching = []
        loop_constraints = base_constraints
        parent_branch = relaxed_branch
        __i__ = 1
        while not has_finished:
            coefficients_variables = [(0, _v[1]) if _v[1].id != parent_branch.variable_to_branch[1].id else (1, _v[1]) for _v in parent_branch.solution.decision_variables]
            lower_bound = floor(v[0])
            upper_bound = ceil(v[0])
            c_down = Constraint(coefficients_variables, '<=', lower_bound)
            c_up = Constraint(coefficients_variables, '>=', upper_bound)
            const_down = deepcopy(loop_constraints)
            const_up = deepcopy(loop_constraints)
            const_down.append(c_down)
            const_up.append(c_up)
            l_down = LinearModel(objective_function=self.model.fo, constraints_list=const_down, name='Branch {0}'.format(iteration))
            iteration = iteration + 1
            l_up = LinearModel(objective_function=self.model.fo, constraints_list=const_up, name='Branch {0}'.format(iteration))
            iteration = iteration + 1
            s_up = self.solve_two_phase(l_up)
            s_down = self.solve_two_phase(l_down)
            b_down = Branch(solution=s_down)
            b_down.constraints = const_down
            parent_branch.children.append(b_down)
            b_up = Branch(solution=s_up)
            b_up.constraints = const_up
            parent_branch.children.append(b_up)
            if b_down.feasible:
                if b_down.feasible and b_down.has_only_integers:
                    possible_solutions.append(b_down)
                    if b_down.fo_value > global_fo:
                        global_fo = b_down.fo_value
                        best_solution = b_down
                else:
                    needs_further_branching.append(b_down)
            if b_up.feasible:
                if b_up.has_only_integers:
                    possible_solutions.append(b_up)
                    if b_up.fo_value > global_fo:
                        global_fo = b_up.fo_value
                        best_solution = b_up
                else:
                    needs_further_branching.append(b_up)

            if needs_further_branching and len(needs_further_branching) > 0:
                needs_further_branching = sorted(needs_further_branching, key=lambda _b: _b.fo_value, reverse=True)
                possible_next_branch = needs_further_branching[0]
                if possible_next_branch.fo_value > global_fo:
                    v = possible_next_branch.variable_to_branch
                    loop_constraints = possible_next_branch.constraints
                    needs_further_branching.pop(0)
                    parent_branch = possible_next_branch
                    __i__ += 1
                else:
                    has_finished = True
                    self.branch_tree = BranchTree(root_branch=relaxed_branch)
                    self.best_solution = best_solution
                    self.all_solutions = possible_solutions
            else:
                has_finished = True
                self.branch_tree = BranchTree(root_branch=relaxed_branch)
                self.best_solution = best_solution
                self.all_solutions = possible_solutions


    @staticmethod
    def solve_two_phase(model):
        try:
            p1 = Phase1(linear_model=model)
            p1.find_base()
            p2 = Phase2(phase_one=p1)
            p2.solve()
            return p2.solution
        except InfeasibleError:
            return None

    def two_phase(self):
        try:
            self.p1 = Phase1(linear_model=self.model)
            self.initial_base = self.p1.find_base()
            self.p2 = Phase2(phase_one=self.p1)
            self.p2.solve()
            self.solution = self.p2.solution
            self.analysis = SensitivityAnalysis(solution=self.p2.solution)
        except InfeasibleError:
            raise InterruptedError("Infeasible model")