from models.solution import Solution
from math import isclose


class Branch:
    def __init__(self, solution: Solution, children=None, iteration=0):
        if solution is not None and not isinstance(solution, Solution):
            raise TypeError("solution argument must be a Solution() object")
        if not children:
            children = []
        self.iteration = iteration
        self.solution = solution
        self.children = children
        self.branch_var = None
        self.feasible = True
        if solution is None:
            self.feasible = False

        self.fo_value = None
        if solution:
            self.fo_value = solution.fo_value
        self.needs_branching = []
        self.check_branching()

    @property
    def has_only_integers(self):
        return len(self.needs_branching) <= 0

    def check_branching(self):
        if not self.feasible:
            return

        for v in self.solution.decision_variables:
            if v[1].integer:
                if not isclose(v[0], int(v[0])):
                    self.needs_branching.append(v)


