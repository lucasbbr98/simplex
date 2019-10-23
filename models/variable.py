from enum import Enum


class VariableConstraint(Enum):
    Positive = 1
    Negative = 2
    Unrestricted = 3


class Variable:
    def __init__(self, name='', v_type='Variable', initial_index=0, constraint: VariableConstraint = VariableConstraint.Positive, integer=False):
        self.name = name

        # Internal stuff, don't mess up :D
        self.internal_name = name
        self.internal_initial_index = initial_index
        self.type = v_type  # Variable, Slack, Excess

        # Backwards compatibility, could be rewritten
        self.free = False
        self.non_positive = False
        self.integer = integer

        if not isinstance(constraint, VariableConstraint):
            raise ValueError("variable_constraint must be a VariableConstraint() enum object")

        if constraint == VariableConstraint.Unrestricted:
            self.free = True  # If free == True, then x may be positive or negative
        elif constraint == VariableConstraint.Negative:
            self.non_positive = True  # If negative == True, then x <= 0 assumed

    @property
    def id(self):
        return self.internal_initial_index

    @staticmethod
    def get_key(variable_object):
        return variable_object[1].internal_initial_index

    def __repr__(self):
        return self.internal_name


class FreeVariable(Variable):
    def __init__(self, positive: bool, parent_index: int, name='', initial_index=0, integer=False):
        super().__init__(name=name, v_type='Free', initial_index=initial_index, integer=integer)
        self.parent_index = parent_index
        self.positive = positive


class SlackVariable(Variable):
    def __init__(self, name='', initial_index=0):
        super().__init__(name=name, v_type='Slack', initial_index=initial_index)


class ExcessVariable(Variable):
    def __init__(self, name='', initial_index=0):
        super().__init__(name=name, v_type='Excess', initial_index=initial_index)


class ArtificialVariable(Variable):
    def __init__(self, name='', initial_index=0):
        super().__init__(name=name, v_type='Artificial', initial_index=initial_index)
