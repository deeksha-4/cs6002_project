import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Setup
case = 'n=3_[10,10,10]_[[2,3],[],[]]_[1]'
allocations = {}

# Target v3 slices to visualize
slices_to_plot = [0, 3, 6, 10]

# Read the results file
with open('../../results/' + case, 'r') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) != 6:
            continue  # Expect: player b1 b2 b3 alloc=1.0 _
        player, b1_str, b2_str, b3_str, alloc_str, _ = parts
        try:
            b1 = int(b1_str)
            b2 = int(b2_str)
            b3 = int(b3_str)
            allocation = round(float(alloc_str.split('=')[1]))
        except ValueError:
            continue
        if player == '1' and allocation == 1:
            allocations[(b1, b2, b3)] = 1
        elif player == '2' and allocation == 1:
            allocations[(b1, b2, b3)] = 2
        elif player == '3' and allocation == 1:
            allocations[(b1, b2, b3)] = 3
        elif (b1, b2, b3) not in allocations:
            allocations[(b1, b2, b3)] = -1  # No one got it

# Prepare plot
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
axs = axs.flatten()

# Color map
color_map = {
    1: 'blue',    # Player 1
    2: 'red',     # Player 2
    3: 'green',
    -1: 'gray'    # No allocation
}

# Collect max v1 and v2 for axis limits
all_v1 = [k[0] for k in allocations]
all_v2 = [k[1] for k in allocations]
max_v1 = max(all_v1)
max_v2 = max(all_v2)

for idx, v3 in enumerate(slices_to_plot):
    ax = axs[idx]
    for (v1, v2, v3_val), allocation in allocations.items():
        if v3_val == v3:
            color = color_map.get(allocation, 'black')
            ax.scatter(v1, v2, color=color, s=120, edgecolor='black')

    ax.set_title(f'v3 = {v3}')
    ax.set_xlabel('v1')
    ax.set_ylabel('v2')
    ax.set_xticks(np.arange(max_v1 + 1))
    ax.set_yticks(np.arange(max_v2 + 1))
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_xlim(-1, max_v1 + 1)
    ax.set_ylim(-1, max_v2 + 1)

# Add legend
legend_elements = [
    mpatches.Patch(facecolor='blue', edgecolor='black', label='Player 1'),
    mpatches.Patch(facecolor='red', edgecolor='black', label='Player 2'),
    mpatches.Patch(facecolor='gray', edgecolor='black', label='No Allocation')
]
fig.legend(handles=legend_elements, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.02))

fig.suptitle("Allocation Outcomes for Different v3 Slices", fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save and show
plt.savefig('../../plots/' + case + '_slices.png')
plt.show()
