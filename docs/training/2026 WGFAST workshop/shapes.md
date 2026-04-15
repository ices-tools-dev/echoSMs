### Introduction

The datastore is an online store of scattering model shapes, metadata, and raw data. Access is via a simple RESTful web API and we have developed a prototype for testing, but the intention is for to ICES to eventually host and manage it.

Input data to the datastore are TOML- or JSON-formatted text files containing the shapes and metadata, and miscellaneous other files (e.g., raw images). The datastore schema:

- Specifies the data format (required attributes, data, units, valid values, etc)
- Is the authoritative source of the data format
- Is used to validate data files before the datastore will accept them
- Is implemented as a [JSON Schema](https://json-schema.org/)

The data format has been designed to be easy to work with (supported by multiple programming languages, text-based, readable by people) and general enough to store all types of shapes used in fish and plankton scattering models.

### Data format

A **specimen** contains one or more **shapes**, representing parts of the specimen (e.g., body, swimbladder, backbone, etc), and metadata about the specimen. A **dataset** can be used to group specimens.

There are different shape types:

- **outline** - dorsal and lateral outlines
- **surface** - 3D triangulated surface mesh
- **voxels** - 3D grid of density and sound speed values
- **categorised voxels** - 3D grid of categorised material properties
- **geometric** - combination of simple shapes (cylinders, spheroids)

In the data format, each shape type has data attributes for storing the shape (documentation [here](https://ices-tools-dev.github.io/echoSMs/datastore_anatomical/#shapes)). Unit and coordinate systems are the same as in [echoSMs](https://ices-tools-dev.github.io/echoSMs/conventions/).

- The schema is kept in the echoSMs [github repository](https://github.com/ices-tools-dev/echoSMs/tree/main/data_store/schema/v1)
- The direct URL to the schema is <https://raw.githubusercontent.com/ices-tools-dev/echoSMs/refs/heads/main/data_store/schema/v1/anatomical_data_store.json>
- The direct URL can be used in some online JSON schema viewers (e.g., [json-schema](https://json-schema.app/start) and [jsoncrack](https://jsoncrack.com/editor)) and validators (see below)
- A more readable version is in the echoSMs [documentation](https://ices-tools-dev.github.io/echoSMs/schema/data_store_schema/).
- An example of a TOML input file is [here](XXXXXXXXXX)

### Creating input files

Input files can be created by hand, but this quickly becomes tedious, especially for the shape data itself. Using a script to create the TOML files is likely better.

A notebook demonstrating how to create a input data file is [here](XXXXXXXXXXXXXXx). Further instructions are in the echoSMs [documentation](https://ices-tools-dev.github.io/echoSMs/datastore_anatomical/#preparing-datasets-for-the-datastore).

The `validating a TOML datastore file.ipynb` notebook demonstrates how to use the Python jsonschema-rs package to validate a TOML file. The R [jsonvalidate](https://cran.r-project.org/web/packages/jsonvalidate/vignettes/jsonvalidate.html) and [rjsoncons](https://cran.r-project.org/web/packages/rjsoncons/index.html) packages can be used from R.

Currently, there is no automated way to load an input file to the datastore (it's a manual process that Gavin does).

??? "Using a local version of the datastore"

    Your online computer is running a local version of the datastore and you can load an input file to that. Instructions for that are here XXXXX.


### Getting shapes

This is done with the RESTful web API. This a deliberately simple API that will fit many (but not all) uses.

Documentation on the API is [here](https://echosms-data-store-app-ogogm.ondigitalocean.app/docs).

There are API calls to:

- retrieve specimen metadata (excluding the shape data) with filtering on some metadata attributes
- retrieve data for a specific specimen (shape data and metadata)
- retrieve an image of the shape data for a specific specimen

API calls can be tested in a web browser. For example:

- All specimens: <https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens>
- All specimens with `imaging_method` set to `radiograph`: <https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimens?imaging_method=radiograph>
- All data for a specimen with a specific `uuid`: <https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/48d60557-f9d5-4bb3-a977-00d8db818a56/data>
- An image of the shape for a specific specimen: <https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/48d60557-f9d5-4bb3-a977-00d8db818a56/image>

The `simple echoSMs datastore demo.ipynb` notebook shows more details on using web API.
