import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as mpatches
import numpy as np

# File setup
case = 'myerson_10,10,10'
allocations = {}

# Read the results file
with open('../../results/' + case, 'r') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) != 6:
            continue  # Expected: player b1 b2 b3 alloc=1.0 _

        player, b1_str, b2_str, b3_str, alloc_str, _ = parts
        try:
            b1 = int(b1_str)
            b2 = int(b2_str)
            b3 = int(b3_str)
            allocation = round(float(alloc_str.split('=')[1]))  # Round 0 or 1
        except ValueError:
            continue

        key = (b1, b2, b3)
        if allocation == 1:
            if player == '1':
                allocations[key] = 1
            elif player == '2':
                allocations[key] = 2
            elif player == '3':
                allocations[key] = 3
        elif key not in allocations:
            allocations[key] = -1  # No one got it

# Extract all bids for axes
all_b1 = [key[0] for key in allocations]
all_b2 = [key[1] for key in allocations]
all_b3 = [key[2] for key in allocations]
max_b1 = max(all_b1)
max_b2 = max(all_b2)
max_b3 = max(all_b3)

# 3D plot setup
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Color map: player -> color
color_map = {
    1: 'blue',
    2: 'red',
    3: 'green',
    -1: 'gray'
}

# Plot each point
for (b1, b2, b3), allocation in allocations.items():
    color = color_map.get(allocation, 'black')
    ax.scatter(b1, b2, b3, color=color, s=60, edgecolor='black')

# Custom legend
legend_elements = [
    mpatches.Patch(facecolor='blue', edgecolor='black', label='Player 1'),
    mpatches.Patch(facecolor='red', edgecolor='black', label='Player 2'),
    mpatches.Patch(facecolor='green', edgecolor='black', label='Player 3'),
    mpatches.Patch(facecolor='gray', edgecolor='black', label='No Allocation')
]
ax.legend(handles=legend_elements, loc='upper left')

# Axis labels
ax.set_xlabel('v1')
ax.set_ylabel('v2')
ax.set_zlabel('v3')
ax.set_title('3D Allocation Outcome for (v1, v2, v3)')

# Ticks and grid
ax.set_xticks(np.arange(max_b1 + 1))
ax.set_yticks(np.arange(max_b2 + 1))
ax.set_zticks(np.arange(max_b3 + 1))
ax.grid(True)

# Save figure
plt.tight_layout()
plt.savefig('../../plots/' + case + '_3d.png')
plt.show()
