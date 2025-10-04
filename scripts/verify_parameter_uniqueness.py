#!/usr/bin/env python3
# Supports: --dry-run (prints intended actions without running)
# When run without arguments the script prints help: parser.print_help()
"""
Parameter Uniqueness Verification
=================================

Optional utility (Extras): This script is not required for the core OptiConn
pipeline (Steps 01–03). It verifies that different parameter combinations
actually produce different connectivity results. Useful during development and
parameter sweep design to ensure uniqueness.
#!/usr/bin/env python3
# Supports: --dry-run (delegated)
# When run without arguments the script prints help: parser.print_help()
"""
Compatibility wrapper: delegates to `scripts/quality_checks.py uniqueness`.

Keeps the original entrypoint `scripts/verify_parameter_uniqueness.py` working while
centralizing implementation in `quality_checks.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

def main():
    script = Path(__file__).resolve().parent / 'quality_checks.py'
    args = ['uniqueness'] + sys.argv[1:]
    cmd = [sys.executable, str(script)] + args
    return __import__('subprocess').call(cmd)

if __name__ == '__main__':
    raise SystemExit(main())
    parser.add_argument('--output', '-o', help='Output directory for results', default='uniqueness_check_results')
    
    args = parser.parse_args()
    setup_logging()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Run analysis
    results = analyze_parameter_uniqueness(args.matrices_dir)
    
    # Save detailed results
    if results['uniqueness_results'] is not None and not results['uniqueness_results'].empty:
        results_file = os.path.join(args.output, 'parameter_uniqueness_results.csv')
        results['uniqueness_results'].to_csv(results_file, index=False)
        logging.info(f"Detailed results saved to: {results_file}")
    
    # Save duplicate report
    if results['duplicate_matrices']:
        duplicates_file = os.path.join(args.output, 'duplicate_matrices.json')
        import json
        with open(duplicates_file, 'w') as f:
            json.dump(results['duplicate_matrices'], f, indent=2)
        logging.info(f"Duplicate matrices report saved to: {duplicates_file}")
    
    # Summary
    logging.info(f"\n📊 SUMMARY:")
    logging.info(f"Total groups: {results['summary']['total_groups']}")
    logging.info(f"Duplicate groups: {results['summary']['duplicate_groups']}")
    logging.info(f"Parameter diversity: {results['summary']['mean_diversity']:.6f}")
    
    return 0 if results['summary']['duplicate_groups'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
