"""Functions to test the echoSMs datastore API."""
import pytest
import requests
from echosms import plot_specimen
from matplotlib import pyplot as plt

def test_api_plot(tmp_path):
    """Test calls to the datastore API"""
    # Get an outline shape from the echoSMs anatomical datastore
    baseURI = 'https://echosms-data-store-app-ogogm.ondigitalocean.app/'
    baseURI = 'http://127.0.0.1:8000/'

    r = requests.get(baseURI + 'v2/specimens?shape_type=outline')
    specimens = r.json()
    uuids = [s['uuid'] for s in specimens]
    
    for uuid in uuids:
        # Get the full specimen data (including the shape)
        r = requests.get(baseURI + 'v2/specimen/' + uuid + '/data')
        sp = r.json()
        filename = tmp_path/(uuid + '.png')
        plot_specimen(sp, savefile=filename)
        assert filename.exists()
