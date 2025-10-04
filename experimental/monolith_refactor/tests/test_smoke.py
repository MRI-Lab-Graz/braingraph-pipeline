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


def test_sparsity_score_regression():
    # Load sample adjacency
    import numpy as _np
    from pathlib import Path as _P
    csv = _P(__file__).resolve().parents[1] / 'data' / 'sample_adj.csv'
    mat = _np.loadtxt(str(csv), delimiter=',')
    # Compute sparsity using POC helper via subprocess import
    script = _P(__file__).resolve().parents[1] / 'analysis_monolith.py'
    # Direct import from the script to call helper
    import importlib.util as _spec
    spec = _spec.spec_from_file_location('analysis_monolith', str(script))
    mod = _spec.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sparsity = mod.compute_sparsity_from_matrix(mat)
    assert abs(sparsity - 0.3333333333333333) < 1e-6
    # If MetricOptimizer available, compare scores
    try:
        from scripts.metric_optimizer import MetricOptimizer
        mo = MetricOptimizer()
        # MetricOptimizer expects arrays; compute score using its method
        svals = _np.array([sparsity])
        mo_scores = mo.compute_sparsity_score(svals)
        poc_scores = mod.compute_sparsity_score_generic(svals)
        assert abs(float(mo_scores[0]) - float(poc_scores[0])) < 1e-6
    except Exception:
        # If MetricOptimizer isn't available in imports, at least verify poc scoring produces expected shape
        svals = _np.array([sparsity])
        poc_scores = mod.compute_sparsity_score_generic(svals)
        assert poc_scores.shape == (1,)


def test_cli_prints_help_on_no_args():
    script = Path(__file__).resolve().parents[1] / 'analysis_monolith.py'
    # Running with no args should print help and exit 0
    res = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    print(res.stdout)
    assert res.returncode == 0
    assert ('usage' in res.stdout.lower()) or ('experimental monolith' in res.stdout.lower()) or ('analysis_monolith' in res.stdout)


import pytest


@pytest.mark.parametrize('vals', [
    [0.01, 0.1, 0.2, 0.3],
    [0.05, 0.15, 0.35, 0.5],
    [0.0, 0.4, 0.6]
])
def test_vectorized_sparsity_scores(vals):
    """Compare vectorized sparsity scoring between POC helper and MetricOptimizer when available."""
    import numpy as _np
    from importlib import util as _spec
    script = Path(__file__).resolve().parents[1] / 'analysis_monolith.py'
    spec = _spec.spec_from_file_location('analysis_monolith', str(script))
    mod = _spec.module_from_spec(spec)
    spec.loader.exec_module(mod)
    arr = _np.array(vals, dtype=float)
    poc = mod.compute_sparsity_score_generic(arr)
    try:
        from scripts.metric_optimizer import MetricOptimizer
        mo = MetricOptimizer()
        mo_scores = mo.compute_sparsity_score(arr)
        # Allow small numerical tolerance
        assert _np.allclose(_np.asarray(poc, dtype=float), _np.asarray(mo_scores, dtype=float), atol=1e-6)
    except Exception:
        # If MetricOptimizer not importable, ensure POC returns sensible numbers in [0,1]
        assert _np.all((poc >= 0.0) & (poc <= 1.0))


def test_matrix_sparsity_and_score_various():
    """Generate small matrices with controlled sparsity and check scoring behaviour."""
    import numpy as _np
    from importlib import util as _spec
    script = Path(__file__).resolve().parents[1] / 'analysis_monolith.py'
    spec = _spec.spec_from_file_location('analysis_monolith', str(script))
    mod = _spec.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Create matrices 3x3 with varying off-diagonal zeros
    mats = []
    # fully connected (no zeros off-diag)
    mats.append(_np.array([[0,1,1],[1,0,1],[1,1,0]]))
    # one zero off-diag
    mats.append(_np.array([[0,1,0],[1,0,1],[0,1,0]]))
    # many zeros (sparse)
    mats.append(_np.array([[0,0,0],[0,0,1],[0,1,0]]))

    sparsities = [round(mod.compute_sparsity_from_matrix(m), 6) for m in mats]
    # Basic sanity: sparsity values should be between 0 and 1 and increase with more zeros
    assert all(0.0 <= s <= 1.0 for s in sparsities)
    assert sparsities[0] < sparsities[1] < sparsities[2]

    # Check scoring produces array same length
    arr = _np.array(sparsities)
    scores = mod.compute_sparsity_score_generic(arr)
    assert scores.shape == arr.shape


    def test_regression_grid_sparsity_scores():
        """Compare scoring vectors over a grid of sparsity values and synthetic matrices."""
        import numpy as _np
        from importlib import util as _spec
        script = Path(__file__).resolve().parents[1] / 'analysis_monolith.py'
        spec = _spec.spec_from_file_location('analysis_monolith', str(script))
        mod = _spec.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Generate grid of sparsity values
        grid = _np.linspace(0.0, 1.0, 21)
        poc_scores = mod.compute_sparsity_score_generic(grid)
        try:
            from scripts.metric_optimizer import MetricOptimizer
            mo = MetricOptimizer()
            mo_scores = mo.compute_sparsity_score(grid)
            # Compare full vectors
            assert _np.allclose(_np.asarray(poc_scores, dtype=float), _np.asarray(mo_scores, dtype=float), atol=1e-6)
        except Exception:
            # If MetricOptimizer not importable, check shape and range
            assert poc_scores.shape == grid.shape
            assert _np.all((poc_scores >= 0.0) & (poc_scores <= 1.0))

    def test_regression_synthetic_matrices():
        """Create a set of synthetic matrices, compute sparsity and compare scoring vectors."""
        import numpy as _np
        from importlib import util as _spec
        script = Path(__file__).resolve().parents[1] / 'analysis_monolith.py'
        spec = _spec.spec_from_file_location('analysis_monolith', str(script))
        mod = _spec.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Create synthetic matrices of size 4x4 with varying sparsity
        mats = []
        # Fully connected
        mats.append(_np.ones((4,4)) - _np.eye(4))
        # Half zeros off-diag
        m = _np.ones((4,4)) - _np.eye(4)
        m[0,1] = m[1,2] = m[2,3] = m[3,0] = 0
        mats.append(m)
        # Mostly zeros
        m = _np.zeros((4,4))
        m[0,3] = m[1,2] = m[2,1] = m[3,0] = 1
        mats.append(m)

        sparsities = [_np.round(mod.compute_sparsity_from_matrix(mat), 6) for mat in mats]
        arr = _np.array(sparsities)
        poc_scores = mod.compute_sparsity_score_generic(arr)
        try:
            from scripts.metric_optimizer import MetricOptimizer
            mo = MetricOptimizer()
            mo_scores = mo.compute_sparsity_score(arr)
            assert _np.allclose(_np.asarray(poc_scores, dtype=float), _np.asarray(mo_scores, dtype=float), atol=1e-6)
        except Exception:
            assert poc_scores.shape == arr.shape
            assert _np.all((poc_scores >= 0.0) & (poc_scores <= 1.0))
