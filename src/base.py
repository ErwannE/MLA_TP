import gurobipy as gp
from gurobipy import GRB

def no_decomposition_model(instance):
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
    

    return model