using JuMP
using CPLEX
using Random

# Structure pour stocker l'instance (équivalent de ta classe Python)
struct Instance
    n::Int
    f::Vector{Float64}
    c::Vector{Float64}
    d::Int
end


function read_instance(filename::String)
    lines = readlines(filename)
    
    n = parse(Int, lines[1])
    f = parse.(Float64, split(lines[2], ","))
    c = parse.(Float64, split(lines[3], ","))
    d = parse(Int, lines[4])
    
    return Instance(n, f, c, d)
end

"""
Crée et résout le modèle sans décomposition
"""
function no_decomposition_model(instance::Instance; y_constraint=false, seed=42)
    n = instance.n
    f = instance.f
    c = instance.c
    d = instance.d

    # Initialisation du modèle avec CPLEX
    model = Model(CPLEX.Optimizer)
    set_optimizer_attribute(model, "CPXPARAM_Benders_Strategy", 3)
    set_silent(model) # Équivalent de OutputFlag = 0

    # Variables de décision
    @variable(model, x[1:n] >= 0)
    @variable(model, y[1:n], Bin)

    # Fonction Objectif
    @objective(model, Min, sum(f[i] * x[i] for i in 1:n) + sum(c[i] * y[i] for i in 1:n))

    # Contraintes de base
    @constraint(model, DemandConstraint, sum(y[i] for i in 1:n) == d)
    @constraint(model, LinkingConstraints[i in 1:n], x[i] >= y[i])

    # Ajout des contraintes aléatoires
    # if y_constraint
    #     Random.seed!(seed) # Fixe la seed globale pour la reproductibilité
    #     nb_constraints = floor(Int, n / 100)
        
    #     if nb_constraints > 0
    #         # Génération des indices (Attention : Julia commence à 1)
    #         idx_i = rand(1:n, nb_constraints)
    #         idx_j = rand(1:n, nb_constraints)
            
    #         for k in 1:nb_constraints
    #             @constraint(model, y[idx_i[k]] >= y[idx_j[k]])
    #         end
    #     end
    # end

    return model
end

# --- Exemple d'utilisation ---
inst = read_instance("data/instances_5.csv")
model = no_decomposition_model(inst, y_constraint=true)
optimize!(model)
solve_time = JuMP.solve_time(model)

println("Statut : ", termination_status(model))
println("Objectif : ", objective_value(model))
println("Temps de résolution (solveur) : ", solve_time, " secondes")
