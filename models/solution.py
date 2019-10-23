from models.variable import Variable, FreeVariable
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

        if any([type(i) == FreeVariable for i in solver.model.fo.variables]):
            print('[WARNING]: We have found unrestricted variables. [Xi = Xip-Xin]. '
                  '\nXi values, are saved on .decision_variables. '
                  '\nXip and Xin, are saved on both .support_variables and .variables')

        already_solved_free_vars = []
        for index, v in enumerate(solver.model.fo.variables):
            value = 0
            if v.id in self.model.B_variables:
                position_index = self.model.B_variables.index(v.id)
                value = solver.xb[position_index][0]
                # Free Variables
                un_value = 0
                if type(v) == FreeVariable and v.id not in already_solved_free_vars:
                    if v.positive:
                        un_value = solver.xb[position_index][0]
                    else:
                        un_value = -1*solver.xb[position_index][0]
                    already_solved_free_vars.append(v.id)

                    for _v in solver.model.fo.variables:
                        if type(_v) == FreeVariable and _v.parent_index == v.parent_index and _v.id != v.id:
                            if _v in self.model.B_variables:
                                n_index = self.model.B_variables.index(_v.id)
                                if v.positive:
                                    un_value = un_value + solver.xb[n_index][0]
                                else:
                                    un_value = un_value - solver.xb[n_index][0]
                            already_solved_free_vars.append(_v.id)

                    decision_var = Variable(name='x{0}'.format(v.parent_index + 1), initial_index=v.parent_index)
                    self.decision_variables.append((un_value, decision_var))

            if type(v) == Variable:  # Decision Variables
                if v.non_positive:
                    print("[WARNING]: {0} is required to be non_positive, but solver only deals with positive values."
                          "\nThe solution value can be found in solution.decision_variables"
                          "\nThe solver value can be find in solution.variables".format(v.name))
                    self.decision_variables.append((-1*value, v))
                else:
                    self.decision_variables.append((value, v))
            else:
                self.support_variables.append((value, v))

            self.variables.append((value, v))

    def __str__(self):
        return str(self.variables)

    def __repr__(self):
        return str(self)





