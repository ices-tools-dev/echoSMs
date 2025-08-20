# Anatomical data store

???+ Note

    This page contains the draft specification and documentation for the echoSMs anatomical data store. It is a work in progress and no data store has been set up yet.

The echoSMs anatomical data store aims to:

1. Provide an accessible repository of anatomical fish and plankton data for use in acoustic scattering models
1. Facilitate standardisation of data formats and metadata relevant to acoustic scattering model inputs
1. Provide a web API for searching and accessing anatomical and model data
1. Provide a web-based user interface for browsing, searching, uploading, and downloading datasets

Objective 3 exists to facilitate access to datasets from scattering models running on cloud resources.

## Data store contents and structure

Each dataset comprises the following:

1. Metadata about a dataset
1. Input data to scattering models (one or more files that specify material properties, 3D shapes, and other model parameters)
1. Raw data files that were used to produce the scattering model input data (mostly binary files, such as x-ray and photographic images, MRI & CT scan files, etc)
1. Processing files (programs, notes, intermediate data files, etc)

Each dataset may contain information about more than one organism (e.g., multiple fish shapes were used in an analysis) but is restricted to a single species per dataset.

The dataset metadata and model data have prescribed formats and are structured for convenient access via a Web API, loading from formatted files, and inputting to scattering models. The raw data and processing file formats and layout are unconstrained and are accessible via a Web API as a zipped download and a browsable directory hierarchy.

Model outputs are not stored.

## Datasets for uploading

A dataset ready for uploading should contain the following files and directory structures, bundled into a single .zip file:

|Path|File(s)|Comment|
|----|-------|-------|
|/|metadata.toml|Dataset metadata in TOML format. This file can include specimen and model data. The file name must be metadata.toml|
|/|specimen*.toml|Specimen and model data in one or more TOML-formatted files. File names must start with ‘specimen’ and have a suffix of .toml. These files are simply appended to the metadata.toml file when reading the dataset data.|
|/data|Any|Raw and processing files in user-supplied directory hierarchy|

### Validation

The contents of a metadata.toml file can be validated using the data store schema. There are many online tools that can do this, and an offline version in Python will be provided (_to do_). It is also likely that it will be automatically validated when uploading a new data set.

## Data formats

### Dataset and model data

The dataset metadata and model data structures have been designed as a hierarchical structure of key-value pairs that can be realised in many commonly used data file formats, including TOML, XML, YAML, JSON, HDF5, netCDF4, and Zarr. The data structures are also designed to be simple to instantiate in the programming languages that are commonly used for acoustic scattering models (e.g., Julia, Matlab, Python, and R).

The dataset metadata requires information about the species, the collection and processing of specimens used in scattering models, links to published work, and other context. These are intended to provide information for users to assess the quality, usability, and suitability of a particular dataset for scattering models.

Associated with each dataset are one or more specimen datasets. These contain basic information about the specimen(s) (e.g., length and weight), along with the three-dimensional shape information required by acoustic scattering models.

The type of shape data required by a scattering model falls into three main types: a three-dimensional triangulated closed surface, dorsal and ventral outlines, and a rectangular three-dimensional grid of voxels (see table below). The model data structure provides the means to store each of these. Some models have multiple shapes for a single specimen (e.g., a fish body and swimbladder) and this is achieved with multiple instances of the shape attributes per specimen.

The structure and attributes required for the dataset metadata and model data are recorded as a [JSON schema](https://json-schema.org/) that is stored in the echoSMs [github repository](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/schema/v1/anatomical_data_store.json). The schema documents the required attributes, their structure, valid values, and is rendered into the echoSMs [documentation](schema/data_store_schema.md). The schema can also used to validate incoming datasets.

|Shape data name|Realisation|Models that use this|Notes|
|---------------|-----------|--------------------|-----|
|surface|3D triangular surface mesh|BEM, KA|ρ and c per shape|
|voxels|3D rectangular grid with material properties for each voxel|PT-DWBA, FEM|ρ and c for each voxel|
|outline|Dorsal and ventral outlines (widths and heights) along a curved centreline|KRM, DWBA, DCM|ρ and c per shape (KRM) or per section (DWBA)|

Specialisations of the `outline` shape are:

- KRM: non-circular cross-sections along a straight centreline
- DWBA: circular cross-sections along a curved centreline
- DCM: circular cross-sections along a straight or curved centreline

### Shape data structure

The format of model shape data is specified in the echoSMs anatomical data store schema, but some additional explanatory notes and examples are provided here (_to do_). Code is also provided in the echoSMs python package to make it easy to convert data to the schema format (_to do_).

### Raw files

Raw data formats are not directly used by scattering models so do not need to be formatted for direct use in scattering models. Raw data typically includes images (e.g., png, tiff, jpg), imaging system files (e.g., CT, MRI, and x-ray – typically DICOM or sets of 2D images), and other more ad-hoc data (e.g., spreadsheets). Text-based formats are preferred for their long-term usability, but well-defined and accessible binary formats are acceptable (e.g., common image formats and DICOM)

### Processing files

A preference for text file formats, then common binary formats (e.g, for images), then other binary formats with documentation. The aim here is to make the information readily accessible in the future without the use of specialised software.
