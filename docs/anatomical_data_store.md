# Anatomical data store

???+ Note

    This page contains the draft specification and documentation for the echoSMs anatomical data store. It is a work in progress.

The echoSMs anatomical data store aims to:

1. Provide an accessible repository of anatomical fish and plankton data for use in acoustic scattering models
1. Facilitate standardisation of data formats and metadata relevant to acoustic scattering model inputs
1. Provide a web API for searching and accessing anatomical and model data
1. Provide a web-based user interface for browsing, searching, uploading, and downloading datasets

Objective 3 exists to facilitate access to datasets from scattering models running on cloud resources.

## Data store contents and structure

The data store will contain many datasets, where each dataset comprises the following:

1. Metadata about a dataset
1. Input data to scattering models (material properties, 3D shapes, and other model parameters)
1. Optionally, raw data files that were used to produce the scattering model input data (mostly binary files, such as x-ray and photographic images, MRI & CT scan files, etc)
1. Optionally, processing files (programs, notes, intermediate data files, etc)

Each dataset may contain information about more than one organism (e.g., multiple fish shapes were used in an analysis) but is restricted to a single species per dataset.

The dataset metadata and model data have prescribed formats and are structured for convenient access via a [RESTful](https://en.wikipedia.org/wiki/REST) API, loading from formatted files, and inputting to scattering models. The raw data and processing file formats and layout are unconstrained and are accessible via the RESTful API as a zipped download and a browsable directory hierarchy.

Model outputs are not stored.

## Datasets for uploading

A dataset ready for uploading should contain the following files and directory structures, bundled into a single .zip file:

|Path|File(s)|Comment|
|----|-------|-------|
|/|metadata.toml|Dataset metadata in TOML format. This file can include specimen and model data. The file name must be `metadata.toml`|
|/|specimen*.toml|Specimen and model data in one or more TOML-formatted files. File names must start with `specimen` and have a suffix of `.toml`. These files are simply appended to the metadata.toml file when reading the dataset data.|
|/data|Any|Raw and processing files in user-supplied directory hierarchy|

## Data formats

### Dataset and model data

The dataset metadata and model data structures have been designed as a hierarchical structure of key-value pairs that can be realised in many commonly used data file formats, including TOML, XML, YAML, JSON, HDF5, netCDF4, and Zarr. The data structures are also designed to be simple to instantiate in the programming languages that are commonly used for acoustic scattering models (e.g., Julia, Matlab, Python, and R).

The dataset metadata requires information about the species, the collection and processing of specimens used in scattering models, links to published work, and other context. These are intended to provide information for users to assess the quality, usability, and suitability of a particular dataset.

Associated with each dataset are data about one or more specimens. This includes basic information about the specimen(s) (e.g., length and weight), along with the three-dimensional shape information required by acoustic scattering models. A specimen is not necessarily a whole organism - the data structure allows for a specimen to be some part of the organism (e.g., swimbladder, organs, etc)

The type of shape data required by a scattering model falls into three main types: a three-dimensional triangulated closed surface, dorsal and ventral outlines, and a rectangular three-dimensional grid of voxels (see table below). The model data structure provides the means to store each of these. Some models have multiple shapes for a single specimen (e.g., a fish body and swimbladder) and this is achieved with multiple shapes per specimen. Additional shape formats can be added as required (e.g., 3D shapes defined by tetrahedrons, as used by the [TetraScatt](https://doi.org/10.1115/1.4067286) scattering model).

The structure and attributes required for the dataset metadata and model data are recorded as a [JSON schema](https://json-schema.org/) that is stored in the echoSMs [github repository](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/schema/v1/anatomical_data_store.json). The schema documents the required attributes, their structure, valid values, and is rendered into the echoSMs [documentation](schema/data_store_schema.md). To make the schema more concrete, several examples are available [here](). The schema can also used to programmatically validate incoming datasets.

|Shape data type|Realisation|Models that use this|Notes|
|---------------|-----------|--------------------|-----|
|surface|3D triangular surface mesh|BEM, KA|ρ and c per shape|
|outline|Dorsal and ventral outlines (widths and heights) along a curved centreline|KRM, DWBA, DCM|ρ and c per shape (KRM) or per section (DWBA)|
|voxels|3D rectangular grid with material properties for each voxel|FEM|ρ and c for each voxel|
|categorised voxels|3D rectangular grid with a material property category for each voxel|PT-DWBA|There is a ρ and c for each category|

Specialisations of the outline shape are:

- KRM: non-circular cross-sections along a straight centreline
- DWBA: circular cross-sections along a curved centreline
- DCM: circular cross-sections along a straight or curved centreline

### Shape data structure

The format of model shape data is specified in the echoSMs anatomical data store schema, but some additional explanatory notes and examples are provided here. Code is also provided in the echoSMs python package to make it easy to convert data to the schema format.

#### Surface

The `surface` format stores a 3D triangular surface mesh. The mesh is represented with three numeric arrays (`x`, `y`, and `z`) for the x, y, and z coordinates of the surface nodes, three integer arrays (`facets_0`, `facets_1`, `facets_2`) that index into the x, y, and z arrays and specify which nodes form individual triangles, and three arrays that give the outward normal vector for each triangle (`normals_x`, `normals_y`, and `normals_z`). The lengths of the facets and normals arrays must all be the same.

!!! note
    Some scattering models require a closed 3D surface mesh (i.e., without holes), but the `surface` format does not require this.

EchoSMs provides a function, [surface_from_stl()][echosms.surface_from_stl], to convert an .stl file into the surface shape format. This function can be used like this:

```py
from echosms import surface_from_stl

# Load the surface shape from an .stl file. The named parameters are optional.
shape = surface_from_stl('A.stl', dim_scale=1e-3, name='body', boundary='soft')
```
This shape can then be combined with the specimen metadata and written to a TOML file ready for 
loading to the echoSMs datastore:

```py
import tomli_w
# Create specimen metadata and add in the shape
specimens = {'specimens': 
                [{'specimen_id': 'A',
                  'specimen_condition': 'unknown',
                  'length': 0.0,
                  'weight': 0.0,
                  'sex': 'unknown',
                  'length_type': 'unknown',
                  'shape_type': 'surface',
                  'shapes': [shape]}]}

# Write to a TOML file
with open('specimen_A.toml', 'wb') as f:
    tomli_w.dump(specimens, f)
```

There is complimentary function to `surface_from_stl()` that takes the echoSMs data store form of a surface shape and returns the mesh as a trimesh object (see [mesh_from_datastore()][echosms.mesh_from_datastore]).

#### Outline

The `outline` format is a generalised structure that can represent the outline shapes typically used for the DWBA, KRM, and DCM models. It uses a centreline (defined by a series of x, y, and z points) and a height and width for each centreline point. The [echoSMs coordinate system][] is used so heights are along the _z_-axis and widths along the _y_-axis. Five numeric arrays are used to represent the shape in the echSMs format with names of `x`, `y`, `z`, `height`, and `width`. The lengths of these arrays must all be the same.

EchoSMs provides functions to convert to and from the outline format into the specific formats typically required by the DWBA, KRM, and DCM models - see the examples below.

Historically, outline shapes used in the KRM model used a straight centreline along the _x_-axis (with _y_ = _z_ = 0), non-symmetric heights (i.e., lower and upper heights measured from the centreline) and symmetric widths. This form of shape can be converted to the echoSMs via:

```py
from echosms import outline_from_krm

# Make up a shape in the KRM style
x = []
height_u = []
height_l = []
width = []

shape = outline_from_krm(x, height_u, height_l, width, name='body', boundary='soft')
```

As per the surface example above, this can then be combined with specimen metadata and written to a TOML file.

In contrast, DBWA model implementations tend to use a centreline that is curved in the _y_-axis and circular cross-sections:

```py
from echosms import outline_from_dwba

# Make up a shape in the DWBA style
x = []
y = []  # in the echoSMs coordinate system, this is the negative z-axis
radius = []

shape = outline_from_dwba(x, y, radius, width, name='body', boundary='soft')
```

#### Voxels

The `voxels` format contains two 3D matrices, one for density and one for sound speed. The echoSMs representation of a 3D matrix is a doubly-nested list. Conversion between a Python numpy (or xarray) 3D matrix and the echoSMs structure is done as follows:

_not yet done_

#### Categorised voxels

The `categorised voxels` format uses a single 3D matrix of material property categories (named `categories` in the schema) - for echoSMs these categories must be integers starting at 0. The categories define regions of differing material properties in the specimen. The category value is used as a zero-based index into the associated `mass_density` and `sounds_speed_compressional` vectors. Hence, the length of the density and sound speed arrays must be at least one more than the highest category number in `categories`.

Example code that converts from a Python numpy (or xarray) 3D matrix of categories into the echoSMs format is a follows:

_not yet done_

### Raw files

Raw data formats are not directly used by scattering models so do not need to be formatted for direct use in scattering models. Raw data typically includes images (e.g., png, tiff, jpg), imaging system files (e.g., CT, MRI, and x-ray – typically DICOM or sets of 2D images), and other more ad-hoc data (e.g., spreadsheets). Text-based file formats are preferred for their long-term usability, but well-defined and accessible binary formats are acceptable (e.g., common image formats and DICOM).

### Processing files

A preference for text file formats, then common binary formats (e.g, for images), then other binary formats with documentation. The aim here is to make the information readily accessible in the future without the use of specialised software.
