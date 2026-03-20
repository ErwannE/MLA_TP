import gurobipy
from instance import Instance
import numpy as np


def solve_separation(d, y, c):
    m = gurobipy.Model()
    m.setParam('OutputFlag', 0)
    
    # Variables
    b = m.addVar(vtype=gurobipy.GRB.CONTINUOUS, name='b')
    v = m.addVars(d, vtype=gurobipy.GRB.CONTINUOUS, name='v')

    # Objective
    m.setObjective(d*b - gurobipy.quicksum((y[i]*v[i]) for i in range(d)), gurobipy.GRB.MAXIMIZE)

    # Constraints 
    m.addConstrs( b-v[i] <= c[i] for i in range(d))
    m.addConstrs( v[i] >= 0 for i in range(d))
    m.addConstr( gurobipy.quicksum(v[i] for i in range(d))+b <= 100)

    m.optimize()

#    return m.ObjVal, b.X, [v[i].X for i in range(d)]

    if m.status==gurobipy.GRB.OPTIMAL:
        return m.ObjVal, b.X, [v[i].X for i in range(d)]
    elif m.status==gurobipy.GRB.UNBOUNDED:
        m.addConstr( gurobipy.quicksum(v[i] for i in range(d))+b <= 1000)
        m.optimize()
        return m.ObjVal, b.X, [v[i].X for i in range(d)]
 #   return m.ObjVal, b.X, [v[i].X for i in range(d)]



def solve_master(c, f, n, d, cuts):
    m = gurobipy.Model()
    m.setParam('OutputFlag', 0)
    #m.setParam('TimeLimit', 10)
    #m.setParam('MIPGap', 0.01)

    # Variables
    y = m.addVars(d, vtype=gurobipy.GRB.BINARY, name='y')
    w = m.addVar(vtype=gurobipy.GRB.CONTINUOUS, name='w')

    # Objective
    m.setObjective(gurobipy.quicksum((f[i]*y[i]) for i in range(d)) + w, gurobipy.GRB.MINIMIZE)

    # Constraints
    m.addConstrs( w >= cuts[j][0]*d -  gurobipy.quicksum((cuts[j][1][i]*y[i]) for i in range(d)) for j in range(len(cuts)))

    m.optimize()

    return m.ObjVal, [y[i].X for i in range(d)], w.X

def solve_benders(Instance):
    c = Instance.c
    f = Instance.f
    n = Instance.n
    d = Instance.d
    cuts = [(0, np.zeros(d))]
    while True:
        obj_master, y_vals, w_val = solve_master(c, f, n, d, cuts)
        obj_sep, b_val, v_vals = solve_separation(d, y_vals, c)
        if obj_sep <= w_val + 1e-6:
            return obj_master, y_vals
        else:
            cut = (b_val, v_vals)
            cuts.append(cut)
        
Instance = Instance.from_csv('data/instance1.csv')
print(Instance)
obj, y = solve_benders(Instance)
print(f"Optimal value: {obj}")
