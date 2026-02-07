"""
Create sample OPF data file for testing.
This creates a 5-bus test system.
"""
import pandas as pd
import numpy as np

# Node Data (5 buses)
node_data = pd.DataFrame({
    'Vmax': [1.00, 1.05, 1.05, 1.05, 1.05],
    'Vmin': [1.00, 0.95, 0.95, 0.95, 0.95],
    'VAnglemax': [0.0, np.pi, np.pi, np.pi, np.pi],
    'VAnglemin': [0.0, -np.pi, -np.pi, -np.pi, -np.pi],
    'Pload': [0.0, 0.0, 0.0, 0.9, 0.239],
    'Qload': [0.0, 0.0, 0.0, 0.4, 0.129],
    'PGmax': [1000.0, 0.0, 0.4, 0.4, 0.0],
    'PGmin': [-1000.0, 0.0, 0.1, 0.05, 0.0],
    'QGmax': [1000.0, 0.0, 0.3, 0.2, 0.0],
    'QGmin': [-1000.0, 0.0, -0.2, -0.2, 0.0],
    'a': [0.0, 0.0, 0.4, 0.5, 0.0],
    'b': [0.35, 0.0, 0.2, 0.3, 0.0],
    'c': [0.0, 0.0, 0.0, 0.0, 0.0]
})

# Real Admittance Matrix (G matrix - 5x5)
# All buses must be connected for feasibility
G_matrix = pd.DataFrame([
    [ 1.57, 0.00, -1.07,  0.00, -0.50],
    [ 0.00, 6.16,  0.00, -5.66, -0.50],
    [-1.07, 0.00,  1.41, -0.09, -0.25],
    [ 0.00,-5.66, -0.09,  6.25, -0.50],
    [-0.50,-0.50, -0.25, -0.50,  1.75]
])

# Imaginary Admittance Matrix (B matrix - 5x5)
B_matrix = pd.DataFrame([
    [-3.14, 0.00,  2.14,  0.00,  1.00],
    [ 0.00,-11.11, 0.00, 10.11,  1.00],
    [ 2.14, 0.00, -2.83,  0.18,  0.51],
    [ 0.00, 10.11, 0.18,-11.29,  1.00],
    [ 1.00, 1.00,  0.51,  1.00, -3.51]
])

# Create Excel file with multiple sheets
with pd.ExcelWriter('data/OPFData.xlsx', engine='openpyxl') as writer:
    node_data.to_excel(writer, sheet_name='NodeData', index=False)
    G_matrix.to_excel(writer, sheet_name='RealAdmittanceMatrix', index=False, header=False)
    B_matrix.to_excel(writer, sheet_name='ImaginaryAdmittanceMatrix', index=False, header=False)

print("Sample OPF data file created successfully at data/OPFData.xlsx")
print("\nBus Configuration:")
print("- Bus 1: Slack bus (external grid)")
print("- Bus 2: Transmission bus")
print("- Bus 3: Generator bus (0.1-0.4 MW)")
print("- Bus 4: Generator bus (0.05-0.4 MW) + Load (0.9 MW)")
print("- Bus 5: Load bus (0.239 MW)")
