"""
Optimal Power Flow (AC & DC) - IEEE 5-Bus Test System
Uses Pyomo for optimization modeling.
- AC OPF: Solved via NEOS Server (IPOPT nonlinear solver)
- DC OPF: Solved locally via HiGHS (linear solver)
"""
import os
import numpy as np
import pyomo.environ as pyo

# NEOS server requires an email
os.environ['NEOS_EMAIL'] = 'user@example.com'

N_BUS = 5

# ──────────────────────────────────────────────────
# IEEE 5-Bus Test System Data
# ──────────────────────────────────────────────────
BUS_DATA = {
    #       Pgen_max  Pgen_min  Qgen_max  Qgen_min  Pload  Qload  Vmax   Vmin   a      b      c
    0: {'PGmax': 2.0, 'PGmin': 0.0, 'QGmax': 1.5, 'QGmin': -1.5,
        'Pload': 0.0, 'Qload': 0.0, 'Vmax': 1.06, 'Vmin': 1.06,
        'a': 0.0, 'b': 14.0, 'c': 0.0},
    1: {'PGmax': 0.8, 'PGmin': 0.0, 'QGmax': 0.6, 'QGmin': -0.4,
        'Pload': 0.2, 'Qload': 0.1, 'Vmax': 1.05, 'Vmin': 0.95,
        'a': 15.0, 'b': 16.0, 'c': 10.0},
    2: {'PGmax': 0.5, 'PGmin': 0.0, 'QGmax': 0.4, 'QGmin': -0.3,
        'Pload': 0.45, 'Qload': 0.15, 'Vmax': 1.05, 'Vmin': 0.95,
        'a': 18.0, 'b': 20.0, 'c': 12.0},
    3: {'PGmax': 0.0, 'PGmin': 0.0, 'QGmax': 0.0, 'QGmin': 0.0,
        'Pload': 0.40, 'Qload': 0.05, 'Vmax': 1.05, 'Vmin': 0.95,
        'a': 0.0, 'b': 0.0, 'c': 0.0},
    4: {'PGmax': 0.0, 'PGmin': 0.0, 'QGmax': 0.0, 'QGmin': 0.0,
        'Pload': 0.60, 'Qload': 0.10, 'Vmax': 1.05, 'Vmin': 0.95,
        'a': 0.0, 'b': 0.0, 'c': 0.0},
}

# Line data: (from_bus, to_bus, resistance, reactance)
LINE_DATA = [
    (0, 1, 0.02, 0.06),
    (0, 2, 0.08, 0.24),
    (1, 2, 0.06, 0.18),
    (1, 3, 0.06, 0.18),
    (1, 4, 0.04, 0.12),
    (2, 3, 0.01, 0.03),
    (3, 4, 0.08, 0.24),
]

# Derived sets
GEN_BUSES = [i for i in range(N_BUS) if BUS_DATA[i]['PGmax'] > 0]
LOAD_BUSES = [i for i in range(N_BUS) if i not in GEN_BUSES]


def build_admittance_matrices():
    """Build G (conductance) and B (susceptance) matrices from line data."""
    G = np.zeros((N_BUS, N_BUS))
    B = np.zeros((N_BUS, N_BUS))

    for (i, j, r, x) in LINE_DATA:
        z_sq = r**2 + x**2
        g_ij = r / z_sq
        b_ij = -x / z_sq

        G[i, i] += g_ij;  G[j, j] += g_ij
        G[i, j] -= g_ij;  G[j, i] -= g_ij
        B[i, i] += b_ij;  B[j, j] += b_ij
        B[i, j] -= b_ij;  B[j, i] -= b_ij

    return G, B


