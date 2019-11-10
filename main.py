from models.variable import Variable, VariableConstraint
from models.function import ObjectiveFunction, Constraint
from models.linear_model import LinearModel
from models.solver import LinearSolver


# Problem setup
x1 = Variable(name='x1', integer=True)
x2 = Variable(name='x2', integer=True)

fo = ObjectiveFunction('max', [(3, x1), (5, x2)])
c1 = Constraint([(2, x1), (4, x2)], '<=', 25)
c2 = Constraint([(1, x1)], '<=', 8)
c3 = Constraint([(2, x2)], '<=', 10)

model = LinearModel(objective_function=fo, constraints_list=[c1, c2, c3])
solver = LinearSolver(linear_model=model)
print(solver.best_solution)

"""
# Problem setup
x1 = Variable(name='x1', integer=True)
x2 = Variable(name='x2', integer=True)

fo = ObjectiveFunction('max', [(3, x1), (7, x2)])
c1 = Constraint([(1, x1)], '<=', 3.5)
c2 = Constraint([(5, x1), (-4, x2)], '<=', 10)
c3 = Constraint([(4/7, x1), (2, x2)], '<=', 9)

model = LinearModel(objective_function=fo, constraints_list=[c1, c2, c3])
solver = LinearSolver(linear_model=model)
print(solver.best_solution)
"""





