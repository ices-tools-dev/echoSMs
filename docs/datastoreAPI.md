# API

???+ Note

    This page contains the draft API specification and documentation for web access to the echoSMs anatomical data store. It is a work in progress and no web access data store has been set up yet.

The data store API is implemented as a RESTful web API with calls to:

1. Query dataset metadata
1. Obtain specimen information and model definitions and parameters.
1. Access the full dataset associated with a model (this includes the raw data, processing scripts, intermediate data, etc).

API endpoints to modify the data store have not yet been created as the data store can be manually loaded given the relatively low rate of expected model uploading.



!!swagger datastore_api_openapi.json!!
