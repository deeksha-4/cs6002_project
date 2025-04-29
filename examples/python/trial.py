from gurobipy import Model, GRB
from itertools import product, chain, combinations
from collections import defaultdict, deque

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

# Perform DFS to find informed players given a strategy profile
def get_informed_players(source_nodes, reported_edges, num_players):
    visited = set(source_nodes)
    stack = list(source_nodes)

    while stack:
        u = stack.pop()
        for v in reported_edges[u]:
            if v not in visited:
                visited.add(v)
                stack.append(v)
    return visited

try:
    model = Model()

    # Example data
    b = [2, 2]
    R = [[2], []]
    source = [1]  # Source is connected to player 1 
    num_players = len(b)

    # f[i][v] = probability player i has value v
    f = []
    for i in range(num_players):
        vi_range = range(b[i] + 1)
        prob = 1.0 / len(vi_range)
        f_i = {v: prob for v in vi_range}
        f.append(f_i)

    # h[i][r_i] = probability player i reports set r_i (singleton dist on R[i])
    h = []
    for i in range(num_players):
        r_powerset = powerset(R[i])
        h_i = {frozenset(r): 0.0 for r in r_powerset}
        h_i[frozenset(R[i])] = 1.0
        h.append(h_i)

    # Optional: pretty print
    # for i in range(num_players):
    #     print(f"f[{i}] = {f[i]}")
    #     print(f"h[{i}] = { {tuple(r): p for r, p in h[i].items()} }")

    # Generate all possible (v_i, r_i) pairs for each i
    options_per_i = []
    for i in range(num_players):
        vi_range = range(b[i] + 1)
        ri_powerset = powerset(R[i])
        options = [(v, frozenset(r)) for v in vi_range for r in ri_powerset]
        options_per_i.append(options)

    theta_vars = {}
    p_vars = {i: {} for i in range(1, num_players + 1)}
    g_vars = {i: {} for i in range(1, num_players + 1)}

    for combo in product(*options_per_i):
        var_name = make_theta_name(combo)
        theta_var = model.addVar(vtype=GRB.CONTINUOUS, name=var_name)
        theta_vars[combo] = theta_var

        for i in range(1, num_players + 1):
            p_var = model.addVar(lb=0.0, name=f"p{i}_{var_name}")
            g_var = model.addVar(lb=0.0, name=f"g{i}_{var_name}")
            p_vars[i][combo] = p_var
            g_vars[i][combo] = g_var

    model.update()

    # Add constraints to force g_i and p_i = 0 for uninformed players
    for combo in theta_vars:
        # Build the reported network graph from this strategy profile
        reported_edges = defaultdict(set)
        for i, (_, r_i) in enumerate(combo):
            player_id = i + 1
            for neighbor in r_i:
                reported_edges[player_id].add(neighbor)

        # Perform DFS from source to find informed players
        informed = get_informed_players(source, reported_edges, num_players)
        print(f"Theta: {theta_vars[combo].VarName}")
        print(f"Informed players: {informed}")
        print()
        # For each uninformed player, force g_i = 0 and p_i = 0
        for i in range(1, num_players + 1):
            if i not in informed:
                model.addConstr(g_vars[i][combo] == 0, name=f"uninformed_g{i}_{make_theta_name(combo)}")
                model.addConstr(p_vars[i][combo] == 0, name=f"uninformed_p{i}_{make_theta_name(combo)}")
        
    # Print all created variables
    # for combo in theta_vars:
    #     print(f"Theta: {theta_vars[combo].VarName}")
        # for i in range(1,num_players+1):
        #     print(f"  P{i}: {p_vars[i][combo].VarName}, G{i}: {g_vars[i][combo].VarName}")

except Exception as e:
    print("Exception during optimization")
    print(e)