def build_ac_model():
    """Build AC OPF Pyomo model with full nonlinear power flow."""
    G, B = build_admittance_matrices()
    m = pyo.ConcreteModel("AC_OPF")
    m.buses = pyo.Set(initialize=range(N_BUS))

    # Parameters (using Pyomo Param for proper modeling)
    m.Pload = pyo.Param(m.buses, initialize={i: BUS_DATA[i]['Pload'] for i in range(N_BUS)})
    m.Qload = pyo.Param(m.buses, initialize={i: BUS_DATA[i]['Qload'] for i in range(N_BUS)})

    # Variables with initialization
    total_load = sum(BUS_DATA[i]['Pload'] for i in range(N_BUS))
    m.Pg = pyo.Var(m.buses, within=pyo.Reals, initialize={0: total_load, 1: 0.1, 2: 0.1, 3: 0, 4: 0})
    m.Qg = pyo.Var(m.buses, within=pyo.Reals, initialize=0.0)
    m.V = pyo.Var(m.buses, within=pyo.NonNegativeReals,
                  initialize={i: 1.06 if i == 0 else 1.0 for i in range(N_BUS)})
    m.theta = pyo.Var(m.buses, within=pyo.Reals, initialize=0.0)

    # Fix slack bus
    m.V[0].fix(1.06)
    m.theta[0].fix(0.0)

    # Fix non-generator buses to zero generation
    for i in LOAD_BUSES:
        m.Pg[i].fix(0.0)
        m.Qg[i].fix(0.0)

    # Set variable bounds directly (more efficient than constraint functions)
    for i in range(N_BUS):
        m.Pg[i].setlb(BUS_DATA[i]['PGmin'])
        m.Pg[i].setub(BUS_DATA[i]['PGmax'])
        m.Qg[i].setlb(BUS_DATA[i]['QGmin'])
        m.Qg[i].setub(BUS_DATA[i]['QGmax'])
        m.V[i].setlb(BUS_DATA[i]['Vmin'])
        m.V[i].setub(BUS_DATA[i]['Vmax'])
        m.theta[i].setlb(-np.pi)
        m.theta[i].setub(np.pi)

    # Objective: minimize quadratic generation cost
    m.obj = pyo.Objective(
        expr=sum(
            BUS_DATA[i]['a'] * m.Pg[i]**2 +
            BUS_DATA[i]['b'] * m.Pg[i] +
            BUS_DATA[i]['c']
            for i in GEN_BUSES
        ),
        sense=pyo.minimize
    )

    # AC Power Flow equations (nodal power balance)
    def p_balance_rule(m, i):
        Pflow = sum(
            m.V[i] * m.V[k] * (
                float(G[i, k]) * pyo.cos(m.theta[i] - m.theta[k]) +
                float(B[i, k]) * pyo.sin(m.theta[i] - m.theta[k])
            )
            for k in range(N_BUS)
        )
        return m.Pg[i] - m.Pload[i] == Pflow

    def q_balance_rule(m, i):
        Qflow = sum(
            m.V[i] * m.V[k] * (
                float(G[i, k]) * pyo.sin(m.theta[i] - m.theta[k]) -
                float(B[i, k]) * pyo.cos(m.theta[i] - m.theta[k])
            )
            for k in range(N_BUS)
        )
        return m.Qg[i] - m.Qload[i] == Qflow

    m.p_balance = pyo.Constraint(m.buses, rule=p_balance_rule)
    m.q_balance = pyo.Constraint(m.buses, rule=q_balance_rule)

    return m


