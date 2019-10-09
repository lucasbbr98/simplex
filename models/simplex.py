from models.linear_model import LinearModel
import numpy as np


class Simplex:
    def __init__(self, linear_model: LinearModel):
        self.lm = linear_model
        self.fix_variables = self.lm.n - self.lm.m
        self.B_indexes = []
        self.B = np.zeros(shape=(self.lm.m, self.lm.m))
        self.N_indexes = []
        self.N = np.zeros(shape=(self.lm.m, self.fix_variables))
        self.Cb = []
        self.Cn = []
        self.iteration_hist = {}