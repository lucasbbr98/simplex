class Variable:
    def __init__(self, name='', v_type='Variable', initial_index=0, free=False, non_positive=False):
        self.name = name

        # Internal stuff, don't mess up :D
        self.internal_name = name
        self.internal_initial_index = initial_index
        self.type = v_type  # Variable, Slack, Excess
        self.free = free  # If free == True, then x may be positive or negative
        self.non_positive = non_positive  # If non_positive == True, then x <= 0 assumed

    @property
    def id(self):
        return self.internal_initial_index

    @staticmethod
    def get_key(variable_object):
        return variable_object[1].internal_initial_index

    def __repr__(self):
        return self.internal_name


class FreeVariable(Variable):
    def __init__(self, parent_index: int, name='', initial_index=0):
        super().__init__(name=name, v_type='Free', initial_index=initial_index)
        self.parent_index = parent_index


class SlackVariable(Variable):
    def __init__(self, name='', initial_index=0):
        super().__init__(name=name, v_type='Slack', initial_index=initial_index)


class ExcessVariable(Variable):
    def __init__(self, name='', initial_index=0):
        super().__init__(name=name, v_type='Excess', initial_index=initial_index)


class ArtificialVariable(Variable):
    def __init__(self, name='', initial_index=0):
        super().__init__(name=name, v_type='Artificial', initial_index=initial_index)
