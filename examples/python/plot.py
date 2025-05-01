import matplotlib.pyplot as plt
import numpy as np
import sys
# Initialize allocation map: (b1, b2) -> allocation (0, 1, or -1 for empty)
case = 'myerson_20,10'
allocations = {}
# Read the results file (output.txt)
with open('../../results/' + case, 'r') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) != 5:
            continue  # Skip malformed lines

        player, b1_str, b2_str, alloc_str, _ = parts
        try:
            b1 = int(b1_str)
            b2 = int(b2_str)
            allocation = round(float(alloc_str.split('=')[1]))  # Round the allocation (0 or 1)
        except ValueError:
            continue  # Skip lines with conversion issues
        # Store allocation; use -1 for empty allocation (if no allocation)
        if player == '1' and allocation == 1:
            allocations[(b1, b2)] = 1  # Player 1's allocation
        elif player == '2' and allocation == 1:
            allocations[(b1, b2)] = 0  # Player 2's allocation
        elif (b1,b2) not in allocations:
            allocations[(b1, b2)] = -1 # No one got it
        
# Determine grid size
all_b1 = [key[0] for key in allocations]
all_b2 = [key[1] for key in allocations]
max_b1 = max(all_b1)
max_b2 = max(all_b2)

# Initialize the plot
plt.figure(figsize=(8, 6))

# Plot circles for each allocation
for (b1, b2), allocation in allocations.items():
    if allocation == 1:
        # Player 1's circle (color blue)
        plt.scatter(b1, b2, color='blue', s=200, edgecolor='black', marker='o')
    elif allocation == 0:
        # Player 2's circle (color red)
        plt.scatter(b1, b2, color='red', s=200, edgecolor='black', marker='o')
    else:
        # Empty allocation (no circle or gray color)
        plt.scatter(b1, b2, color='gray', s=200, edgecolor='black', marker='o')

# Labels and title
plt.xlabel("b1")
plt.ylabel("b2")
plt.title("Allocation Outcome for Each (b1, b2) Pair")

# Grid and ticks
plt.xticks(np.arange(max_b1+1))
plt.yticks(np.arange(max_b2+1))
plt.grid(visible=True, color='gray', linestyle='--', alpha=0.3)

# Show plot
plt.savefig('../../plots/' + case)
