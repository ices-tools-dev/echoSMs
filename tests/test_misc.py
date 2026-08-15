"""Functions to test that models check their input parameters."""
import pandas as pd
import pytest

import echosms
from echosms import BenchmarkData, ReferenceModels, theoretical_Sa


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


def test_test_instance(models):
    """Test that all models have the required instance variables."""
    for m in models:
        assert isinstance(m.long_name, str)
        assert isinstance(m.short_name, str)
        assert isinstance(m.analytical_type, str)
        assert isinstance(m.boundary_types, list)
        assert isinstance(m.shapes, list)
        assert m.max_ka > 0.0


def test_reference_names(rm):
    """Test aspects of the reference model API."""
    assert len(rm.names()) > 0

    assert rm.specification('an invalid model name') == {}
    assert rm.parameters('an invalid model name') == {}


def test_benchmark_data(bm):
    """Test that benchmarkdata are present."""
    assert len(bm.freq_names()) > 0
    assert len(bm.angle_names()) > 0


def test_benchmark_freq(bm):
    """Test that frequency data are available from the benchmark class."""
    name = bm.freq_names()[0]
    f, ts = bm.freq_data(name)
    assert len(f) > 0
    assert len(f) == len(ts)

    with pytest.raises(ValueError):
        bm.freq_data('not a benchmark name')


def test_benchmark_angle(bm):
    """Test that angle data are available from the benchmark class."""
    name = bm.angle_names()[0]
    angle, ts = bm.angle_data(name)
    assert len(angle) > 0
    assert len(angle) == len(ts)

    with pytest.raises(ValueError):
        bm.angle_data('not a benchmark name')


def test_benchmark_return_dataframe(bm):
    """Test that the benchmark returns dataframes."""
    assert isinstance(bm.angle_as_dataframe(), pd.DataFrame)
    assert isinstance(bm.freq_as_dataframe(), pd.DataFrame)
