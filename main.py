from models.variable import Variable
from models.restriction import Restriction
from models.linear_model import LinearModel
from models.base_finder import InitialBaseFinder
from models.internal.simplex_solver import SimplexSolver

# Declaring Variables
x1 = Variable(fo_coefficient=10)
x2 = Variable(fo_coefficient=7)
r1 = Restriction([(2, x1), (1, x2)], '<=', 5000)
r2 = Restriction([(4, x1), (5, x2)], '<=', 15000)
# x1 >= 0 and x2 >= 0 are automatically assumed

# Building a LP Model
model = LinearModel()
model.build_objective_function(fo_type='max', variables=[x1, x2])
model.add_restrictions([r1, r2])
model.transform_to_standard_form()

# Finds an initial feasible solution
base_finder = InitialBaseFinder(linear_model=model)
base_finder.find_base()
initial_base = base_finder.solution_B_vars_indexes

# Simplex Algorithm
solver = SimplexSolver(linear_model=model, start_base=initial_base)
solver.solve()
solution = solver.solution
print(solution)