from models.solution import Solution
from math import isclose, modf


class Branch:
    def __init__(self, solution: Solution, children=None, iteration=0):
        if solution is not None and not isinstance(solution, Solution):
            raise TypeError("solution argument must be a Solution() object")
        if children is None:
            children = []
        self.iteration = iteration
        self.solution = solution
        self.children = children
        self.feasible = True
        if solution is None:
            self.feasible = False

        self.fo_value = None
        if solution:
            self.fo_value = solution.fo_value * -1
        self.needs_branching = []
        self.variable_to_branch = None
        self.check_branching()
        self.constraints = None

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

        if len(self.needs_branching) > 0:
            self.needs_branching = sorted(self.needs_branching,
                                          key=lambda _v: modf(_v[0])[0], reverse=True)
            self.variable_to_branch = self.needs_branching[0]

    def __repr__(self):
        return str(self.solution) + ' FO: {0}'.format(self.fo_value)


class BranchTree:
    def __init__(self, root_branch: Branch):
        if not isinstance(root_branch, Branch):
            raise TypeError("root_branch must be a Branch() object")

        self.root_branch = root_branch

