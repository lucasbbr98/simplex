class Variable:
    def __init__(self, fo_coefficient: float,  name='', v_type='Variable'):
        self.name = name
        self.fo_coefficient = fo_coefficient

        # Internal stuff, don't mess up :D
        self.internal_name = ''
        self.internal_initial_index = 0
        self.type = v_type  # Variable, Slack, Excess

    @staticmethod
    def get_key(variable_object):
        return variable_object[1].internal_initial_index

    def __repr__(self):
        return self.internal_name