from models.variable import Variable
from models.simplex_solver import SimplexSolver


class Solution:
    def __init__(self, solver: SimplexSolver):
        self.model = solver
        self.A = solver.model.A
        self.b = solver.model.b
        self.fo_value = solver.fo_value

        self.decision_variables = []
        self.support_variables = []
        self.variables = []

        for index, v in enumerate(solver.model.fo.variables):
            value = 0
            if v.id in self.model.B_variables:
                position_index = self.model.B_variables.index(v.id)
                value = solver.xb[position_index][0]

            if type(v) == Variable:  # Decision Variables
                self.decision_variables.append((value, v))
            else:
                self.support_variables.append((value, v))

            self.variables.append((value, v))

    def __str__(self):
        return str(self.variables)

    def __repr__(self):
        return str(self)





