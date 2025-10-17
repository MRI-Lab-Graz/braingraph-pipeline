# OptiConn Simplified Workflow

## Overview

The `opticonn` tool has been restructured to provide a simpler, more intuitive workflow for finding optimal tractography parameters.

## New Command Structure

### 1. Find Optimal Parameters
Find the best parameters using either Bayesian optimization or parameter sweep:

```bash
# Bayesian optimization (intelligent search)
opticonn find-optimal-parameters --method bayesian \
  -i data/subjects \
  -o results/optimization \
  --config configs/base_config.json \
  --n-iterations 30 \
  --max-workers 4

# Parameter sweep (exhaustive search)
opticonn find-optimal-parameters --method sweep \
  -i data/subjects \
  -o results/sweep \
  --config configs/sweep_config.json \
  --subjects 5 \
  --max-workers 4
```

**Options:**
- `--method`: Choose between `bayesian` or `sweep`
- `-i, --data-dir`: Input data directory
- `-o, --output-dir`: Output directory for results
- `--config`: Configuration file
- `--n-iterations`: [Bayesian] Number of optimization iterations (default: 30)
- `--max-workers`: Maximum parallel workers (default: 1)
- `--subjects`: [Sweep] Number of subjects to test (default: 3)
- `--verbose`: Enable detailed output

### 2. Apply Configuration
Apply a selected optimal configuration to your full dataset:

```bash
opticonn apply \
  --data-dir data/full_dataset \
  --output results/final_analysis \
  --extraction-config results/optimization/best_config.json \
  --step all
```

**Options:**
- `--data-dir`: Input data directory
- `--output`: Output directory
- `--extraction-config`: Configuration file to use
- `--step`: Pipeline step(s) to run (01, 02, 03, all, analysis)
- `--verbose`: Enable verbose output
- `--quiet`: Reduce console output

### 3. Sensitivity Analysis
Analyze how sensitive your results are to parameter variations:

```bash
opticonn sensitivity \
  --config results/optimization/best_config.json \
  --output results/sensitivity \
  --parameter fa_threshold \
  --range 0.05 0.20 \
  --steps 10
```

**Options:**
- `--config`: Base configuration file
- `--output`: Output directory
- `--parameter`: Parameter to vary
- `--range`: Min and max values
- `--steps`: Number of steps

### 4. Review Results
Interactive review and comparison of optimization results:

```bash
opticonn review results/optimization
```

## Workflow Example

### Step 1: Find Optimal Parameters

Start with Bayesian optimization to efficiently find good parameters:

```bash
opticonn find-optimal-parameters --method bayesian \
  -i data/fib_samples \
  -o results/bayesian_opt \
  --config configs/base_config.json \
  --n-iterations 20 \
  --max-workers 2 \
  --verbose
```

This will:
1. Intelligently sample the parameter space
2. Run tractography for each parameter set
3. Evaluate QA scores
4. Find the optimal combination
5. Save results to `results/bayesian_opt/bayesian_optimization_results.json`

### Step 2: Validate with Sweep (Optional)

For a more thorough search in a specific region:

```bash
opticonn find-optimal-parameters --method sweep \
  -i data/fib_samples \
  -o results/sweep_validation \
  --config configs/sweep_narrow.json \
  --subjects 5 \
  --max-workers 4
```

### Step 3: Apply to Full Dataset

Once you have optimal parameters:

```bash
opticonn apply \
  --data-dir data/all_subjects \
  --output results/final_analysis \
  --extraction-config results/bayesian_opt/best_config.json \
  --step all
```

### Step 4: Sensitivity Analysis

Check robustness of your parameters:

```bash
opticonn sensitivity \
  --config results/bayesian_opt/best_config.json \
  --output results/sensitivity \
  --parameter fa_threshold \
  --range 0.05 0.20 \
  --steps 10
```

## Configuration Files

### Bayesian Optimization Config
The config file should specify parameter ranges:

```json
{
  "tract_count": 100000,
  "tracking_parameters": {
    "fa_threshold": 0.1,
    "min_length": 20,
    "turning_angle": 45.0,
    "step_size": 1.0
  },
  "parameter_ranges": {
    "tract_count": [10000, 200000],
    "fa_threshold": [0.05, 0.3],
    "min_length": [5, 50],
    "turning_angle": [30.0, 90.0],
    "step_size": [0.5, 2.0]
  }
}
```

### Sweep Config
For parameter sweep, specify discrete values:

```json
{
  "sweep_parameters": {
    "tract_count": {
      "values": [50000, 100000, 150000],
      "maps_to": "tract_count"
    },
    "fa_threshold": {
      "values": [0.05, 0.10, 0.15, 0.20],
      "maps_to": "tracking_parameters.fa_threshold"
    },
    "sampling": {
      "method": "grid",
      "n_samples": 12,
      "random_seed": 42
    }
  }
}
```

## Output Structure

### Bayesian Optimization Output
```
results/bayesian_opt/
├── bayesian_optimization_results.json  # Final results
├── bayesian_optimization_progress.json # Progress tracking
├── iterations/                         # Individual iterations
│   ├── iteration_0001/
│   │   ├── iteration_0001_config.json
│   │   ├── 01_connectivity/
│   │   └── 02_optimization/
│   └── ...
```

### Sweep Output
```
results/sweep/
├── sweep_results.json                  # Final results
├── configs/                           # Generated configs
│   ├── combination_0001.json
│   └── ...
├── combinations/                      # Test results
│   ├── combination_0001/
│   │   ├── 01_connectivity/
│   │   └── 02_optimization/
│   └── ...
```

## Tips & Best Practices

1. **Start with Bayesian**: More efficient for initial exploration
2. **Use Sweep for Validation**: Once you have a good region, sweep can validate
3. **Parallel Processing**: Use `--max-workers` to speed up optimization
4. **Verbose Mode**: Use `--verbose` during testing to see detailed output
5. **Check Sensitivity**: Always run sensitivity analysis on final parameters

## Migration from Old Commands

Old workflow:
```bash
opticonn bayesian -i data -o results --config config.json --n-iterations 20
opticonn sweep -i data -o results --config config.json
opticonn pipeline --data-dir data --output results --config config.json
```

New workflow:
```bash
opticonn find-optimal-parameters --method bayesian -i data -o results --config config.json --n-iterations 20
opticonn find-optimal-parameters --method sweep -i data -o results --config config.json
opticonn apply --data-dir data --output results --extraction-config config.json
```
