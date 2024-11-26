"""Functions to test that models check their input parameters."""
import pytest
import echosms
from echosms import ReferenceModels, BenchmarkData, theoretical_Sa


@pytest.fixture
def rm():
    """Provide a ReferenceModels instance."""
    return ReferenceModels()


@pytest.fixture
def bm():
    """Provide a BenchmarkData instance."""
    return BenchmarkData()


@pytest.fixture
def models():
    """All available models."""
    model_names = [d for d in dir(echosms) if d.endswith('Model')]

    models = []
    for m in model_names:
        models.append(getattr(echosms, m)())

    return models


# These are more playing around with tests than real or comprehensive...

def test_theoretical_sa():
    with pytest.raises(ValueError):
        theoretical_Sa(-45.0, 20.1, 10)
        theoretical_Sa(-45.0, -20.1, 0.0)


def test_test_instance(models):
    for m in models:
        assert isinstance(m.boundary_types, list)
        assert isinstance(m.shapes, list)
        assert isinstance(m.long_name, str)
        assert isinstance(m.short_name, str)
        assert isinstance(m.analytical_type, str)
        assert m.max_ka > 0.0


def test_reference_models(rm):
    assert len(rm.names()) > 0


def test_benchmark_data(bm):
    bmf = bm.freq_dataset
    bmt = bm.angle_dataset

    assert bmf.shape[0] > 0 and bmf.shape[1] > 0
    assert bmt.shape[0] > 0 and bmt.shape[1] > 0


def test_ts_results(rm):
    from echosms import MSSModel
    mod = MSSModel()
    m = rm.parameters('pressure release sphere')

    m['f'] = 38000
    assert mod.calculate_ts(m) == [-44.99786464477027]


def test_missing_parameter(rm):
    from echosms import MSSModel
    m = rm.parameters('pressure release sphere')

    mod = MSSModel()
    with pytest.raises(KeyError):
        mod.calculate_ts(m)


def test_negative_parameter(rm):
    from echosms import MSSModel
    m = rm.parameters('pressure release sphere')

    mod = MSSModel()
    m['f'] = [-10, 2, 3]
    with pytest.raises(ValueError):
        mod.calculate_ts(m)


def test_unsupported_boundary_type(rm):
    from echosms import MSSModel
    m = rm.parameters('pressure release sphere')

    mod = MSSModel()
    m['f'] = [2, 3]
    m['boundary_type'] = ['elastic']
    with pytest.raises(ValueError):
        mod.calculate_ts(m)
