import gurobipy
import numpy as np
#from separation import no_pl_separation
import time
     
try:
    from .separation import no_pl_separation
except ImportError:
    try:
        from src.separation import no_pl_separation
    except ImportError:
        from separation import no_pl_separation

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


def solve_separation(d, y, c, n, verbose=False):
    if verbose:
        print (f"Solving separation problem with d={d}, y={y}, c={c}, n={n}")
    m = gurobipy.Model()
    m.setParam('OutputFlag', 0)

    # Variables
    b = m.addVar(vtype=gurobipy.GRB.CONTINUOUS, name='b')
    v = m.addVars(n, vtype=gurobipy.GRB.CONTINUOUS, name='v')

    # Objective
    m.setObjective(d*b - gurobipy.quicksum((y[i]*v[i]) for i in range(n)), gurobipy.GRB.MAXIMIZE)

    # Constraints 
    m.addConstrs( b-v[i] <= c[i] for i in range(n))
    m.addConstrs( v[i] >= 0 for i in range(n)) 
    m.addConstr( gurobipy.quicksum(v[i] for i in range(d))+b <= 100)

    m.optimize()
    if m.Status in [gurobipy.GRB.INFEASIBLE, gurobipy.GRB.UNBOUNDED, gurobipy.GRB.INF_OR_UNBD]:
        m.addConstr(gurobipy.quicksum(v[i] for i in range(n)) + b == 1000, name="contrainte_secours")
        m.optimize()

    debug_infeasible_model(m, "separation_model")
    if m.Status != gurobipy.GRB.OPTIMAL:
        return float('inf'), None, None

    return m.ObjVal, b.X, [v[i].X for i in range(n)]


def solve_master(c, f, n, d, cuts):
    m = gurobipy.Model()
    m.setParam('OutputFlag', 0)

    # Variables
    y = m.addVars(n, vtype=gurobipy.GRB.BINARY, name='y')
    w = m.addVar(vtype=gurobipy.GRB.CONTINUOUS, name='w')

    # Objective
    m.setObjective(gurobipy.quicksum((f[i]*y[i]) for i in range(n)) + w, gurobipy.GRB.MINIMIZE)

    # Constraints
    m.addConstrs( w >= cuts[j][0]*d -  gurobipy.quicksum((cuts[j][1][i]*y[i]) for i in range(n)) for j in range(len(cuts)))
    m.optimize()
    return m.ObjVal, [y[i].X for i in range(n)], w.X

def solve_benders(instance, with_PL=True):
    c = instance.c
    f = instance.f
    n = instance.n
    d = instance.d
    cuts = [(0, np.zeros(n))]
    start_time = time.time()
    while True:
        obj_master, y_vals, w_val = solve_master(c, f, n, d, cuts)
        if not with_PL and sum(y_vals) == d:
            obj_sep, b_val, v_vals = no_pl_separation(d, y_vals, c, n)
        else:
            obj_sep, b_val, v_vals = solve_separation(d, y_vals, c, n)
        if obj_sep <= w_val + 1e-6:  # Tolérance pour la convergence
            end_time = time.time()
            elapsed_time = end_time - start_time
            return obj_master, y_vals, elapsed_time
        else:
            cut = (b_val, v_vals)
            cuts.append(cut)



def solve_benders_full(instance, with_PL=True, y_constraint=False, seed=42):
    c, f, n, d = instance.c, instance.f, instance.n, instance.d
    
    m = gurobipy.Model("Benders_Master")
    m.setParam('OutputFlag', 0)

    # Variables
    y = m.addVars(n, vtype=gurobipy.GRB.BINARY, name='y')
    w = m.addVar(vtype=gurobipy.GRB.CONTINUOUS, name='w', lb=0)
    
    m.setObjective(gurobipy.quicksum(f[i]*y[i] for i in range(n)) + w, gurobipy.GRB.MINIMIZE)

    if y_constraint:
        rng = np.random.default_rng(seed)
        nb_constraints = n // 100
        if nb_constraints > 0:
            idx_i = rng.integers(0, n, size=nb_constraints)
            idx_j = rng.integers(0, n, size=nb_constraints)
            for k in range(nb_constraints):
                m.addConstr(y[idx_i[k]] >= y[idx_j[k]], name=f"rand_y_{k}")

    start_time = time.time()
    
    while True:
        m.optimize()
        
        if m.Status != gurobipy.GRB.OPTIMAL:
            return None, None, time.time() - start_time 

        obj_master = m.ObjVal
        y_vals = [y[i].X for i in range(n)]
        w_val = w.X

        if not with_PL and sum(y_vals) == d:
            obj_sep, b_val, v_vals = no_pl_separation(d, y_vals, c, n)
        else:
            obj_sep, b_val, v_vals = solve_separation(d, y_vals, c, n)

        # Test de convergence avec epsilon
        if obj_sep <= w_val + 1e-6:
            elapsed_time = time.time() - start_time
            return obj_master, y_vals, elapsed_time
        
        else:
            m .addConstr(w >= b_val * d - gurobipy.quicksum(v_vals[i] * y[i] for i in range(n)))


if __name__ == '__main__':
    instance = Instance.from_csv('data/instance1.csv')
    print(instance)
    #obj, y, elapsed_time = solve_benders(instance, False)
    obj, y, elapsed_time = solve_benders_full(instance, with_PL=True, y_constraint=True, seed=42)
    print(f"Optimal value: {obj}")
    print(f"y: {y}")