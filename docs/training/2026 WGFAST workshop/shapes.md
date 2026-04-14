### Introduction

- The datastore is an online place to store and access scattering model shapes, metadata, and raw data
- Access is via a simple RESTful web  API - documentation is [here](https://echosms-data-store-app-ogogm.ondigitalocean.app/docs)
- Intention is for to ICES to eventually host and manage it
- Input data to the datastore are TOML-formatted files containing data and metadata and miscellaneous other files (e.g., raw images)
- The TOML files are validated against a schema before the datastore will accept them

### Schema

The schema:

- specifies the data format (required data, units, valid values, etc)
- is used as the authoritative source of the data format
- is used to check that data files follow the data format
- is implemented as a [JSON Schema](https://json-schema.org/)

The data format has been designed to be:

- easy to understand text files,
- general enough to store all types of shapes used in scattering models.

### Data format

A **specimen** contains one or more **shapes**, representing parts of the specimen (e.g., body, swimbladder, backbone, etc), and metadata about the specimen. A **dataset** can be used to group specimens.

There are different types of shape:

- **outline** - dorsal and lateral outlines
- **surface** - 3D triangulated surface mesh
- **voxels** - 3D grid of density and sound speed values
- **categorised voxels** - 3D grid of categorised material properties
- **geometric** - combinations of simple shapes (cylinders, spheroids)

Each shape type has relevant data attributes for storing the shape (documentation [here](https://ices-tools-dev.github.io/echoSMs/datastore_anatomical/#shapes)). Unit and coordinate systems are the same as in [echoSMs](https://ices-tools-dev.github.io/echoSMs/conventions/).

- The schema is kept in the echoSMs [github repository](https://github.com/ices-tools-dev/echoSMs/tree/main/data_store/schema/v1)
- The direct URL to the schema is <https://raw.githubusercontent.com/ices-tools-dev/echoSMs/refs/heads/main/data_store/schema/v1/anatomical_data_store.json>
- The direct URL can be used in some online JSON schema viewers (e.g., [json-schema](https://json-schema.app/start) and [jsoncrack](https://jsoncrack.com/editor)) and validators (see below)
- A more readable version of the schema is in the echoSMs [documentation](https://ices-tools-dev.github.io/echoSMs/schema/data_store_schema/).

### Creating specimen files

In the prototype datastore, datasets are formatted as per the schema and then arranged in a set of directories. This is explained [here](https://ices-tools-dev.github.io/echoSMs/datastore_anatomical/#preparing-datasets-for-the-datastore).

### Validating specimen files

There are many existing tools that will check that a given file meets the requirements given in a JSON schema. Some online tools are:

- https://www.jsonschemavalidator.net/
- https://jsonschema.dev/
- https://mockoon.com/tools/json-schema-validator/

Some Python validation packages are:

- [JSONschema](https://github.com/python-jsonschema/jsonschema)
- [jsonschema-rs](https://pypi.org/project/jsonschema-rs/)

Some R validation libraries are:

- [jsonvalidate](https://cran.r-project.org/web/packages/jsonvalidate/vignettes/jsonvalidate.html)
- [rjsoncons](https://cran.r-project.org/web/packages/rjsoncons/index.html)

The `validating a TOML datastore file.ipynb` notebook demonstrates how to use the Python jsonschema-rs package to validate a TOML file.

### Retrieving datastore data

This is the RESTful web API. The current access methods will fit many (but not all) uses. Feedback on the usability of the access methods is welcome.

Open the `simple echoSMs datastore demo.ipynb` notebook for a demonstration of the web API.
