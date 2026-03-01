# gf3/interleaver.py
import numpy as np

def interleave(data, depth):
    matrix = np.reshape(data, (-1, depth))
    return matrix.T.flatten()

def deinterleave(data, depth):
    matrix = np.reshape(data, (depth, -1))
    return matrix.T.flatten()