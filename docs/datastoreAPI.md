# API

???+ Note

    This page contains the draft API specification and documentation for web access to the echoSMs anatomical data store. It is a work in progress.

The anatomical data store API is implemented as a RESTful web API with calls to:

1. Query dataset metadata
1. Obtain specimen information and model definitions and parameters.
1. Access the full dataset associated with a model (this includes the raw data, processing scripts, intermediate data, etc).

A testing server is available with some sample data, along with the API [documentation](https://echosms-data-store-app-ogogm.ondigitalocean.app/docs). Example Python code that demonstrates use of the API is available [here](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/src/api_examples.py). That code also includes an example of how to download all specimen data to a local file for offline access.

API endpoints to modify the data store have not yet been created as the data store can be manually loaded given the relatively low rate of expected model uploading.

Some example API calls are:

- A list of all [specimens](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens)
- A list of all [specimens](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens?dataset_id=CLAY_HORNE) in the CLAY_HORNE dataset
- A list of all specimens with a shape type of [outline](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens?shape_type=outline)
- A list of all specimens with genus of [Champsocephalus](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens?genus=Champsocephalus)
- All data from the [CLAY_HORNE_A](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/CLAY_HORNE_B/data) specimen and an [image](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/CLAY_HORNE_B/image) of that specimen
- A specimen with a shape type of [voxels](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/GJM001_5/image) (and the [metadata](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens?id=GJM001_5) about that specimen)
- A specimen with a shape type of [surface](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/GJM003_CBO_cbo12/image) (and the [metadata](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens?id=GJM003_CBO_cbo12))

The API call to get the full raw data is not yet implemented.
