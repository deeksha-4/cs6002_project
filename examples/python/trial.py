from gurobipy import Model, GRB
from itertools import product, chain, combinations

# Generate powerset of a list
def powerset(s):
    return list(map(set, chain.from_iterable(combinations(s, r) for r in range(len(s)+1))))

# Format a full theta name from a list of (v_i, r_i)
def make_theta_name(v_r_list):
    parts = []
    for idx, (v, r) in enumerate(v_r_list):
        r_str = ",".join(map(str, sorted(r)))
        parts.append(f"{v}_{{{r_str}}}")
    return f"theta_" + "_".join(parts)

try:
    model = Model()

    # Example data
    b = [2, 1]               # For i=0: v ∈ [0,2]; for i=1: v ∈ [0,1]
    R = [[1, 2], [3]]        # R₀ = {1,2}; R₁ = {3}
    num_players = len(b)

    # Generate all possible (v_i, r_i) pairs for each i
    options_per_i = []
    for i in range(num_players):
        vi_range = range(b[i] + 1)
        ri_powerset = powerset(R[i])
        options = [(v, frozenset(r)) for v in vi_range for r in ri_powerset]
        options_per_i.append(options)

    theta_vars = {}
    p_vars = {i: {} for i in range(num_players)}  # Nested dict: p_vars[i][combo]
    g_vars = {i: {} for i in range(num_players)}

    for combo in product(*options_per_i):
        var_name = make_theta_name(combo)
        theta_var = model.addVar(vtype=GRB.BINARY, name=var_name)
        theta_vars[combo] = theta_var

        for i in range(num_players):
            p_var = model.addVar(lb=0.0, name=f"p{i}_{var_name}")
            g_var = model.addVar(lb=0.0, name=f"g{i}_{var_name}")
            p_vars[i][combo] = p_var
            g_vars[i][combo] = g_var

    model.update()

    # Print all created variables
    for combo in theta_vars:
        print(f"Theta: {theta_vars[combo].VarName}")
        for i in range(num_players):
            print(f"  P{i}: {p_vars[i][combo].VarName}, G{i}: {g_vars[i][combo].VarName}")

except Exception as e:
    print("Exception during optimization")
    print(e)
