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



def test_theoretical_Sa():
    with pytest.raises(ValueError):
        theoretical_Sa(ts=-45.0, eba=20.1, r=10)
        theoretical_Sa(ts=-45.0, eba=-20.1, r=0.0)


# Test that all models have the required instance variables.
def test_test_instance(models):
    for m in models:
        assert isinstance(m.long_name, str)
        assert isinstance(m.short_name, str)
        assert isinstance(m.analytical_type, str)
        assert isinstance(m.boundary_types, list)
        assert isinstance(m.shapes, list)
        assert m.max_ka > 0.0


# Test that reference model data is present.
def test_reference_models(rm):
    assert len(rm.names()) > 0


# Test that benchmarkdata are present
def test_benchmark_data(bm):

    assert len(bm.freq_names()) > 0
    assert len(bm.angle_names()) > 0

