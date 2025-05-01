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
    b = [100, 100]
    R = [[], []]
    source = [1,2]  # Players which are connected to source
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

    theta_vars = set()
    p_vars = {i: {} for i in range(1, num_players + 1)}
    g_vars = {i: {} for i in range(1, num_players + 1)}

    for combo in product(*options_per_i):
        theta_vars.add(combo)
        var_name = make_theta_name(combo)
        # print(var_name)
        for i in range(1, num_players + 1):
            p_var = model.addVar(vtype=GRB.CONTINUOUS, name=f"p{i}_{var_name}")
            g_var = model.addVar(vtype=GRB.CONTINUOUS, lb=0.0, ub=1.0, name=f"g{i}_{var_name}")
            p_vars[i][combo] = p_var
            g_vars[i][combo] = g_var

    model.update()


    for combo in theta_vars:
        
        # Ensure sum of allocations over all players is 1
        alloc_sum = sum(g_vars[i][combo] for i in range(1, num_players + 1))
        model.addConstr(alloc_sum <= 1, name=f"sum_alloc_{make_theta_name(combo)}")

        # Build the reported network graph from this strategy profile
        reported_edges = defaultdict(set)
        for i, (_, r_i) in enumerate(combo):
            player_id = i + 1
            for neighbor in r_i:
                reported_edges[player_id].add(neighbor)

        # Perform DFS from source to find informed players
        informed = get_informed_players(source, reported_edges, num_players)
        
        # print(f"Theta: {theta_vars[combo].VarName}")
        # print(f"Informed players: {informed}")
        # print()

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

    # Compute α_i(v_i, r_i) for all i, v_i, r_i
    alpha = {i: defaultdict(lambda: defaultdict(float)) for i in range(1, num_players + 1)}

    for i in range(1, num_players + 1):
        vi_range = range(b[i - 1] + 1)
        ri_powerset = [frozenset(r) for r in powerset(R[i - 1])]

        for v_i in vi_range:
            for r_i in ri_powerset:
                alpha_sum_expr = 0
                for combo in theta_vars:
                    v_r_i = combo[i - 1]
                    if v_r_i[0] != v_i or v_r_i[1] != r_i:
                        continue

                    # Multiply over other players' f_j(v_j)
                    product_fj = 1.0
                    for j in range(1, num_players + 1):
                        if j == i:
                            continue
                        v_j = combo[j - 1][0]
                        product_fj *= f[j - 1][v_j]

                    alpha_sum_expr += product_fj * g_vars[i][combo]

                alpha[i][v_i][r_i] = alpha_sum_expr

    # Add monotonicity constraints: αᵢ(vᵢ+1, rᵢ) ≥ αᵢ(vᵢ, rᵢ)
    for i in range(1, num_players + 1):
        vi_range = range(b[i - 1] + 1)
        ri_powerset = [frozenset(r) for r in powerset(R[i - 1])]

        for r_i in ri_powerset:
            for v_i in vi_range[:-1]:  # skip last since we compare v_i to v_i+1
                alpha_current = alpha[i][v_i][r_i]
                alpha_next = alpha[i][v_i + 1][r_i]
                model.addConstr(alpha_next >= alpha_current,
                                name=f"monotonicity_alpha_i{i}_r{''.join(map(str, sorted(r_i)))}_v{v_i}")


    # Compute pay_i(v_i, r_i) for all i, v_i, r_i
    pay = {i: defaultdict(lambda: defaultdict(float)) for i in range(1, num_players + 1)}

    for i in range(1, num_players + 1):
        vi_range = range(b[i - 1] + 1)
        ri_powerset = [frozenset(r) for r in powerset(R[i - 1])]

        for v_i in vi_range:
            for r_i in ri_powerset:
                pay_sum_expr = 0
                for combo in theta_vars:
                    v_r_i = combo[i - 1]
                    if v_r_i[0] != v_i or v_r_i[1] != r_i:
                        continue

                    product_fj = 1.0
                    for j in range(1, num_players + 1):
                        if j == i:
                            continue
                        v_j = combo[j - 1][0]
                        product_fj *= f[j - 1][v_j]

                    pay_sum_expr += product_fj * p_vars[i][combo]

                pay[i][v_i][r_i] = pay_sum_expr

    # Add constraints: pay_i(0, r_i) ≤ 0 for all i, r_i
    for i in range(1, num_players + 1):
        ri_powerset = [frozenset(r) for r in powerset(R[i - 1])]

        for r_i in ri_powerset:
            pay_expr = pay[i][0][r_i]
            model.addConstr(pay_expr <= 0, name=f"pay0_upper_i{i}_r{''.join(map(str, sorted(r_i)))}")

    # Add Valuation IC constraints
    for i in range(1, num_players + 1):
        vi_range = range(b[i - 1] + 1)
        ri_powerset = [frozenset(r) for r in powerset(R[i - 1])]

        for r_i in ri_powerset:
            for v_i in vi_range:
                lhs = v_i * alpha[i][v_i][r_i] - pay[i][v_i][r_i]
                for v_i_prime in vi_range:
                    rhs = v_i * alpha[i][v_i_prime][r_i] - pay[i][v_i_prime][r_i]
                    model.addConstr(lhs >= rhs, name=f"IC_val_i{i}_v{v_i}_v'{v_i_prime}_r{''.join(map(str, sorted(r_i)))}")

    # Add Reporting (edge set) IC constraints
    for i in range(1, num_players + 1):
        vi_range = range(b[i - 1] + 1)
        ri_powerset = [frozenset(r) for r in powerset(R[i - 1])]

        for v_i in vi_range:
            for r_i in ri_powerset:
                lhs = v_i * alpha[i][v_i][r_i] - pay[i][v_i][r_i]
                for r_i_prime in ri_powerset:
                    if not r_i_prime.issubset(r_i) or r_i_prime == r_i:
                        continue
                    rhs = v_i * alpha[i][v_i][r_i_prime] - pay[i][v_i][r_i_prime]
                    model.addConstr(lhs >= rhs, name=f"IC_rep_i{i}_v{v_i}_r{''.join(map(str, sorted(r_i)))}_r'{''.join(map(str, sorted(r_i_prime)))}")

    # Define the objective: maximize expected revenue
    objective_expr = 0

    for i in range(1, num_players + 1):
        vi_range = range(b[i - 1] + 1)
        R_i = frozenset(R[i - 1])  # fixed truthful report

        for v_i in vi_range:
            prob = f[i - 1][v_i]  # f_i(v_i)
            payment = pay[i][v_i][R_i]
            objective_expr += prob * payment

    model.setObjective(objective_expr, GRB.MAXIMIZE)
    model.optimize()

    if model.status == GRB.OPTIMAL:
        
        print("\n--- Allocations and Payments for Truthful Reports ---\n")
        for combo in theta_vars:
            is_truthful = all(r_i == frozenset(R[i]) for i, (_, r_i) in enumerate(combo))
            if not is_truthful:
                continue

            # Extract reported values
            value_profile = [v_i for (v_i, _) in combo]
            allocs = [g_vars[i + 1][combo].X for i in range(num_players)]
            pays = [p_vars[i + 1][combo].X for i in range(num_players)]

            # Print each player's allocation and payment
            for i in range(num_players):
                print(f"{i+1} {value_profile[0]} {value_profile[1]} alloc={allocs[i]:.4f} pay={pays[i]:.4f}")
    else:
        print("Optimization did not find an optimal solution.")

    



except Exception as e:
    print("Exception during optimization")
    print(e)
