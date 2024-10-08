"""

"""
import pytest
from echosms import MSSModel, ReferenceModels, BenchmarkData


@pytest.fixture
def rm():
    """Provide a ReferenceModels instance."""
    return ReferenceModels()


@pytest.fixture
def bm():
    """Provide a BenchmarkData instance."""
    return BenchmarkData()


models = [d for d in dir(echosms) if d.endswith('Model')]

def test_reference_models(rm):
    assert len(rm.names()) > 0


#####################################################################
# Test the parameter validation that each model should have implemented.

def test_benchmark_data(bm):
    bmf = bm.freq_dataset
    bmt = bm.angle_dataset

    assert bmf.shape[0] > 0 and bmf.shape[1] > 0
    assert bmt.shape[0] > 0 and bmt.shape[1] > 0


def test_function(rm):
    m = rm.parameters('pressure release sphere')

    m['f'] = 38000
    mod = MSSModel()
    assert mod.calculate_ts(m) == [-44.99786464477027]


def test_missing_parameter(rm):
    m = rm.parameters('pressure release sphere')

    mod = MSSModel()
    with pytest.raises(KeyError):
        mod.calculate_ts(m)


def test_negative_parameter(rm):
    m = rm.parameters('pressure release sphere')

    mod = MSSModel()
    m['f'] = [-10, 2, 3]
    with pytest.raises(ValueError):
        mod.calculate_ts(m)


def test_unsupported_boundary_type(rm):
    m = rm.parameters('pressure release sphere')

    mod = MSSModel()
    m['f'] = [2, 3]
    m['boundary_type'] = ['elastic']
    with pytest.raises(ValueError):
        mod.calculate_ts(m)

#############################
# Test TS results from models
