
class Restriction:
    def __init__(self, coefficients: list, inequality: str, restriction_value: float):
        self.inequality = inequality
        self.restriction_value = restriction_value

        if self.restriction_value < 0:
            raise ValueError("Restriction may not have a negative value on the right hand side")

        if inequality == '<=':
            self.equality_type = 0
        elif inequality == '>=':
            self.equality_type = 1
        elif inequality == '=':
            self.equality_type = 2
        else:
            ValueError("Equality operators must be: '<=' or '>=' or '=' not {0}".format(inequality))

        self.coefficients = coefficients

        # Internal stuff, don't mess up :D
        self.internal_name = ''
        self.internal_initial_index = 0

    def __repr__(self):
        f_rep = '{0}:'.format(self.internal_name)

        for index, c in enumerate(self.coefficients):
            if c[0] >= 0:
                f_rep = f_rep + ' + {0}*{1}'.format(str(c[0]), c[1].internal_name)
            else:
                f_rep = f_rep + ' {0}*{1}'.format(str(c[0]), c[1].internal_name)

        f_rep = f_rep + ' {0} {1}'.format(self.inequality, self.restriction_value)

        return f_rep