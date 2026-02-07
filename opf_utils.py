"""
Utility functions for Optimal Power Flow optimization
"""
import pyomo.environ as pyo
import json


def solve_and_print(model, AC=True):
    """
    Solve the OPF model and print results.

    Parameters:
    -----------
    model : pyomo ConcreteModel
        The OPF model to solve
    AC : bool
        True for AC OPF, False for DC OPF
    """
    # Select appropriate solver
    if AC:
        # Use NEOS CONOPT for nonlinear AC OPF
        solver_manager = pyo.SolverManagerFactory('neos')
        results = solver_manager.solve(model, opt='conopt', tee=True)
    else:
        # Use local solver for linear DC OPF
        solver = pyo.SolverFactory('glpk')  # Or 'gurobi', 'cplex'
        results = solver.solve(model, tee=True)

    # Print results
    print("\n\nSolution\n")

    # Voltage angles
    print("\nNode\t\tVoltage angle [deg]")
    for i in model.nodes:
        if hasattr(model.x_v_angle[i], 'value') and model.x_v_angle[i].value is not None:
            print(f"{i+1} \t\t {model.x_v_angle[i].value}")
        else:
            print(f"{i+1} \t\t Not solved")

    # Voltage magnitudes (AC only)
    if AC:
        print("\nNode\t\tVoltage magnitude")
        for i in model.nodes:
            if hasattr(model.x_v[i], 'value') and model.x_v[i].value is not None:
                print(f"{i+1} \t\t {model.x_v[i].value}")
            else:
                print(f"{i+1} \t\t Not solved")

    # Real power
    print("\nNode\t\tPower")
    for i in model.nodes:
        if hasattr(model.x_p[i], 'value') and model.x_p[i].value is not None:
            print(f"{i+1} \t\t {model.x_p[i].value}")
        else:
            print(f"{i+1} \t\t Not solved")

    # Reactive power (AC only)
    if AC:
        print("\nNode\t\tReactive Power")
        for i in model.nodes:
            if hasattr(model.x_q[i], 'value') and model.x_q[i].value is not None:
                print(f"{i+1} \t\t {model.x_q[i].value}")
            else:
                print(f"{i+1} \t\t Not solved")

    # Objective value
    if hasattr(model.objective_function, 'expr'):
        obj_value = pyo.value(model.objective_function)
        print(f"\nCost:  {obj_value}")

    return results


def create_results_json(model, team_name, AC=True):
    """
    Export results to JSON file.

    Parameters:
    -----------
    model : pyomo ConcreteModel
        Solved OPF model
    team_name : str
        Team identifier
    AC : bool
        True for AC OPF, False for DC OPF
    """
    results = {
        'team_name': team_name,
        'model_type': 'AC_OPF' if AC else 'DC_OPF',
        'nodes': {}
    }

    for i in model.nodes:
        node_data = {
            'voltage_angle': model.x_v_angle[i].value if hasattr(model.x_v_angle[i], 'value') else None,
            'power': model.x_p[i].value if hasattr(model.x_p[i], 'value') else None
        }

        if AC:
            node_data['voltage_magnitude'] = model.x_v[i].value if hasattr(model.x_v[i], 'value') else None
            node_data['reactive_power'] = model.x_q[i].value if hasattr(model.x_q[i], 'value') else None

        results['nodes'][f'node_{i+1}'] = node_data

    # Add cost
    if hasattr(model.objective_function, 'expr'):
        results['total_cost'] = pyo.value(model.objective_function)

    # Save to file
    filename = f'{team_name}_{"AC" if AC else "DC"}_results.json'
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {filename}")

    return results
