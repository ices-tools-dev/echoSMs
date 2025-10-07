# API

???+ Note

    This page contains the draft API specification and documentation for web access to the echoSMs anatomical data store. It is a work in progress.

The anatomical data store API is implemented as a RESTful web API with calls to:

1. Query dataset metadata
1. Obtain specimen information and model definitions and parameters.
1. Access the full dataset associated with a model (this includes the raw data, processing scripts, intermediate data, etc).

A testing server is available with some sample data, along with the API [documentation](https://echosms-data-store-app-ogogm.ondigitalocean.app/docs). Example Python code that demonstrates use of the API is available [here](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/src/api_examples.py). That code also includes an example of how to download all specimen data to a local file for offline access.

Two versions of the API are provided. V1 provides data in a dataset structure, where one dataset contains multiple specimens. V2 provides a flattened view of this, where there are only specimens. It is not yet clear which way is preferred so, for testing, both are provided. API endpoints to modify the data store have not yet been created as the data store can be manually loaded given the relatively low rate of expected model uploading.

Some example API calls are:

- For the V1 API:

    - A list of all [dataset ids](https://echosms-data-store-app-ogogm.ondigitalocean.app/v1/datasets) in the testing server
    - A [dataset](https://echosms-data-store-app-ogogm.ondigitalocean.app/v1/dataset/CLAY_HORNE)
    - Shape data from a [specimen](https://echosms-data-store-app-ogogm.ondigitalocean.app/v1/specimen/CLAY_HORNE/B) in a dataset and an [image](https://echosms-data-store-app-ogogm.ondigitalocean.app/v1/specimen_image/CLAY_HORNE/B) of that specimen
    - The API call to provide the [raw](https://echosms-data-store-app-ogogm.ondigitalocean.app/v1/dataset/CLAY_HORNE?full_data=true) dataset is there, but currently doesn't return any raw data

- For the V2 API:

    - A list of all [specimens](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens)
    - A list of all [specimens](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens?dataset_id=CLAY_HORNE) in the CLAY_HORNE dataset
    - A list of all specimens with a shape type of [outline](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens?shape_type=outline)
    - A list of all specimens with genus of [Champsocephalus](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens?genus=Champsocephalus)
    - Shape data from the [CLAY_HORNE_A](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/CLAY_HORNE_B/shape) specimen and an [image](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/CLAY_HORNE_B/image) of that specimen

