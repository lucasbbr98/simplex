from models.variable import Variable
from models.function import ObjectiveFunction, Constraint
from models.linear_model import LinearModel
from models.phase1 import Phase1
from models.phase2 import Phase2

x1 = Variable(name='x1')
x2 = Variable(name='x2')
fo = ObjectiveFunction('max', [(3, x1), (5, x2)])
c1 = Constraint([(1, x1)], '<=', 4)
c2 = Constraint([(2, x2)], '<=', 12)
c3 = Constraint([(3, x1), (2, x2)], '=', 18)
model = LinearModel(objective_function=fo, constraints_list=[c1, c2])
p1 = Phase1(linear_model=model)
initial_base = p1.find_base()
p2 = Phase2(linear_model=model, base_indexes=p1.base_variables)
p2.solve()

print(p2.solution)
