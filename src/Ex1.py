import gurobipy
import numpy as np

try:
    from .instance import Instance
except ImportError:
    try:
        from src.instance import Instance
    except ImportError:
        from instance import Instance


def debug_infeasible_model(model, model_name):
    if model.Status != gurobipy.GRB.INFEASIBLE:
        return

    lp_path = f"{model_name}.lp"
    iis_path = f"{model_name}.ilp"
    print(f"[Gurobi] Modèle infaisable: {model_name}")
    model.printStats()
    model.write(lp_path)
    model.computeIIS()
    model.write(iis_path)
    print(f"[Gurobi] Modèle exporté: {lp_path}")
    print(f"[Gurobi] IIS exporté: {iis_path}")


def solve_separation(d, y, c):
    print (f"Solving separation problem with d={d}, y={y}, c={c}")
    m = gurobipy.Model()
    m.setParam('OutputFlag', 1)

    # Variables
    b = m.addVar(vtype=gurobipy.GRB.CONTINUOUS, name='b')
    v = m.addVars(d, vtype=gurobipy.GRB.CONTINUOUS, name='v')

    # Objective
    m.setObjective(d*b - gurobipy.quicksum((y[i]*v[i]) for i in range(d)), gurobipy.GRB.MAXIMIZE)

    # Constraints 
    m.addConstrs( b-v[i] <= c[i] for i in range(d))
    m.addConstrs( v[i] >= 0 for i in range(d))

    m.optimize()

    debug_infeasible_model(m, "separation_model")
    if m.Status != gurobipy.GRB.OPTIMAL:
        return float('inf'), None, None

    return m.ObjVal, b.X, [v[i].X for i in range(d)]


def solve_master(c, f, n, d, cuts):
    m = gurobipy.Model()
    m.setParam('OutputFlag', 1)
    #m.setParam('TimeLimit', 10)
    #m.setParam('MIPGap', 0.01)

    # Variables
    y = m.addVars(d, vtype=gurobipy.GRB.BINARY, name='y')
    w = m.addVar(vtype=gurobipy.GRB.CONTINUOUS, name='w')

    # Objective
    m.setObjective(gurobipy.quicksum((f[i]*y[i]) for i in range(d)) + w, gurobipy.GRB.MINIMIZE)

    # Constraints
    m.addConstrs( w >= cuts[j][0]*d -  gurobipy.quicksum((cuts[j][1][i]*y[i]) for i in range(d)) for j in range(len(cuts)))
#    for (b_val, v_vals) in cuts:
#        m.addConstr(w >= d * b_val - gurobipy.quicksum(v_vals[i] * y[i] for i in range(d)))
    m.optimize()

    debug_infeasible_model(m, "master_model")
    if m.Status != gurobipy.GRB.OPTIMAL:
        raise RuntimeError(f"Master problem non résolu à l'optimum (status={m.Status}).")

    return m.ObjVal, [y[i].X for i in range(d)], w.X

def solve_benders(instance):
    c = instance.c
    f = instance.f
    n = instance.n
    d = instance.d
    cuts = [(0, np.zeros(d))]
    while True:
        obj_master, y_vals, w_val = solve_master(c, f, n, d, cuts)
        obj_sep, b_val, v_vals = solve_separation(d, y_vals, c)
        if obj_sep <= w_val + 1e-6:  # Tolérance pour la convergence
            return obj_master, y_vals
        else:
            cut = (b_val, v_vals)
            cuts.append(cut)
        
if __name__ == '__main__':
    instance = Instance.from_csv('data/instance1.csv')
    print(instance)
    obj, y = solve_benders(instance)
    #print(f"Optimal value: {obj}")