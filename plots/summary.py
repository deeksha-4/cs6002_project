import matplotlib.pyplot as plt
import numpy as np

# Given data
x_vals = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
y_vals = np.array([4.5454545, 8.730158730, 12.90322581, 17.07317073, 21.24183007,
                   25.40983607, 29.57746479, 33.74485597, 37.91208791, 42.07920792])

# Line: y = (5/12)x
x_line = np.linspace(0, 110, 500)
y_line = (5/12) * x_line

# Plotting
plt.figure(figsize=(8, 6))
plt.plot(x_vals, y_vals, 'o-', label='Observed Data')
plt.plot(x_line, y_line, 'r--', label='Expected Max Revenue in Myerson')

# Labels and title
plt.xlabel('x')
plt.ylabel('y')
plt.title('Simulated Expected Revenue vs Myerson')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show plot
plt.savefig('SimulationvsMyerson')
