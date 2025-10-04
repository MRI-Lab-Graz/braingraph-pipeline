import subprocess
import sys
from pathlib import Path


def test_monolith_dry_run_score():
    script = Path(__file__).resolve().parents[1] / 'analysis_monolith.py'
    cmd = [sys.executable, str(script), '--dry-run', 'score', '-i', 'data/none', '-o', '/tmp/monolith_score.json']
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    assert res.returncode == 0


def test_monolith_dry_run_compare():
    script = Path(__file__).resolve().parents[1] / 'analysis_monolith.py'
    cmd = [sys.executable, str(script), '--dry-run', 'compare', 'a', 'b', '-o', '/tmp/monolith_compare']
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    assert res.returncode == 0
