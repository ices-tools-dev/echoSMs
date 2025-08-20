# Data store API documentation and examples

Some quick links help on using the echoSMs data store web API.

Need to start the web server first:

    cd echoSMs/data_store/src
    fastapi dev echosms_webapi.py

## API documentation

Live [docs](http://127.0.0.1:8000/docs)

Live [docs](http://127.0.0.1:8000/redoc) in a different format

Live [openAPI JSON file](http://127.0.0.1:8000/openapi.json)

## Datasets

[All datasets](http://127.0.0.1:8000/v1/datasets)

[Datasets with species name of Gadus morhua](http://127.0.0.1:8000/v1/datasets?species=Gadus%20morhua)

[Datasets with species name of Pleuragramma antarcticum](http://127.0.0.1:8000/v1/datasets?species=Pleuragramma%20antarcticum)

[Metadata and shape data for dataset_id = CLAY_HORNE](http://127.0.0.1:8000/v1/dataset/CLAY_HORNE)

[Full raw data with dataset_id = CLAY_HORNE](http://127.0.0.1:8000/v1/dataset/CLAY_HORNE?full_data=true)

[Specimen B data from CLAY_HORNE dataset](http://127.0.0.1:8000/v1/specimen/CLAY_HORNE/B)

[Plot of specimen D from CLAY_HORNE dataset](http://127.0.0.1:8000/v1/specimen_image/CLAY_HORNE/D)