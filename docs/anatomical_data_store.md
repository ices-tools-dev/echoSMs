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

Each dataset may contain information about more than one organism (e.g., multiple fish shapes were used in an analysis) but is restricted to a single species per dataset. For ease of use, output from the datastore is a flattened version of the input - the grouping of organisms into datasets is removed (although this can be easily reconstructed if needed).

The dataset metadata and model data have prescribed formats and are structured for convenient access via a [RESTful](https://en.wikipedia.org/wiki/REST) API, loading from formatted files, and inputting to scattering models.

The raw data and processing file formats and layout are unconstrained and are accessible via the RESTful API as a zipped download and a browsable directory hierarchy.

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

The dataset metadata and specimen data structures have been designed as a hierarchical structure of key-value pairs that can be realised in many commonly used data file formats, including TOML, XML, YAML, JSON, HDF5, netCDF4, and Zarr. The data structures are also designed to be simple to instantiate in the programming languages that are commonly used for acoustic scattering models (e.g., Julia, Matlab, Python, and R).

The dataset data format is specified by a [JSON schema](https://json-schema.org/) file stored in the echoSMs [github repository](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/schema/v1/anatomical_data_store.json). The schema documents the required attributes, their structure, valid values, etc, and is included in the echoSMs [documentation](schema/data_store_schema.md). The schema is a very technical document and is perhaps more easily understood via the examples [here](https://github.com/ices-tools-dev/echoSMs/tree/main/data_store/resources). The schema can also used to programmatically validate incoming datasets.

The dataset metadata requires information about the species, the collection and processing of specimens used in scattering models, links to published work, and other context. These are intended to provide information for users to assess the quality, usability, and suitability of a particular dataset.

Associated with each dataset are data about one or more specimens. This includes basic information about the specimen(s) (e.g., length and weight), along with the three-dimensional shape information required by acoustic scattering models. A specimen is not necessarily a whole organism - the data structure allows for a specimen to be some part of the organism (e.g., swimbladder, organs, etc)

Most anatomical scattering models use one of these three-dimensional representations:

- 3D triangulated surface meshes,
- dorsal and ventral outlines,
- 3D grids of cuboids (voxels).

The echoSMs data structure provides the means to store each of these (see table below). Some models can use multiple shapes for a single specimen (e.g., a fish body and swimbladder) and this is achieved with multiple shapes per specimen. Additional shape formats can be added as required (e.g., 3D shapes defined by tetrahedrons, as used by the [TetraScatt](https://doi.org/10.1115/1.4067286) scattering model).

|Shape data type|Realisation|Models that use this|Notes|
|---------------|-----------|--------------------|-----|
|surface|3D triangular surface mesh|BEM, KA|ρ and c per shape|
|outline|Dorsal and ventral outlines (widths and heights) along a curved centreline|KRM, DWBA, DCM|ρ and c per shape (KRM) or per section (DWBA)|
|voxels|3D rectangular grid with material properties for each voxel|FEM|ρ and c for each voxel|
|categorised voxels|3D rectangular grid with a material property category for each voxel|PT-DWBA|ρ and c for each category|

The outline shape is a generalised form of the shape definition used for several models:

- KRM: non-circular cross-sections along a straight centreline
- DWBA: circular cross-sections along a curved centreline
- DCM: circular cross-sections along a straight or curved centreline

### Shape data structure

The shape data format is formally specified in the echoSMs anatomical data store schema, but some additional explanatory notes, utility code, and examples are provided here.

#### Surface

The `surface` format stores a 3D triangular surface mesh. The mesh is represented with three numeric arrays (`x`, `y`, and `z`) for the x, y, and z coordinates of the surface nodes, three integer arrays (`facets_0`, `facets_1`, `facets_2`) that index into the x, y, and z arrays and specify the nodes that make up individual triangles, and three arrays that give the outward unit normal vector for each triangle (`normals_x`, `normals_y`, and `normals_z`). The lengths of the facets and normals arrays must all be the same.

!!! note
    Some scattering models require a closed 3D surface mesh (i.e., without holes), but the `surface` format does not enforce this.

EchoSMs provides a function, [surface_from_stl()][echosms.surface_from_stl], to convert an [STL](https://en.wikipedia.org/wiki/STL_(file_format)) file into the echoSMs surface shape format:

```py
from echosms import surface_from_stl

shape = surface_from_stl('A.stl', dim_scale=1e-3, name='body', boundary='soft')
```

This shape can then be combined with specimen metadata and written to a TOML file ready for loading into the echoSMs datastore:

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

There is complimentary function to `surface_from_stl()` that takes the echoSMs datastore surface format and returns a [trimesh](https://trimesh.org/) object (see [mesh_from_datastore()][echosms.mesh_from_datastore]), from which an STL file can be written.

#### Outline

The `outline` format is a generalised structure that can represent the outline shapes typically used for the DWBA, KRM, and DCM models. It uses a centreline (defined by a list of (_x_, _y_, _z_) coordinates) and a height and width at each centreline point. The [echoSMs coordinate system][coordinate-systems] is used so heights are along the _z_-axis and widths along the _y_-axis. Five numeric arrays are used to represent the shape in the echSMs format with names of `x`, `y`, `z`, `height`, and `width`. The lengths of these arrays must all be the same.

EchoSMs provides functions to convert to and from the outline format into the specific formats typically required by the DWBA, KRM, and DCM models - see the examples below.

Historically, outline shapes used in the KRM model used a centreline coincident with the _x_-axis (i.e., _y_ = _z_ = 0), upper and lower shape distances measured from the centreline, and symmetric widths. This form of outline shape can be converted to the anatomical datastore form using an echoSMs utility function:

```py hl_lines="10 11 12 13 14 15"
from echosms import outline_from_krm, KRMdata, plot_specimen

# Get a fish shape from the old echoSMs KRM datastore
data = KRMdata()
cod = data.model('Cod')
cod.plot()

# Convert the shape to the echoSMs anatomical datastore form. To keep
# this example brief, only do the body outline and ignore any inclusions.
s = outline_from_krm(x = cod.body.x,
                     height_u = cod.body.z_U,
                     height_l = cod.body.z_L,
                     width = cod.body.w,
                     name='body',
                     boundary=cod.body.boundary)

# Add in other shape attributes to give a shape that contains all
# those required by the schema.
s['sound_speed_compressional'] = cod.body.rho
s['mass_density'] = cod.body.c

# The shape is now in the echoSMs anatomical datastore form with
# (x,y,z) points defining the centreline and widths and heights for
# the body size.
print(s.keys())

# Add the shape to some example specimen metadata
specimens = {'specimens': 
                [{'specimen_id': 'A',
                  'specimen_condition': 'unknown',
                  'length': 0.0,
                  'weight': 0.0,
                  'sex': 'unknown',
                  'length_type': 'unknown',
                  'shape_type': 'outline',
                  'shapes': [s]}]}

# And use an echoSMs function to plot the shape 
# (to compare to the one from KRMdata above()).
plot_specimen(specimens['specimens'][0], dataset_id='Cod')
```

In the same way as for the surface mesh example above, the 
specimen data can be written to a TOML file.

DBWA model implementations tend to use a centreline that is curved in the _z_-axis and body cross-sections that are circular, so there is a separate function for converting DWBA shapes:

```py  hl_lines="9 10 11 12"
from echosms import outline_from_dwba, DWBAdata, plot_specimen

# Get a krill shape from the old echoSMs DWBA datastore
data = DWBAdata()
krill = data.model('Generic krill (McGehee 1998)')
krill.plot()

# Convert the shape to the echoSMs anatomical datastore form.
s = outline_from_dwba(x = krill.rv_pos[:, 0],
                      z = -krill.rv_pos[:, 2],
                      radius = krill.a,
                      name='body', boundary='soft')

# Add in other shape attributes to give enough information to run a model.
s['sound_speed_ratio'] = krill.h
s['mass_density_ratio'] = krill.g

# The shape is now in the echoSMs anatomical datastore form with
# (x,y,z) points defining the centreline and widths and heights for
# the body size.
print(s.keys())

# Add the shape to some example specimen metadata
specimens = {'specimens': 
                [{'specimen_id': '123',
                  'specimen_condition': 'unknown',
                  'length': 0.0,
                  'weight': 0.0,
                  'sex': 'unknown',
                  'length_type': 'unknown',
                  'shape_type': 'outline',
                  'shapes': [s]}]}

# And use an echoSMs function to plot the shape 
# (to compare to the one from DWBAdata above()).
plot_specimen(specimens['specimens'][0], dataset_id='Krill')
```

#### Voxels

The `voxels` format contains two 3D matrices, one for density and one for sound speed. The echoSMs representation of a 3D matrix is a doubly-nested list as used by the numpy package. Rows (numpy axis 0) correspond to the echoSMs _z_-axis, columns (numpy axis 1) to the echoSMs _x_-axis, and slices (numpy axis 2) to the echoSMs _y_-axis.

Conversion between a Python numpy 3D matrix and the echoSMs structure can simply use the numpy `tolist()` method:

```py
import numpy as np

# Get 3D matrices of sound speed and density
rho = np.array([...])
c = np.array([...])

# Put into a dict as per the echoSMs datastore schema
shape = {'voxel_size': [0.005, 0.005, 0.005],  # echoSMs expects units of metres
         'mass_density': rho.tolist(),
         'sound_speed_compressional': c.tolist()}
```
If using xarrays rather than numpy, you'll need to use the xarray `.values` attribute to get a numpy matrix and then call `tolist()`:

```py
shape = {'voxel_size': [0.005, 0.005, 0.005],
         'mass_density': rho.values.tolist(),
         'sound_speed_compressional': c.values.tolist()}
```

#### Categorised voxels

The `categorised voxels` format uses a single 3D matrix of material property categories (named `categories` in the schema) - for echoSMs these categories must be integers starting at 0. The categories define regions of homogenous material properties in the specimen. The category value is used as a zero-based index into associated `mass_density` and `sounds_speed_compressional` vectors. Hence, the length of the density and sound speed arrays must be at least one more than the highest category number in `categories`. The 3D category matrix is structured the same way as for the voxels format (see above).

### Raw files

Raw data formats are not directly used by scattering models so do not need to be formatted for direct use in scattering models. Raw data typically includes images (e.g., png, tiff, jpg), imaging system files (e.g., CT, MRI, and x-ray – typically DICOM or sets of 2D images), and other more ad-hoc data (e.g., spreadsheets). Text-based file formats are preferred for their long-term usability, but well-defined and accessible binary formats are acceptable (e.g., common image formats and DICOM).

### Processing files

A preference for text file formats, then common binary formats (e.g, for images), then other binary formats with documentation. The aim here is to make the information readily accessible in the future without the use of specialised software.
