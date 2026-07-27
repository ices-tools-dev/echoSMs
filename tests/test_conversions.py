"""Functions to test the functions in the conversions.py file."""
import pytest
from pathlib import Path
import echosms
import tomllib

@pytest.fixture
def datastore_dir(pytestconfig) -> Path:
    """Shape example directory."""
    return pytestconfig.rootpath/'data_store'/'resources'


def test_krmorganism_from_datastore(datastore_dir):

    with Path.open(datastore_dir/'example_metadata A.toml', 'rb') as f:
        organism = tomllib.load(f)

    shapes = organism['shapes']
    krm = echosms.krmorganism_from_datastore(shapes = shapes)

    assert krm.body.boundary == 'fluid-filled'
    assert len(krm.inclusions) == 1
