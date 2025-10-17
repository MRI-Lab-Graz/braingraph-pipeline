#!/usr/bin/env python3
"""
OptiConn Hub CLI
=================

Central CLI that orchestrates optimization, analysis, and pipeline steps.
This module replaces the root-level braingraph.py by living inside scripts/
and resolving paths relative to the repository root automatically.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from scripts.utils.runtime import configure_stdio, propagate_no_emoji


def repo_root() -> Path:
    """Return repository root directory (parent of scripts/)."""
    # This file lives at <repo>/scripts/opticonn_hub.py
    return Path(__file__).resolve().parent.parent


def _abs(path_like: str | os.PathLike | None) -> str | None:
    if not path_like:
        return None
    return str(Path(path_like).resolve())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="OptiConn - Unbiased, modality-agnostic connectomics optimization & analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
3-Step Workflow:
  1. opticonn find-optimal-parameters --method bayesian -i /path/to/data -o studies/run1
     → Use Bayesian optimization to find the best parameters efficiently.

  2. opticonn apply --data-dir /path/to/full/dataset --optimal-config studies/run1/best_config.json --output-dir studies/run1
     → Apply the winning parameters to your full dataset.

  3. opticonn review -o studies/run1
     → (Optional) Manually review results with an interactive dashboard.

Advanced Exploration:
  opticonn sensitivity -i /path/to/data -o studies/sensitivity_analysis
     → Explore which parameters have the most impact on your results.
        """,
    )

    parser.add_argument("--version", action="version", version="OptiConn v2.0.0")
    parser.add_argument(
        "--no-emoji",
        action="store_true",
        help="Disable emoji in console output (useful on limited terminals)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # New simplified command structure
    p_find = subparsers.add_parser(
        "find-optimal-parameters",
        help="Find optimal parameters using Bayesian optimization or grid sweep",
    )
    p_find.add_argument(
        "--method",
        choices=["bayesian", "sweep"],
        default="bayesian",
        help="Optimization method (default: bayesian)",
    )
    p_find.add_argument("-i", "--data-dir", required=True, help="Input data directory")
    p_find.add_argument(
        "-o", "--output-dir", required=True, help="Output directory for results"
    )
    p_find.add_argument("--config", required=True, help="Configuration file")
    # Bayesian-specific
    p_find.add_argument(
        "--n-iterations",
        type=int,
        default=30,
        help="[Bayesian] Number of optimization iterations",
    )
    p_find.add_argument(
        "--n-bootstrap",
        type=int,
        default=3,
        help="[Bayesian] Number of bootstrap samples per evaluation",
    )
    p_find.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="[Bayesian] Number of parallel workers",
    )
    p_find.add_argument(
        "--random-state",
        type=int,
        help="[Bayesian] Seed for reproducibility",
    )
    # Sweep-specific
    p_find.add_argument(
        "--subjects",
        type=int,
        default=3,
        help="[Sweep] Number of subjects for cross-validation",
    )
    p_find.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    p_apply = subparsers.add_parser(
        "apply", help="Apply optimal parameters to a full dataset"
    )
    p_apply.add_argument("-i", "--data-dir", required=True, help="Input data directory")
    p_apply.add_argument(
        "--optimal-config", required=True, help="Path to the optimal configuration file"
    )
    p_apply.add_argument(
        "-o", "--output-dir", required=True, help="Output directory for analysis"
    )
    p_apply.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    p_review = subparsers.add_parser(
        "review",
        help="Review the results of an optimization run",
        description="Provides a non-interactive summary of the chosen optimal parameters from a 'find-optimal-parameters' run.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_review.add_argument(
        "output_dir",
        type=str,
        help="The output directory of the optimization run to review.",
    )
    p_review.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
    p_review.add_argument(
        "--no-emoji", action="store_true", help="Disable emoji in console output"
    )

    p_sensitivity = subparsers.add_parser(
        "sensitivity", help="Analyze parameter sensitivity"
    )
    p_sensitivity.add_argument(
        "-i", "--data-dir", required=True, help="Input data directory"
    )
    p_sensitivity.add_argument(
        "-o", "--output-dir", required=True, help="Output directory for results"
    )
    p_sensitivity.add_argument("--config", required=True, help="Configuration file")
    p_sensitivity.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()
    root = repo_root()
    scripts_dir = root / "scripts"
    subcommands_dir = scripts_dir / "subcommands"
    configure_stdio(getattr(args, "no_emoji", False))

    import subprocess

    def run_script(script_name: str, script_args: list[str]):
        script_path = subcommands_dir / f"{script_name}.py"
        if not script_path.exists():
            print(f"Error: Script not found at {script_path}")
            return 1
        cmd = [sys.executable, str(script_path)] + script_args
        print(f"🚀 Running command: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, env=propagate_no_emoji())
            return 0
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed with exit code {e.returncode}")
            return e.returncode

    if args.command == "find-optimal-parameters":
        script_name = "find_optimal_parameters"
        script_args = [
            "--method",
            args.method,
            "-i",
            _abs(args.data_dir),
            "-o",
            _abs(args.output_dir),
            "--config",
            _abs(args.config),
        ]
        if args.method == "bayesian":
            script_args.extend(
                [
                    "--n-iterations",
                    str(args.n_iterations),
                    "--n-bootstrap",
                    str(args.n_bootstrap),
                    "--max-workers",
                    str(args.max_workers),
                ]
            )
            if args.random_state is not None:
                script_args.extend(["--random-state", str(args.random_state)])
        elif args.method == "sweep":
            script_args.extend(["--subjects", str(args.subjects)])
        if args.verbose:
            script_args.append("--verbose")
        return run_script(script_name, script_args)

    elif args.command == "apply":
        script_args = [
            "--data-dir",
            _abs(args.data_dir),
            "--output",
            _abs(args.output_dir),
            "--cross-validated-config",
            _abs(args.optimal_config),
            "--step",
            "all",
        ]
        if args.verbose:
            script_args.append("--verbose")
        return run_script("apply", script_args)

    elif args.command == "review":
        script_name = "review"
        script_args = [_abs(args.output_dir)]
        if args.verbose:
            script_args.append("--verbose")
        return run_script(script_name, script_args)

    elif args.command == "sensitivity":
        script_args = [
            "-i",
            _abs(args.data_dir),
            "-o",
            _abs(args.output_dir),
            "--config",
            _abs(args.config),
        ]
        if args.verbose:
            script_args.append("--verbose")
        return run_script("sensitivity", script_args)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
