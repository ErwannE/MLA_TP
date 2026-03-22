import numpy as np

def no_pl_separation(d, y, c, n):
    if sum(y) > d:
        raise ValueError(f"Must use PL separation when sum(y) > d, but got sum(y)={sum(y)} and d={d}")
    b = np.max(c)
    v = b - np.array(c)
    objective_value = np.sum(c[i] * y[i] for i in range(n))
    return objective_value, b, v