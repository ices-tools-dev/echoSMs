# Workshop material

## Suggested activities

Some things to try:

1. Convert your shape data into the echoSMs coordinate and unit systems
1. Generate TOML files that are suitable for loading to the datastore
1. Retrieve shape data from the web API and use in a scattering model
1. Add a TOML file to the local web API and test

## Materials

Most of these notebooks and datasets are mentioned in the workshop material and are listed here for convenience. These are all in sub-directories of the `echoSMs-2026-FAST-workshop` directory on your onliner computer.

### Notebooks

- Read shape data, add metadata, validate, and write to TOML format (`creating a datastore input file.ipynb`)
- Get shape data from the datastore (`getting shapes.ipynb`)
- Running models using shape data from the datastore (`running models.ipynb`)
- Retrieve shape data and use in a scattering model (`web shapes to TS.ipynb`)

### Shapes

- Example shape data (in the `shapes` subdirectory):
    - A file with one specimen (`specimen A.toml`)
    - Other example specimen files (of the form `specimen_*.toml`)
    - Shape data not in echoSMs datastore format (`cod_B.txt` and `cod_C.txt`)
