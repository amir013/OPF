# Optimal Power Flow (OPF)

AC and DC Optimal Power Flow optimization solver using Pyomo and NEOS.

## Overview

This project implements both AC (Alternating Current) and DC (Direct Current) Optimal Power Flow optimization models to minimize the cost of power generation while satisfying network constraints and power balance equations.

## Features

- **AC Optimal Power Flow**: Full nonlinear AC power flow equations with voltage magnitude and angle constraints
- **DC Optimal Power Flow**: Simplified linearized DC power flow model for faster computation
- **Optimization**: Uses Pyomo for mathematical modeling and NEOS solvers for optimization
- **Cost Minimization**: Minimizes generator operating costs (quadratic cost functions)
- **Network Constraints**: Handles voltage limits, power limits, and admittance matrices

## Problem Formulation

### Decision Variables
- Real power generation (P)
- Reactive power generation (Q)
- Voltage magnitudes (V)
- Voltage angles (θ)

### Objective Function
Minimize total generation cost:
```
Cost = Σ (aᵢ·Pᵢ² + bᵢ·Pᵢ + cᵢ)
```

### Constraints
- Power balance equations
- Generator capacity limits
- Voltage magnitude and angle limits
- Real and imaginary admittance relationships

## Requirements

```
python>=3.7
numpy
pandas
pyomo
openpyxl
```

## Installation

```bash
pip install numpy pandas pyomo openpyxl
```

## Usage

1. Set your NEOS email in the notebook:
```python
os.environ['NEOS_EMAIL'] = 'your.email@example.com'
```

2. Run the AC OPF model:
```python
AC = True
model = load_model(FILENAME, pyo.ConcreteModel(), AC)
solve_and_print(model, AC)
```

3. Run the DC OPF model:
```python
AC = False
model = load_model(FILENAME, pyo.ConcreteModel(), AC)
solve_and_print(model, AC)
```

## Data Format

The input Excel file (`OPFData.xlsx`) should contain three sheets:

1. **NodeData**: Bus parameters (Vmax, Vmin, loads, generator limits, cost coefficients)
2. **RealAdmittanceMatrix**: Real part of admittance matrix (G)
3. **ImaginaryAdmittanceMatrix**: Imaginary part of admittance matrix (B)

## Results

The solver outputs:
- Optimal power generation for each bus
- Voltage magnitudes and angles
- Reactive power generation
- Total operating cost

## Technical Details

- **Slack Bus**: Reference bus with fixed voltage (1.0 p.u.) and angle (0°)
- **Solver**: Uses NEOS server for optimization (CONOPT for AC, CPLEX for DC)
- **Units**: Power in MW/MVA, Voltage in per unit (p.u.)

## License

This project is available for educational and research purposes.
