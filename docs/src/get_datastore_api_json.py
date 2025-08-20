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

    r = requests.get(url)

    # If the requests.get call fails, this will silently fail and fall over to the existing
    # .json file in the docs_dir.

    if r.status_code == 200:
        with open(Path(config["docs_dir"])/'datastore_api_openapi.json', 'w') as file:
            json.dump(r.json(), file, indent=2)
