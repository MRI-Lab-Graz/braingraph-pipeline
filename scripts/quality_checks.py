#!/usr/bin/env python3
"""
Unified quality checks: quick diversity checks and parameter uniqueness analysis.

This script merges the functionality of `quick_quality_check.py` and
`verify_parameter_uniqueness.py` into one tool with subcommands:
  - quick: lightweight checks based on aggregated_network_measures.csv
  - uniqueness: deeper matrix-level hashing/stats to find duplicate matrices

Provides --dry-run and prints help when run without arguments to comply with
project global instructions.
"""

from __future__ import annotations

import argparse
import logging
import glob
import os
import sys
from pathlib import Path
from collections import defaultdict
import hashlib
import pandas as pd
import numpy as np

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


def quick_uniqueness_check(matrices_dir: str) -> bool:
    """Quick check using only network measures files (aggregated CSV).

    Mirrors earlier `quick_quality_check.py` behaviour.
    """
    setup_logging()
    logging.info("🔍 Quick parameter uniqueness check...")

    agg_file = os.path.join(matrices_dir, 'aggregated_network_measures.csv')
    if not os.path.exists(agg_file):
        logging.error(f"❌ Aggregated file not found: {agg_file}")
        return False

    df = pd.read_csv(agg_file)
    logging.info(f"📊 Loaded {len(df)} network measures records")

    subjects = df['subject_id'].nunique() if 'subject_id' in df.columns else 0
    atlases = df['atlas'].nunique() if 'atlas' in df.columns else 0
    metrics = df['connectivity_metric'].nunique() if 'connectivity_metric' in df.columns else 0

    logging.info("📈 Data diversity:")
    logging.info(f"  - Subjects: {subjects}")
    logging.info(f"  - Atlases: {atlases}")
    logging.info(f"  - Connectivity metrics: {metrics}")

    expected_combinations = atlases * metrics
    if expected_combinations and 'subject_id' in df.columns:
        actual_combinations = df.groupby('subject_id').size()
        logging.info(f"\n🎯 Parameter combination check:")
        logging.info(f"  - Expected combinations per subject: {expected_combinations}")
        logging.info(f"  - Actual range: {actual_combinations.min()} - {actual_combinations.max()}")
        incomplete_subjects = actual_combinations[actual_combinations < expected_combinations]
        if len(incomplete_subjects) > 0:
            logging.warning(f"⚠️  {len(incomplete_subjects)} subjects have incomplete parameter combinations")
        else:
            logging.info("✅ All subjects have complete parameter combinations")

    # Basic diversity sample for a few measures
    key_measures = ['density', 'global_efficiency(binary)', 'clustering_coeff_average(binary)']
    diversity_results = []
    for subject in (df['subject_id'].unique()[:5] if 'subject_id' in df.columns else []):
        subject_data = df[df['subject_id'] == subject]
        for measure in key_measures:
            if measure in df.columns:
                measure_values = subject_data[measure]
                if len(measure_values) > 1:
                    values = measure_values.values
                    diversity_score = np.std(values) / (np.mean(values) + 1e-10)
                    diversity_results.append({
                        'subject': subject,
                        'measure': measure,
                        'n_values': len(values),
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'diversity_score': diversity_score
                    })

    if diversity_results:
        diversity_df = pd.DataFrame(diversity_results)
        logging.info(f"\n📊 Parameter diversity analysis (sample of {len(diversity_df)} measure/subject combinations):")
        avg_diversity = diversity_df.groupby('measure')['diversity_score'].mean()
        for measure, score in avg_diversity.items():
            logging.info(f"  - {measure}: diversity = {score:.4f}")
        low_diversity = diversity_df[diversity_df['diversity_score'] < 0.01]
        if len(low_diversity) > 0:
            logging.warning(f"⚠️  {len(low_diversity)} measure/subject combinations show low parameter diversity (<0.01)")
        else:
            logging.info("✅ Good parameter diversity detected across sampled measures")

    return True


def compute_matrix_hash(matrix_file: str) -> str | None:
    try:
        df = pd.read_csv(matrix_file)
        matrix_data = df.values.tobytes()
        return hashlib.md5(matrix_data).hexdigest()
    except Exception as e:
        logging.warning(f"Could not hash {matrix_file}: {e}")
        return None


def compute_matrix_stats(matrix_file: str) -> dict | None:
    try:
        df = pd.read_csv(matrix_file)
        matrix = df.values
        mask = ~np.eye(matrix.shape[0], dtype=bool)
        off_diagonal = matrix[mask]
        stats = {
            'mean': np.mean(off_diagonal),
            'std': np.std(off_diagonal),
            'min': np.min(off_diagonal),
            'max': np.max(off_diagonal),
            'zeros': int(np.sum(off_diagonal == 0)),
            'nonzeros': int(np.sum(off_diagonal != 0)),
            'sparsity': float(np.sum(off_diagonal == 0) / len(off_diagonal))
        }
        return stats
    except Exception as e:
        logging.warning(f"Could not compute stats for {matrix_file}: {e}")
        return None


