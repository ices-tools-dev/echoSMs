## Exercises

Most of these exercises and datasets have been mentioned in the workshop material but are also listed here for convenience.

We have provided example files and demo notebooks code on your hackathon computer to help with the
above. These are mostly in sub-directories of the `echoSMs-2026-FAST-workshop` directory
on your linux server.

- Example shape data (in the `shapes` subdirectory):
  - A dataset with 4 specimens (`example_metadata.toml`)
  - Shape data not in the echoSMs format (`cod_B.txt` and `cod_C.txt`, and `shared-public/Jech/aherr001.dat`
- TOML shape file template (in the `shapes` subdirectory)
  - `template_metadata.toml`
- Example code and demos (in the `notebooks` subdirectory) to:
  - Read shape data, add metadata, validate, and write to TOML format (`create a TOML datastore file.ipynb`)
  - Validate a TOML file against the schema (`validating a TOML datastore file.ipynb`)
  - Retrieve shape data and use in a scattering model (`web API to TS demo.ipynb`)
  - The WGFAST 2025 echoSMs workshop demo (`echoSMs 2025 workshop demo.ipynb`)
  - The echoSMs 2025 WGFAST presentation demo (`echoSMs WGFAST 2025 demo.ipynb`)

## Suggestions for workshop activities

Some things to try (we don't expect you to do all of these, nor in this order):

1. Convert your shape data (or ones we provide) into the echoSMs coordinate and unit systems
1. Generate TOML files that are suitable for loading to the web API
1. Retrieve shape data from the web API and use in a scattering model
1. Populate the schema metadata and give feedback
1. Use the web API and give feedback
