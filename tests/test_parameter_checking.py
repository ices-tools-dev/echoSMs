"""Functions to test that models check their input parameters."""
import pytest
import echosms
import numpy as np
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


# Test that models raise an error if an input parameter is missing
def test_missing_parameter(rm):
    from echosms import MSSModel
    m = rm.parameters('pressure release sphere')

    mod = MSSModel()
    with pytest.raises(KeyError):
        mod.calculate_ts(m)

# Test that models raise an error when input parameters are out of valid ranges
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
