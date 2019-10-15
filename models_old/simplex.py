from copy import deepcopy
from models_old.variable import Variable
from models_old.restriction import Restriction
from models_old.linear_model import LinearModel
from models_old.base_finder import InitialBaseFinder
from models_old.internal.simplex_solver import SimplexSolver


class Simplex:
    def __init__(self, linear_model: LinearModel, start_base_indexes=None, skip_standard=False):
        if not linear_model.is_standard_form and not skip_standard:
            print('\n[WARNING] Transforming your LinearModel in standard form. To skip, use Simplex(skip_standard = True)')
            linear_model.transform_to_standard_form()

        if start_base_indexes:
            if not isinstance(start_base_indexes, list) or not len(start_base_indexes) == linear_model.m or not all(isinstance(i, int) for i in start_base_indexes):
                raise ValueError('\n[FATAL ERROR]: Your start_base_indexes must be a list containing only numbers with m "length" of {0}'.format(linear_model.m))

        self.linear_model = linear_model
        self.start_base_indexes = start_base_indexes

        # Solution
        self.fo = None
        self.variables_values = None
        self.status = None

    def solve(self):
        initial_base = None
        if not self.start_base_indexes:
            tmp_linear_model = deepcopy(self.linear_model)
            # Phase 1
            base_finder = InitialBaseFinder(linear_model=tmp_linear_model)
            base_finder.find_base()
            print('\nFound an feasible initial base: {0}'.format(base_finder.solution_B_vars))
            initial_base = base_finder.solution_B_vars_indexes
        else:
            initial_base = self.start_base_indexes

        # Phase 2
        solver = SimplexSolver(linear_model=self.linear_model, start_base=initial_base)
        solver.solve()
        self.variables_values = solver.solution
        self.fo = solver.solution_fo
        self.status = solver.status
        return solver.solution

    @property
    def solution_str(self):
        return '\nFound a solution:\nStatus: {0}\n\nFo(x): {1}\n\nVariables: {2}\n\n'.format(self.status, self.fo, self.variables_values)



if __name__ == '__main__':
    # Declaring Variables
    x1 = Variable(fo_coefficient=5)
    x2 = Variable(fo_coefficient=4/9)
    x3 = Variable(fo_coefficient=-3)
    r1 = Restriction([(2, x1), (3, x2), (1, x3)], '<=', 5)
    r2 = Restriction([(4, x1), (1, x2), (-2/3, x2)], '<=', 11)
    r3 = Restriction([(4, x1), (1, x2), (-2 / 3, x2)], '<=', 91)
    r4 = Restriction([(1, x1), (1, x2), (-2 / 3, x2)], '<=', 2)
    r5 = Restriction([(-1, x2), (-1, x3)], '<=', 6/7)
    r6 = Restriction([(-1, x1), (-1, x2)], '<=', 34)

    # x1 >= 0 and x2 >= 0 are automatically assumed

    # Building a LP Model
    model = LinearModel()
    model.build_objective_function(fo_type='max', variables=[x1, x2, x3])
    model.add_restrictions([r1, r2, r3, r4, r5, r6])
    model.transform_to_standard_form()
    print(model)

    # Simplex Algorithm
    simplex = Simplex(linear_model=model)
    simplex.solve()
    print(simplex.solution_str)