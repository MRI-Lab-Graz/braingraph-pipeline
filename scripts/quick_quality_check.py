#!/usr/bin/env python3
"""
Simple Parameter Uniqueness Checker
===================================

Optional utility (Extras): This script is not required for the core OptiConn
pipeline (Steps 01–03). It provides a lightweight check to ensure different
parameter combinations produce different results by analyzing network measures
files only.

Author: Braingraph Pipeline Team
"""

import pandas as pd
import numpy as np
import glob
import os
import sys
import argparse
import logging
from collections import defaultdict

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

def quick_uniqueness_check(matrices_dir):
    """Quick check using only network measures files."""
    logging.info("🔍 Quick parameter uniqueness check...")
    
    # Find aggregated network measures CSV
    agg_file = os.path.join(matrices_dir, 'aggregated_network_measures.csv')
    
    if not os.path.exists(agg_file):
        logging.error(f"❌ Aggregated file not found: {agg_file}")
        return False
    
    # Load aggregated data
    df = pd.read_csv(agg_file)
    logging.info(f"📊 Loaded {len(df)} network measures records")
    
    # Check parameter diversity
    subjects = df['subject_id'].nunique()
    atlases = df['atlas'].nunique()
    metrics = df['connectivity_metric'].nunique()
    
    logging.info(f"📈 Data diversity:")
    logging.info(f"  - Subjects: {subjects}")
    logging.info(f"  - Atlases: {atlases}")
    logging.info(f"  - Connectivity metrics: {metrics}")
    
    # Expected combinations per subject
    expected_combinations = atlases * metrics
    actual_combinations = df.groupby('subject_id').size()
    
    logging.info(f"\n🎯 Parameter combination check:")
    logging.info(f"  - Expected combinations per subject: {expected_combinations}")
    logging.info(f"  - Actual range: {actual_combinations.min()} - {actual_combinations.max()}")
    
    #!/usr/bin/env python3
    # Supports: --dry-run (delegated)
    # When run without arguments the script prints help: parser.print_help()
    """
    Compatibility wrapper: delegates to `scripts/quality_checks.py quick`.

    Keeps the original entrypoint `scripts/quick_quality_check.py` working while
    centralizing implementation in `quality_checks.py`.
    """

    from __future__ import annotations

    import sys
    from pathlib import Path

    def main():
        # Delegate to the unified quality_checks module
        script = Path(__file__).resolve().parent / 'quality_checks.py'
        args = ['quick'] + sys.argv[1:]
        cmd = [sys.executable, str(script)] + args
        return __import__('subprocess').call(cmd)

    if __name__ == '__main__':
        raise SystemExit(main())
        for measure in quality_measures:
            if measure not in df.columns:
                continue
                
            values = df[measure].dropna().values
            if len(values) == 0:
                continue
                
            Q1 = np.percentile(values, 25)
            Q3 = np.percentile(values, 75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (df[measure] < lower_bound) | (df[measure] > upper_bound)
            outlier_subjects = df[outlier_mask]['subject_id'].unique()
            
            total_outlier_subjects.update(outlier_subjects)
        
        logging.info(f"\n📊 Quality outlier summary:")
        logging.info(f"  - Average outlier rate: {avg_outlier_rate:.1%}")
        logging.info(f"  - Subjects with quality issues: {len(total_outlier_subjects)}")
        
        if len(total_outlier_subjects) > 0:
            logging.info(f"  - Potentially problematic subjects: {list(total_outlier_subjects)[:5]}...")
            
            if avg_outlier_rate > 0.10:  # More than 10% outliers
                logging.warning("⚠️  High outlier rate detected - consider reviewing data quality!")
            else:
                logging.info("✅ Outlier rate within acceptable range")
        else:
            logging.info("✅ No quality outliers detected across all measures")
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Quick parameter uniqueness and quality check')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='Perform a safe dry-run: validate inputs and report actions without side-effects')
    # Print help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    parser.add_argument('matrices_dir', help='Directory containing organized matrices')
    parser.add_argument('--quality-only', action='store_true', help='Run only quality analysis')
    
    args = parser.parse_args()
    setup_logging()
    
    logging.info("🚀 Starting parameter uniqueness and quality analysis...")
    
    success = True
    
    if not args.quality_only:
        success &= quick_uniqueness_check(args.matrices_dir)
    
    success &= quality_outlier_analysis(args.matrices_dir)
    
    if success:
        logging.info("\n✅ Analysis completed successfully!")
        return 0
    else:
        logging.error("\n❌ Analysis completed with issues!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