def build_dc_model():
    """Build DC OPF Pyomo model (linear approximation).

    Assumptions: V=1.0 pu, small angles, lossless lines.
    """
    _, B = build_admittance_matrices()
    m = pyo.ConcreteModel("DC_OPF")
    m.buses = pyo.Set(initialize=range(N_BUS))

    # Parameters
    m.Pload = pyo.Param(m.buses, initialize={i: BUS_DATA[i]['Pload'] for i in range(N_BUS)})

    # Variables
    m.Pg = pyo.Var(m.buses, within=pyo.Reals, initialize=0.0)
    m.theta = pyo.Var(m.buses, within=pyo.Reals, initialize=0.0)

    # Fix slack bus angle
    m.theta[0].fix(0.0)

    # Fix non-generator buses
    for i in LOAD_BUSES:
        m.Pg[i].fix(0.0)

    # Set bounds
    for i in range(N_BUS):
        m.Pg[i].setlb(BUS_DATA[i]['PGmin'])
        m.Pg[i].setub(BUS_DATA[i]['PGmax'])
        m.theta[i].setlb(-np.pi)
        m.theta[i].setub(np.pi)

    # Linear objective: sum(b_i * Pg_i) — standard DC OPF uses linear cost
    m.obj = pyo.Objective(
        expr=sum(BUS_DATA[i]['b'] * m.Pg[i] for i in GEN_BUSES),
        sense=pyo.minimize
    )

    # DC Power Flow: Pg_i - Pload_i = sum(B_ij * (theta_i - theta_j))
    def p_balance_rule(m, i):
        Pflow = sum(float(B[i, k]) * (m.theta[i] - m.theta[k]) for k in range(N_BUS))
        return m.Pg[i] - m.Pload[i] == Pflow

    m.p_balance = pyo.Constraint(m.buses, rule=p_balance_rule)

    return m


def print_results(m, ac=True):
    """Print optimization results in a formatted table."""
    print("\n" + "-" * 60)
    print("RESULTS")
    print("-" * 60)

    header = f"{'Bus':<6}{'Pg (MW)':<12}{'Theta (deg)':<14}"
    if ac:
        header += f"{'|V| (pu)':<12}{'Qg (MVAr)':<12}"
    print(header)
    print("-" * 60)

    for i in m.buses:
        pg = m.Pg[i].value if m.Pg[i].value is not None else 0.0
        theta = np.degrees(m.theta[i].value) if m.theta[i].value is not None else 0.0
        line = f"{i+1:<6}{pg:<12.4f}{theta:<14.4f}"
        if ac:
            v = m.V[i].value if m.V[i].value is not None else 0.0
            qg = m.Qg[i].value if m.Qg[i].value is not None else 0.0
            line += f"{v:<12.4f}{qg:<12.4f}"
        print(line)

    cost = pyo.value(m.obj)
    print(f"\nTotal Generation Cost: {cost:.4f}")
    return cost


def main():
    """Run both AC and DC OPF."""

    # ── AC OPF ─────────────────────────────────────
    print("=" * 60)
    print("AC OPTIMAL POWER FLOW (NEOS + IPOPT)")
    print("=" * 60)

    model_ac = build_ac_model()

    try:
        solver_mgr = pyo.SolverManagerFactory('neos')
        results_ac = solver_mgr.solve(model_ac, opt='ipopt', tee=True)
        status = str(results_ac.solver.termination_condition)
        print(f"\nSolver status: {status}")
        ac_cost = print_results(model_ac, ac=True)
    except Exception as e:
        print(f"\nAC OPF failed: {e}")
        print("Ensure NEOS_EMAIL is set and you have internet access.")
        ac_cost = None

    # ── DC OPF ─────────────────────────────────────
    print("\n" + "=" * 60)
    print("DC OPTIMAL POWER FLOW (HiGHS)")
    print("=" * 60)

    model_dc = build_dc_model()

    try:
        solver = pyo.SolverFactory('appsi_highs')
        if not solver.available():
            raise RuntimeError("HiGHS not available. Install: pip install highspy")
        results_dc = solver.solve(model_dc, tee=True)
        status = str(results_dc.solver.termination_condition)
        print(f"\nSolver status: {status}")
        dc_cost = print_results(model_dc, ac=False)
    except Exception as e:
        print(f"\nDC OPF failed: {e}")
        dc_cost = None

    # ── Summary ────────────────────────────────────
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_load = sum(BUS_DATA[i]['Pload'] for i in range(N_BUS))
    print(f"Total System Load: {total_load:.2f} MW")
    if ac_cost is not None:
        print(f"AC OPF Cost: {ac_cost:.4f} (with losses)")
    if dc_cost is not None:
        print(f"DC OPF Cost: {dc_cost:.4f} (lossless)")


if __name__ == '__main__':
    main()
