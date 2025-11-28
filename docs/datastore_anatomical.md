# Anatomical data store

???+ Note

    This page contains the draft specification and documentation for the echoSMs anatomical datastore. It is a work in progress. The specification here may not always be 
    consistent with the example data available from the web API.

## Data store contents and structure

The datastore contains many datasets, where each dataset comprises the following:

1. Metadata
1. Input data to scattering models (material properties, 3D shapes, and other model parameters)
1. Optionally, raw data files that were used to produce the scattering model input data (e.g., binary files, such as x-ray and photographic images, MRI & CT scan files, etc)
1. Optionally, processing files (programs, notes, intermediate data files, etc)

Each dataset may contain information about more than one organism but can only contain data from a single species.

The dataset metadata and model data have prescribed formats that are designed for convenient access via a [RESTful](https://en.wikipedia.org/wiki/REST) API and for inputting to scattering models.

The raw data and processing file formats and layout are unconstrained and are accessible via the RESTful API as a zipped download and a browsable directory hierarchy.

Model outputs are not stored.

## Preparing datasets for the datastore

A dataset ready for uploading to the datastore should contain the following files and directory structures, bundled into a single zip file:

|Path|File(s)|Required|Comment|
|----|-------|--|-------|
|/|metadata.toml|yes|Dataset metadata in TOML format. This file can include specimen and model data. The file name must be `metadata.toml`|
|/|specimen*.toml|no|Specimen and model data in one or more TOML-formatted files. File names must start with `specimen` and have a suffix of `.toml`. These files are simply appended to the metadata.toml file when reading the dataset data.|
|/data|Any|no|Raw and processing files in user-supplied directory hierarchy|

There is currently no automated way to upload datasets to the datastore - it is a manual process - raise an [issue](https://github.com/ices-tools-dev/echoSMs/issues) on Github or contact Gavin Macaulay to have datasets uploaded.

## Data formats

### Raw files

Raw data formats are not directly used by scattering models so do not need to be formatted for direct use in scattering models. Raw data typically includes images (e.g., png, tiff, jpg), imaging system files (e.g., CT, MRI, and x-ray – such as DICOM or sets of 2D images), and other more ad-hoc data (e.g., spreadsheets, csv files). Text-based file formats are preferred for their long-term usability, but well-defined and accessible binary formats are acceptable (e.g., common image formats and DICOM).

### Processing files

A preference for text file formats, then common binary formats (e.g, for images), then other binary formats with documentation. The aim here is to make the information readily accessible in the future without the use of specialised software.

### Dataset and model data

The dataset metadata includes information about the species, the collection and processing of specimens used in scattering models, links to published work, and other context. These are intended to provide information for users to assess the quality, usability, and suitability of a particular dataset.

Associated with each dataset are data about one or more specimens. This includes basic information about the specimen(s) (e.g., length and weight), along with the three-dimensional shape information required by acoustic scattering models. Note that a specimen is not necessarily a whole organism - the data structure allows for a specimen to be some part of the organism (e.g., swimbladder, organs, etc)

The dataset contents are specified by a [JSON schema](https://json-schema.org/) file stored in the echoSMs [github repository](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/schema/v1/anatomical_data_store.json). The schema documents the required attributes, their structure, valid values, etc. The schema is a very technical document and is perhaps more easily understood via the table in the echoSMs [documentation](schema/data_store_schema.md) and an [example file](https://github.com/ices-tools-dev/echoSMs/tree/main/data_store/resources).

An alternative structure for the schema is available in an echoSMs [issue](https://github.com/ices-tools-dev/echoSMs/issues/35).

Your dataset files can be validated against the datastore schema using online validators (e.g., [here](https://www.jsonschemavalidator.net/), [here](https://jsonschema.dev/), or [here](https://www.liquid-technologies.com/online-json-schema-validator)), or within your own code using a JSON schema validation library (e.g., [jsonschema-rs](https://github.com/Stranger6667/jsonschema/tree/master/crates/jsonschema-py) for Python and [jsonvalidate](https://cran.r-project.org/web/packages/jsonvalidate/vignettes/jsonvalidate.html) for R). It is not necessary to validate your data before submitting it to the datastore, but it will help the uploading happen faster (a validation is done during the uploading process and any dataset format problems will be identified then).

### Shapes

Most anatomical scattering models use one of these three-dimensional representations:

- 3D triangulated surface meshes,
- dorsal and ventral outlines,
- 3D grids of cuboids (voxels).

Some models use multiple shapes for a single specimen (e.g., a fish body and swimbladder) and multiple shapes per specimen are permitted. Additional shape formats can be added as required (e.g., tetrahedrons as used by the [TetraScatt](https://doi.org/10.1115/1.4067286) scattering model).

|Shape data type|Realisation|Models that use this|Example from datastore|Material properties|
|---------------|-----------|--------------------|-----|--|
|surface|3D triangular surface mesh|BEM, KA|[data](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/GJM003_HOK_hok108/data), [image](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/GJM003_HOK_hok108/image)|ρ and c per shape|
|outline|Dorsal and ventral outlines along a curved centreline|KRM, DWBA, DCM|[data](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/CLAY_HORNE_A/data), [image](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/CLAY_HORNE_A/image)|ρ and c per shape (KRM) or per section (DWBA)|
|voxels|3D rectangular grid|FEM|[data](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/GJM001_2/data), [image](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/GJM001_2/image)|ρ and c for each voxel|
|categorised voxels|categorised 3D rectangular grid|PT-DWBA|[data](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/test_categorical_1/data), [image](https://echosms-data-store-app-ogogm.ondigitalocean.app/v2/specimen/test_categorical_1/image)|ρ and c for each category|

???+ Note
    The outline shape is a generalised form of the shape definition used for several models:

    - KRM: non-circular cross-sections along a straight centreline
    - DWBA: circular cross-sections along a curved centreline
    - DCM: circular cross-sections along a straight or curved centreline

#### Shape data structure

The shape data format is formally specified in the echoSMs anatomical data store schema, but some additional explanatory notes, utility code, and examples are provided here.

##### Surface

The `surface` format contains a 3D triangular surface mesh. The mesh is represented with three numeric arrays (`x`, `y`, and `z`) for the x, y, and z coordinates of the surface nodes, three integer arrays (`facets_0`, `facets_1`, `facets_2`) that index into the x, y, and z arrays and specify the nodes that make up individual triangles, and three arrays that give the outward unit normal vector for each triangle (`normals_x`, `normals_y`, and `normals_z`). The lengths of the facets and normals arrays must all be the same.

???+ note
    Some scattering models require a closed 3D surface mesh (i.e., without holes), but the `surface` format does not enforce this.

EchoSMs provides a function, [surface_from_stl()][echosms.surface_from_stl], to convert an [STL](https://en.wikipedia.org/wiki/STL_(file_format)) file into the echoSMs surface shape format:

```py
from echosms import surface_from_stl

shape = surface_from_stl('A.stl', dim_scale=1e-3, anatomical_type='body',
                          boundary='pressure-release')
```

This shape can then be combined with specimen metadata and written to a TOML file ready for loading into the echoSMs datastore:

```py
import tomli_w

# Create specimen metadata and add in the shape
specimens = {'specimens': 
                [{'specimen_id': 'A',
                  'specimen_condition': 'unknown',
                  'length': 0.0,
                  'length_units': 'm',
                  'weight': 0.0,
                  'weight_units': 'kg',
                  'sex': 'unknown',
                  'length_type': 'unknown',
                  'shape_type': 'surface',
                  'shapes': [shape]}]}

# Write to a TOML file
with open('specimen_A.toml', 'wb') as f:
    tomli_w.dump(specimens, f)
```

There is a complimentary function to `surface_from_stl()` that takes the echoSMs datastore surface format and returns a [trimesh](https://trimesh.org/) object (see [mesh_from_datastore()][echosms.mesh_from_datastore]), from which an STL file can be written.

##### Outline

The `outline` format is a generalised structure that can represent the outline shapes typically used for the DWBA, KRM, and DCM models. It uses a centreline (defined by a list of (_x_, _y_, _z_) coordinates) and a height and width at each centreline point. The [echoSMs coordinate system][coordinate-systems] is used so heights are along the _z_-axis and widths along the _y_-axis. Five numeric arrays are used to represent the shape in the echSMs format with names of `x`, `y`, `z`, `height`, and `width`. The lengths of these arrays must all be the same.

EchoSMs provides functions to convert to and from the outline format into the specific formats typically required by the DWBA, KRM, and DCM models - see the examples below.

Historically, outline shapes used in the KRM model used a centreline coincident with the _x_-axis (i.e., _y_ = _z_ = 0), upper and lower shape distances measured from the centreline, and symmetric widths. This form of outline shape can be converted to the datastore form using an echoSMs utility function:

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
                     anatomical_type='body',
                     boundary=str(cod.body.boundary))

# Add in other shape attributes to give a shape that contains all
# those required by the schema.
s['sound_speed_compressional'] = cod.body.rho
s['sound_speed_compressional_units'] = 'm/s'
s['mass_density'] = cod.body.c
s['mass_density_units'] = 'kg/m^3'

# The shape is now in the echoSMs anatomical datastore form with
# (x,y,z) points defining the centreline and widths and heights for
# the body size.
print(s.keys())

# Add the shape to some example specimen metadata
specimens = {'specimens': 
                [{'specimen_id': 'A',
                  'specimen_condition': 'unknown',
                  'length': 0.0,
                  'length_units': 'm',
                  'weight': 0.0,
                  'weight_units': 'kg',
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
                      anatomical_type='body',
                      boundary='fluid-filled')

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
                  'length_units': 'm',
                  'weight': 0.0,
                  'weight_units': 'kg',
                  'sex': 'unknown',
                  'length_type': 'unknown',
                  'shape_type': 'outline',
                  'shapes': [s]}]}

# And use an echoSMs function to plot the shape 
# (to compare to the one from DWBAdata above()).
plot_specimen(specimens['specimens'][0], dataset_id='Krill')
```

##### Voxels

The `voxels` format contains two 3D matrices, one for density and one for sound speed. The echoSMs representation of a 3D matrix is a doubly-nested list as used by the Numpy package. Rows (numpy axis 0) correspond to the echoSMs _z_-axis, columns (numpy axis 1) to the echoSMs _x_-axis, and slices (numpy axis 2) to the echoSMs _y_-axis.

Numpy's `tolist()` method is used to convert between a Python numpy 3D matrix and the echoSMs structure:

```py
import numpy as np

# Get 3D matrices of sound speed and density
rho = np.array([...])
c = np.array([...])

# Put into a dict as per the echoSMs datastore schema
shape = {'voxel_size': [0.005, 0.005, 0.005],
         'voxel_size_units': 'm',
         'mass_density': rho.tolist(),
         'mass_density_units': 'kg/m^3',
         'sound_speed_compressional': c.tolist(),
         'sound_speed_compressional_units': 'm/s'}
```
If using Xarrays rather than Numpy, you'll need to use the Xarray `.values` attribute to get the Numpy matrix and then call `tolist()`:

```py
shape = {'voxel_size': [0.005, 0.005, 0.005],
         'voxel_size_units': 'm',
         'mass_density': rho.values.tolist(),
         'mass_density_units': 'kg/m^3',
         'sound_speed_compressional': c.values.tolist(),
         'sound_speed_compressional_units': 'm/s'}
```

##### Categorised voxels

The `categorised voxels` format uses a single 3D matrix of material property categories (named `categories` in the schema) - for echoSMs these categories must be integers starting at 0. The categories define regions of homogenous material properties in the specimen. The category value is used as a zero-based index into associated `mass_density` and `sounds_speed_compressional` vectors. Hence, the length of the density and sound speed arrays must be at least one more than the highest category number in `categories`. The category matrix is structured the same way as for the voxels format (see above).
