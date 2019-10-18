from models.variable import Variable, VariableConstraint
from models.function import ObjectiveFunction, Constraint
from models.linear_model import LinearModel
from models.phase1 import Phase1
from models.phase2 import Phase2
from models.dual import DualTransformation

''''
x1 = Variable(name='x1')
x2 = Variable(name='x2')
x3 = Variable(name='x3')
fo = ObjectiveFunction('max', [(4, x1), (10, x2), (6, x3)])

c1 = Constraint([(0.03, x1), (0.15, x2), (0.10, x3)], '<=', 400)
c2 = Constraint([(0.06, x1), (0.12, x2), (0.10, x3)], '<=', 400)
c3 = Constraint([(0.05, x1), (0.10, x2), (0.12, x3)], '<=', 500)
c4 = Constraint([(2, x2), (1.2, x3)], '<=', 2000)
c5 = Constraint([(1, x1)], '<=', 6000)
c6 = Constraint([(1, x2)], '<=', 500)
c7 = Constraint([(1, x3)], '<=', 1000)
c8 = Constraint([(1, x1)], '>=', 1000)
c9 = Constraint([(1, x3)], '>=', 100)

model = LinearModel(objective_function=fo, constraints_list=[c1, c2, c3, c4, c5, c6, c7, c8, c9])
p1 = Phase1(linear_model=model)
initial_base = p1.find_base()
p2 = Phase2(linear_model=model, base_indexes=p1.base_variables)
p2.solve()

print(p2.solution)
'''

# Problem setup

x1 = Variable(name='x1')
x2 = Variable(name='x2', constraint=VariableConstraint.Unrestricted)
fo = ObjectiveFunction('max', [(30, x1), (-4, x2)])
c1 = Constraint([(1, x1)], '<=', 5)
c2 = Constraint([(5, x1), (-1, x2)], '<=', 30)
model = LinearModel(objective_function=fo, constraints_list=[c1, c2])

p1 = Phase1(linear_model=model)
initial_base = p1.find_base()
p2 = Phase2(linear_model=model, base_indexes=p1.base_variables)
p2.solve()
print(p2.solution)



