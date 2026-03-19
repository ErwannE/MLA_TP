def no_pl_separation(d, y, c):
    if sum(y) > d:
        raise ValueError(f"Must use PL separation when sum(y) > d, but got sum(y)={sum(y)} and d={d}")
    b = max(c)
    v = [b - c[i] for i in range(len(c))]
    objective_value = sum(v[i] * y[i] for i in range(len(y)))
    return objective_value, b, v