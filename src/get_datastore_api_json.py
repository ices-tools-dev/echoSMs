"""Get the data store openAPI .json file."""

import json
from pathlib import Path
import requests


def on_pre_build(config):
    """Get datastore API in openAPI JSON format.

    This function is called when mkdocs runs and gets the echoSMs anatomical
    web API in openAPI JSON format from a running instance of FastAPI

    An extension in mkdocs then uses the json file to provide API docs in the
    echoSMs documentation pages.
    """
    # This URL requires that FASTapi be available on the local machine when the docs are built
    url = 'http://127.0.0.1:8000/openapi.json'

    try:
        r = requests.get(url)

        if r.status_code == 200:
            with open(Path(config["docs_dir"])/'datastore_api_openapi.json', 'w') as file:
                print('== Generating openAPI JSON file (from FastAPI) ==')
                json.dump(r.json(), file, indent=2)
        else:
            print('== Failed to get openAPI.json file, using existing ==')
    except requests.exceptions.ConnectionError:
        print('== Failed to connect to server. openAPI.json not updated ==')
