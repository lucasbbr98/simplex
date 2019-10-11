from models.variable import Variable
from models.restriction import Restriction
from models.linear_model import LinearModel
from models.base_finder import InitialBaseFinder
from models.simplex import Simplex

# Declaring Variables
x1 = Variable(fo_coefficient=-2)
x2 = Variable(fo_coefficient=-1)
r1 = Restriction([(1, x1), (1, x2)], '<=', 4)
r2 = Restriction([(1, x1)], '<=', 3)
r3 = Restriction([(1, x2)], '<=', 7 / 2)
# x1 >= 0 and x2 >= 0 are automatically assumed, so no need to worry :D

# Building a LP Model
model = LinearModel()
model.build_objective_function(fo_type='min', variables=[x1, x2])
model.add_restrictions([r1, r2, r3])
model.transform_to_standard_form()


base_finder = InitialBaseFinder(linear_model=model)
base_finder.find_base()
initial_base = base_finder.solution_B_vars_indexes
solver = Simplex(linear_model=model, start_base=initial_base)

solver.solve()
solution = solver.solution
print('Linear Model test passed')