def analyze_parameter_uniqueness(matrices_dir: str) -> bool:
    """Deep uniqueness analysis at matrix-file level (hashing + stats).

    Mirrors earlier `verify_parameter_uniqueness.py` behaviour.
    """
    setup_logging()
    logging.info("Starting parameter uniqueness analysis...")

    pattern = os.path.join(matrices_dir, '**', 'by_atlas', '**', '*.csv')
    csv_files = glob.glob(pattern, recursive=True)
    csv_files = [f for f in csv_files if not f.endswith('_network_measures.csv')]
    logging.info(f"Found {len(csv_files)} connectivity matrices")

    subject_atlas_groups = defaultdict(list)
    for csv_file in csv_files:
        parts = Path(csv_file).parts
        subject = None
        for part in parts:
            if part.startswith('sub-'):
                subject = part.split('.')[0]
                break
        atlas = None
        filename = Path(csv_file).name
        if 'FreeSurferDKT_Cortical' in filename:
            atlas = 'FreeSurferDKT_Cortical'
        elif 'FreeSurferDKT_Subcortical' in filename:
            atlas = 'FreeSurferDKT_Subcortical'
        elif 'HCP-MMP' in filename:
            atlas = 'HCP-MMP'
        elif 'AAL3' in filename:
            atlas = 'AAL3'
        metric = None
        if '.count.' in filename:
            metric = 'count'
        elif '.fa.' in filename:
            metric = 'fa'
        elif '.qa.' in filename:
            metric = 'qa'
        elif '.ncount2.' in filename:
            metric = 'ncount2'
        if subject and atlas and metric:
            key = f"{subject}_{atlas}_{metric}"
            subject_atlas_groups[key].append(csv_file)

    logging.info(f"Grouped into {len(subject_atlas_groups)} subject/atlas/metric combinations")

    uniqueness_results = []
    duplicate_matrices = []

    for group_key, matrix_files in subject_atlas_groups.items():
        if len(matrix_files) < 2:
            continue
        logging.info(f"Analyzing group: {group_key} ({len(matrix_files)} matrices)")
        group_data = []
        for matrix_file in matrix_files:
            matrix_hash = compute_matrix_hash(matrix_file)
            matrix_stats = compute_matrix_stats(matrix_file)
            if matrix_hash and matrix_stats:
                group_data.append({
                    'file': matrix_file,
                    'hash': matrix_hash,
                    'stats': matrix_stats
                })
        hashes = [d['hash'] for d in group_data]
        unique_hashes = set(hashes)
        if len(unique_hashes) < len(hashes):
            duplicate_count = len(hashes) - len(unique_hashes)
            logging.warning(f"Group {group_key}: Found {duplicate_count} duplicate matrices!")
            hash_to_files = defaultdict(list)
            for d in group_data:
                hash_to_files[d['hash']].append(d['file'])
            for hash_val, files in hash_to_files.items():
                if len(files) > 1:
                    duplicate_matrices.append({
                        'group': group_key,
                        'hash': hash_val,
                        'files': files
                    })
        if len(group_data) > 1:
            means = [d['stats']['mean'] for d in group_data]
            sparsities = [d['stats']['sparsity'] for d in group_data]
            uniqueness_results.append({
                'group': group_key,
                'n_matrices': len(group_data),
                'unique_hashes': len(unique_hashes),
                'mean_range': max(means) - min(means) if means else 0,
                'mean_std': float(np.std(means)) if means else 0.0,
                'sparsity_range': max(sparsities) - min(sparsities) if sparsities else 0,
                'sparsity_std': float(np.std(sparsities)) if sparsities else 0.0,
                'diversity_score': float(np.std(means) + np.std(sparsities)) if means else 0.0
            })

    if len(duplicate_matrices) > 0:
        logging.error(f"🚨 FOUND {len(duplicate_matrices)} GROUPS WITH DUPLICATE MATRICES!")
        for dup in duplicate_matrices[:5]:
            logging.error(f"Group: {dup['group']}")
            logging.error(f"Duplicate files: {dup['files'][:2]}...")
    else:
        logging.info("✅ NO DUPLICATE MATRICES FOUND - All parameter combinations produce unique results!")

    if uniqueness_results:
        results_df = pd.DataFrame(uniqueness_results)
        logging.info(f"\nDiversity Statistics (n={len(results_df)} groups):")
        logging.info(f"Mean connectivity range: {results_df['mean_range'].mean():.6f} ± {results_df['mean_range'].std():.6f}")
        logging.info(f"Sparsity range: {results_df['sparsity_range'].mean():.3f} ± {results_df['sparsity_range'].std():.3f}")
        logging.info(f"Overall diversity score: {results_df['diversity_score'].mean():.6f}")

    return True


def main():
    parser = argparse.ArgumentParser(description='Unified quality checks (quick + uniqueness)')
    parser.add_argument('--dry-run', action='store_true', default=False, help='Safe preview only')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_quick = sub.add_parser('quick', help='Quick aggregated-network-measures checks')
    p_quick.add_argument('matrices_dir', help='Directory containing aggregated_network_measures.csv')

    p_uni = sub.add_parser('uniqueness', help='Matrix-level uniqueness checks (hash+stats)')
    p_uni.add_argument('matrices_dir', help='Base directory to search for connectivity matrices')

    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args()
    if args.dry_run:
        print('[DRY-RUN] Quality checks preview')
        print(f"[DRY-RUN] Command: {args.cmd}")
        print(f"[DRY-RUN] Matrices dir: {getattr(args, 'matrices_dir', None)}")
        return 0

    if args.cmd == 'quick':
        return 0 if quick_uniqueness_check(args.matrices_dir) else 1
    if args.cmd == 'uniqueness':
        return 0 if analyze_parameter_uniqueness(args.matrices_dir) else 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
