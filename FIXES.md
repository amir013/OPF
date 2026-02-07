# Critical Fixes for OPF Notebook

## Issues Found and Fixed

### 1. Missing Files
**FIXED:** Created `opf_utils.py` with solve_and_print() and create_results_json() functions

**FIXED:** Created `create_sample_data.py` to generate sample OPFData.xlsx file

Run this to create the data file:
```bash
python create_sample_data.py
```

### 2. Logic Errors in notebook

#### Error 1: Q_G_max assignment (Line 12 in add_node_data)
**WRONG:**
```python
m.Q_G_max = data['QGmin']  # BUG: Assigning minimum to maximum!
m.Q_G_min = data['QGmin']
```

**CORRECT:**
```python
m.Q_G_max = data['QGmax']  # Fixed: Use QGmax
m.Q_G_min = data['QGmin']
```

#### Error 2: Voltage bounds constraint (voltage_bounds_rule_2)
**WRONG:**
```python
def voltage_bounds_rule_2(m, i):
    return  m.x_v_angle[i] >= m.V_min[i]  # BUG: Using angle instead of voltage!
```

**CORRECT:**
```python
def voltage_bounds_rule_2(m, i):
    return  m.x_v[i] >= m.V_min[i]  # Fixed: Use voltage magnitude
```

### 3. Additional Improvements Needed

#### Initialize Slack Bus
Add after model variable definition:
```python
# Fix slack bus (bus 0)
model.x_v[0].fix(1.0)  # Fixed voltage magnitude
model.x_v_angle[0].fix(0.0)  # Fixed angle at 0 degrees
```

#### Better Solver Configuration
For AC OPF, use:
```python
solver_manager = pyo.SolverManagerFactory('neos')
results = solver_manager.solve(model, opt='conopt', tee=True)
```

For DC OPF, use:
```python
solver = pyo.SolverFactory('glpk')  # or 'gurobi'
results = solver.solve(model, tee=True)
```

### 4. How to Apply Fixes

1. **Generate data file:**
   ```bash
   cd /home/amir/github/OPF
   python create_sample_data.py
   ```

2. **In the notebook, modify cell 6:**
   Change line with `QGmax`:
   ```python
   m.Q_G_max = data['QGmax']  # FIXED
   m.Q_G_min = data['QGmin']
   ```

3. **In the notebook, modify voltage_bounds_rule_2:**
   ```python
   def voltage_bounds_rule_2(m, i):
       return m.x_v[i] >= m.V_min[i]  # FIXED
   ```

4. **In load_model function, add slack bus initialization:**
   After creating variables, add:
   ```python
   # Fix slack bus constraints
   m.x_v[0].fix(1.0)
   m.x_v_angle[0].fix(0.0)
   ```

5. **Update NEOS email:**
   Replace `'piotr.reszel@tum.de'` with your email

### 5. Expected Output After Fixes

AC OPF should converge to:
- Slack bus voltage: 1.00 p.u. @ 0°
- Other buses: 0.95-1.05 p.u.
- Generation costs minimized
- All loads satisfied

DC OPF should converge to:
- Voltage angles: Realistic values (-π to π)
- Power flows: Balanced
- Lower computation time

## Files Created

1. `opf_utils.py` - Utility functions ✅
2. `create_sample_data.py` - Data generation script ✅
3. `data/OPFData.xlsx` - Sample data (run create_sample_data.py) ⏳
4. `FIXES.md` - This file ✅

## Testing

After applying fixes:
```python
# Test AC OPF
AC = True
model = load_model(FILENAME, pyo.ConcreteModel(), AC)
solve_and_print(model, AC)

# Test DC OPF
AC = False
model = load_model(FILENAME, pyo.ConcreteModel(), AC)
solve_and_print(model, AC)
```

Both should now solve successfully!
