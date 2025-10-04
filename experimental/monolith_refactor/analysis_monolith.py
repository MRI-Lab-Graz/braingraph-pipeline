#!/usr/bin/env python3
"""
analysis_monolith.py
--------------------

Proof-of-concept monolith CLI that demonstrates combining key analysis
steps (scoring / comparison / modeling) into a single entrypoint. This file
is intentionally lightweight and supports `--dry-run` so it can be executed
without installing heavy scientific dependencies.

This script is experimental and lives under `experimental/monolith_refactor/`.
"""

from __future__ import annotations

import argparse
import sys
import json
from pathlib import Path

HAS_DEPS = True
try:
    # Try importing heavy modules that may be present in the main repo
    from scripts.metric_optimizer import MetricOptimizer
    from scripts.statistical_analysis import StatisticalAnalysis
    from scripts.statistical_metric_comparator import ConnectivityMetricComparator
except Exception:
    HAS_DEPS = False


def do_score(args: argparse.Namespace) -> int:
    print("\n[1;34m[monolith] SCORE\u001b[0m")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    if args.dry_run:
        print("[DRY-RUN] Would compute quality scores and write summary JSON")
        return 0
    if not HAS_DEPS:
        print("Missing heavy analysis dependencies. Activate venv and run ./install.sh")
        return 2
    # Minimal integration: instantiate MetricOptimizer and call a placeholder method
    mo = MetricOptimizer()
    print("Running MetricOptimizer (POC)...")
    # real integration would load data and call compute routines
    # For POC we just print a small JSON summary to output
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    summary = {"status": "completed", "note": "POC result placeholder"}
    out.write_text(json.dumps(summary, indent=2))
    print(f"Wrote: {out}")
    return 0


def do_compare(args: argparse.Namespace) -> int:
    print("\n[1;34m[monolith] COMPARE\u001b[0m")
    print(f"Inputs: {args.inputs}")
    print(f"Output: {args.output}")
    if args.dry_run:
        print("[DRY-RUN] Would run cross-metric MANOVA/ANOVA analyses and generate plots")
        return 0
    if not HAS_DEPS:
        print("Missing heavy analysis dependencies. Activate venv and run ./install.sh")
        return 2
    cmc = ConnectivityMetricComparator()
    print("Running ConnectivityMetricComparator (POC)...")
    # placeholder: no heavy computation
    Path(args.output).mkdir(parents=True, exist_ok=True)
    (Path(args.output) / 'compare_summary.json').write_text(json.dumps({"status": "ok"}))
    print(f"Wrote compare_summary.json to {args.output}")
    return 0


def do_model(args: argparse.Namespace) -> int:
    print("\n[1;34m[monolith] MODEL\u001b[0m")
    print(f"Data: {args.data}")
    if args.dry_run:
        print("[DRY-RUN] Would fit statistical models and save results")
        return 0
    if not HAS_DEPS:
        print("Missing heavy analysis dependencies. Activate venv and run ./install.sh")
        return 2
    sa = StatisticalAnalysis()
    print("Fitting model (POC)...")
    # placeholder: write a small model summary
    out = Path(args.output or 'experimental/monolith_refactor/model_summary.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"model": "pooled", "status": "ok"}, indent=2))
    print(f"Wrote: {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(prog='analysis_monolith', description='Experimental monolith analysis POC')
    ap.add_argument('--version', action='version', version='monolith-experiment v0.1')
    ap.add_argument('--dry-run', action='store_true', help='Safe dry-run (no heavy imports executed)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p_score = sub.add_parser('score', help='Compute quality scoring')
    p_score.add_argument('-i', '--input', required=False, default='data/placeholder', help='Input data path')
    p_score.add_argument('-o', '--output', required=False, default='experimental/monolith_refactor/score_summary.json')
    p_score.add_argument('--dry-run', action='store_true')

    p_cmp = sub.add_parser('compare', help='Run statistical comparisons')
    p_cmp.add_argument('inputs', nargs='+', help='One or more inputs (directories or CSV)')
    p_cmp.add_argument('-o', '--output', required=False, default='experimental/monolith_refactor/compare_out')
    p_cmp.add_argument('--dry-run', action='store_true')

    p_mod = sub.add_parser('model', help='Fit models')
    p_mod.add_argument('-d', '--data', required=False, default='data/placeholder.csv')
    p_mod.add_argument('-o', '--output', required=False, default='experimental/monolith_refactor/model_summary.json')
    p_mod.add_argument('--dry-run', action='store_true')

    if len(argv) == 0:
        ap.print_help()
        return 0
    args = ap.parse_args(argv)

    # Respect explicit dry-run either globally or per-subcommand
    if getattr(args, 'dry_run', False) or argv and '--dry-run' in argv:
        args.dry_run = True

    if args.cmd == 'score':
        return do_score(args)
    if args.cmd == 'compare':
        return do_compare(args)
    if args.cmd == 'model':
        return do_model(args)

    ap.print_help()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
