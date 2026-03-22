import gurobipy as gp
from gurobipy import GRB
import numpy as np

def no_decomposition_model(instance, y_constraint=False, seed=42):
    n = instance.n
    f = instance.f
    c = instance.c
    d = instance.d

    model = gp.Model("NoDecomposition")
    # Decision variables
    x = model.addVars(n, vtype=GRB.CONTINUOUS, name="x")
    y = model.addVars(n, vtype=GRB.BINARY, name="y")

    # Objective function
    model.setObjective(gp.quicksum(f[i] * x[i] for i in range(n)) + gp.quicksum(c[i] * y[i] for i in range(n)), GRB.MINIMIZE)

    # Constraints
    model.addConstr(gp.quicksum(y[i] for i in range(n)) == d, "DemandConstraint")
    model.addConstrs((x[i] >= y[i] for i in range(n)), "LinkingConstraints")
    
    if y_constraint:
        rng = np.random.default_rng(seed)
        nb_constraints = n // 100
        if nb_constraints > 0:
            # Génération rapide de paires d'indices aléatoires
            idx_i = rng.integers(0, n, size=nb_constraints)
            idx_j = rng.integers(0, n, size=nb_constraints)
            
            # Ajout groupé pour la performance
            model.addConstrs(
                (y[idx_i[k]] >= y[idx_j[k]] for k in range(nb_constraints)),
                name="rand_y_cons"
            )

    return model

def solve_no_decomposition(instance):
    model = no_decomposition_model(instance)
    model.optimize()

    y_values = [model.getAttr('X', model.getVars())[i] for i in range(len(model.getVars())) if 'y' in model.getVars()[i].varName]
    return model.objVal, y_values