"""Functions to test the echoSMs datastore API."""
import subprocess

import pytest
import requests

from echosms import DATASTORE_URI, plot_specimen


@pytest.fixture
def datastore_dir(pytestconfig):
    """Datastore code directory."""
    return pytestconfig.rootpath/'src'/'echosms'/'datastore'


@pytest.mark.internet
@pytest.mark.parametrize('script',
                        [('api_echosms_example.py'),
                         ('api_examples.py'),])
def test_api_scripts(datastore_dir, script):
    """Run a Python script.

    The script needs to use script dependencies to indicate which packages it
    requires. If the echosms package is used that need to be in the script
    dependencies too. Note that running this script uses the latest published
    echoSMs package, not the editable install on the testing server.
    """
    result = subprocess.run(['uv', 'run',
                            str(datastore_dir/script)],
                            capture_output=True, text=True, check=True)

    assert result.returncode == 0


@pytest.mark.internet
def test_validate_cmd(pytestconfig, datastore_dir):
    """Test the validate_toml command line program on the example toml files."""
    result = subprocess.run(['uv', 'run',
                str(datastore_dir/'validate_toml.py'),
                str(pytestconfig.rootpath/'data_store'/'resources/example*.toml')],
                capture_output=False, text=True, check=True)

    assert result.returncode == 0


@pytest.mark.internet
def test_api_plot(tmp_path):
    """Test calls to the datastore API."""
    # Get an outline shape from the echoSMs anatomical datastore
    baseURI = DATASTORE_URI
    # baseURI = 'http://127.0.0.1:8000/'

    r = requests.get(baseURI + 'v2/specimens?shape_type=outline', timeout=15)
    specimens = r.json()
    uuids = [s['uuid'] for s in specimens]

    for uuid in uuids:
        # Get the full specimen data (including the shape)
        r = requests.get(baseURI + 'v2/specimen/' + uuid + '/data', timeout=15)
        sp = r.json()
        assert 'shapes' in sp
        filename = tmp_path/(uuid + '.png')
        plot_specimen(sp, savefile=filename)
        assert filename.exists()


@pytest.mark.internet
def test_process_for_datastore(datastore_dir):
    """Test the process for datastore command line program starts."""
    result = subprocess.run(['uv', 'run',
                            str(datastore_dir/'process_for_datastore.py'),
                            '-h'],
                            capture_output=False, text=True, check=True)

    assert result.returncode == 0
