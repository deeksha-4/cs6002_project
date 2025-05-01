import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Generate random 3D data
np.random.seed(0)
x = np.random.rand(100)
y = np.random.rand(100)
z = np.random.rand(100)

# Color based on the z-values
colors = z  # or any other criteria you'd like

# Create the figure and the 3D axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Scatter plot with color mapping
sc = ax.scatter(x, y, z, c=colors, cmap='viridis')  # You can choose a different colormap

# Add a color bar
plt.colorbar(sc)

# Show the plot
plt.show()
