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

## Verified Results

Both AC and DC OPF have been tested and produce **optimal** solutions.

### AC OPF (NEOS + IPOPT)
```
Solver status: optimal

Bus   Pg (MW)     Theta (deg)   |V| (pu)    Qg (MVAr)
1     1.7116      0.0000        1.0600      -0.0598
2     -0.0000     -3.9083       1.0423      0.3501
3     -0.0000     -6.0082       1.0306      0.2944
4     0.0000      -6.3285       1.0260      0.0000
5     0.0000      -7.1832       1.0120      0.0000

Total Generation Cost: 45.9622
```

### DC OPF (HiGHS)
```
Solver status: optimal

Bus   Pg (MW)     Theta (deg)
1     1.6500      0.0000
2     0.0000      -4.5509
3     0.0000      -7.0065
4     0.0000      -7.4321
5     0.0000      -8.5671

Total Generation Cost: 23.1000
```

### Summary
| Metric | AC OPF | DC OPF |
|--------|--------|--------|
| Total Load | 1.65 MW | 1.65 MW |
| Generation Cost | 45.96 | 23.10 |
| Solver | IPOPT (NEOS) | HiGHS (local) |
| Status | Optimal | Optimal |

## Technical Details

- **Slack Bus**: Reference bus with fixed voltage (1.06 p.u.) and angle (0°)
- **AC Solver**: NEOS server with IPOPT for nonlinear optimization
- **DC Solver**: HiGHS for local linear programming
- **Units**: Power in MW/MVAr, Voltage in per unit (p.u.)
- **Test System**: IEEE 5-bus with 7 transmission lines and 3 generators

## Running the Code

```bash
pip install numpy pyomo highspy
python opf_corrected.py
```

## License

This project is available for educational and research purposes.
