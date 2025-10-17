#!/usr/bin/env python3
"""
Sweep Utilities
===============

Utility functions for parameter sweep operations.

Author: Braingraph Pipeline Team
"""

import itertools
import random
import numpy as np
from typing import List, Dict, Any, Tuple


def build_param_grid_from_config(config: Dict[str, Any]) -> Tuple[List[Dict[str, List]], Dict[str, str]]:
    """
    Build a parameter grid from sweep_parameters in the config.
    
    Args:
        config: Configuration dictionary containing sweep_parameters
        
    Returns:
        Tuple of (param_values, mapping) where:
        - param_values: List of dicts mapping parameter names to their possible values
        - mapping: Dict mapping parameter names to their config paths
    """
    param_values = []
    mapping = {}
    sweep_params = config.get("sweep_parameters", {})
    
    for key, value in sweep_params.items():
        if key in ["sampling"]:  # Skip meta fields
            continue
            
        if isinstance(value, dict) and "values" in value:
            param_values.append({key: value["values"]})
            if "maps_to" in value:
                mapping[key] = value["maps_to"]
        elif isinstance(value, list):
            # Direct list of values
            param_values.append({key: value})
            
    return param_values, mapping


def grid_product(param_values: List[Dict[str, List]]) -> List[Dict[str, Any]]:
    """
    Generate the Cartesian product of parameter values.
    
    Args:
        param_values: List of dicts mapping parameter names to their possible values
        
    Returns:
        List of parameter combinations
    """
    if not param_values:
        return [{}]
        
    keys = [list(p.keys())[0] for p in param_values]
    grids = [list(p.values())[0] for p in param_values]
    
    product = list(itertools.product(*grids))
    
    return [dict(zip(keys, p)) for p in product]


def random_sampling(param_values: List[Dict[str, List]], n_samples: int, seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generate random samples from the parameter space.
    
    Args:
        param_values: List of dicts mapping parameter names to their possible values
        n_samples: Number of samples to generate
        seed: Random seed for reproducibility
        
    Returns:
        List of randomly sampled parameter combinations
    """
    if not param_values:
        return [{}] * n_samples
    
    random.seed(seed)
    keys = [list(p.keys())[0] for p in param_values]
    grids = [list(p.values())[0] for p in param_values]
    
    samples = []
    for _ in range(n_samples):
        sample = {keys[i]: random.choice(grids[i]) for i in range(len(keys))}
        samples.append(sample)
        
    return samples


def lhs_sampling(param_values: List[Dict[str, List]], n_samples: int, seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generate samples using Latin Hypercube Sampling.
    
    Args:
        param_values: List of dicts mapping parameter names to their possible values
        n_samples: Number of samples to generate
        seed: Random seed for reproducibility
        
    Returns:
        List of LHS-sampled parameter combinations
    """
    try:
        from pyDOE2 import lhs
    except ImportError:
        raise ImportError("LHS sampling requires pyDOE2. Install with: pip install pyDOE2")

    if not param_values:
        return [{}] * n_samples
        
    keys = [list(p.keys())[0] for p in param_values]
    grids = [list(p.values())[0] for p in param_values]
    n_dim = len(keys)
    
    np.random.seed(seed)
    lhd = lhs(n_dim, samples=n_samples)
    
    samples = []
    for i in range(n_samples):
        sample = {}
        for j in range(n_dim):
            idx = int(lhd[i, j] * len(grids[j]))
            idx = min(idx, len(grids[j]) - 1)  # Ensure we don't exceed bounds
            sample[keys[j]] = grids[j][idx]
        samples.append(sample)
        
    return samples


def apply_param_choice_to_config(
    base_config: Dict[str, Any], 
    choice: Dict[str, Any], 
    mapping: Dict[str, str]
) -> Dict[str, Any]:
    """
    Apply a parameter choice to a base configuration.
    
    Args:
        base_config: Base configuration dictionary
        choice: Parameter choices to apply
        mapping: Mapping of parameter names to config paths
        
    Returns:
        New configuration with parameters applied
    """
    import copy
    derived_config = copy.deepcopy(base_config)
    
    for key, value in choice.items():
        if key in mapping:
            # Navigate to the target location in the config
            path_parts = mapping[key].split('.')
            target = derived_config
            
            for part in path_parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            
            # Set the final value
            target[path_parts[-1]] = value
        else:
            # Direct assignment to top level
            derived_config[key] = value
    
    return derived_config
