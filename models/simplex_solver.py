import numpy as np
from models.linear_model import LinearModel


class SimplexSolver:
    def __init__(self, linear_model: LinearModel, base_variables: list, non_base_variables: list):
        if not isinstance(linear_model, LinearModel):
            raise TypeError("SimplexSolver() needs  to be initialized with a LinearModel() object")

        # Initial population
        self.model = linear_model


        # Getting constructor input
        self.B_variables = base_variables
        self.N_variables = non_base_variables

    @property
    def B(self):
        return self.model.A[:, [i for i in self.B_variables]]

    @property
    def B_inv(self):
        return np.linalg.inv(self.B)

    @property
    def N(self):
        return self.model.A[:, [i for i in self.N_variables]]

    @property
    def xb(self):
        return np.dot(self.B_inv, self.model.b)


    @property
    def simplex_multiplierT(self):
        return np.dot(self.CbT, self.B_inv)

    @property
    def CbT(self):
        return [self.model.fo.coefficients[i] for i in self.B_variables]

    @property
    def CnT(self):
        return [self.model.fo.coefficients[i] for i in self.N_variables]

    @property
    def fo_value(self):
        return np.dot(self.CbT, self.xb)


if __name__ == '__main__':
    from models.variable import Variable
    from models.function import ObjectiveFunction, Constraint
    from models.phase1 import Phase1
    x1 = Variable(name='x1')
    x2 = Variable(name='x2')
    fo = ObjectiveFunction('min', [(80, x1), (60, x2)])
    c1 = Constraint([(1, x1), (1, x2)], '>=', 1)
    c2 = Constraint([(-0.05, x1), (0.07, x2)], '<=', 0)
    model = LinearModel(objective_function=fo, constraints_list=[c1, c2])
    p1 = Phase1(linear_model=model)
    solver = SimplexSolver(linear_model=p1.model, base_variables=[3, 4], non_base_variables=[0, 1, 2])
    print('Simplex Solver test passed')