"""Misc data store work.

1. Read all dataset metadata .TOML files and populate dataset_id and dataset_size attributes
2. Validate all datasets against the JSON schema
3. Create a single JSON file that contains all dataset metadata, for use in the web API server

"""
# %%
from pathlib import Path
import tomllib
import json
import jsonschema
from rich import print as rprint

datastore_dir = Path(r'C:\Users\GavinMacaulay\OneDrive - Aqualyd Limited'
                     r'\Documents\Aqualyd\Projects\2024-05 NOAA modelling'
                     r'\working\anatomical data store')
echosms_dir = Path(r'E:\repositories\echoSMs')

datasets_dir = datastore_dir/'datasets'
schema_file = echosms_dir/'data_store'/'schema'/'v1'/'anatomical_data_store.json'

metadata_file = 'metadata.toml'
metadata_file_updated = 'metadata_automatically_generated.json'

# json schema for the echoSMs anatomical data store
with open(schema_file, 'rb') as f:
    schema = json.load(f)
v = jsonschema.Draft202012Validator(schema)

# Read in all .toml files that we can find, add/update the dataset_id and dataset_size
# attributes and write out as a json file. Also create a single json file that contains
# all datsets that we can serve from using FastAPI.
all_data = []

for path in datasets_dir.iterdir():
    if path.is_dir():
        # There should be a metadata.toml file and zero or more specimen*.toml files.
        meta_files = [path/metadata_file]

        if not (path/meta_files[0]).exists():
            continue

        # Add any specimen*.toml files to the list
        meta_files.extend(list(path.glob('specimen*.toml')))

        # load each .toml file and cmombine into one echoSMs datastore structure
        for ff in meta_files:
            with open(ff, mode='rb') as f:
                if ff.name == metadata_file:
                    print('Loading ' + ff.name)
                    data = tomllib.load(f)
                    if 'specimens' not in data:
                        data['specimens'] = []
                else:
                    print('Loading ' + ff.stem)
                    specimen = tomllib.load(f)
                    data['specimens'].extend(specimen['specimens'])

        data['dataset_id'] = path.name
        data['dataset_size'] = sum(file.stat().st_size for file in Path(path).rglob('*'))/2**20
        data['shape_types'] = list({s['shape_type'] for s in data['specimens']})

        rprint(f'Validating dataset in [cyan]{path.name}')
        errored = False
        for error in sorted(v.iter_errors(data), key=str):
            print(f'Error in dataset {path.name} at {error.json_path}')
            # rprint('[orange4]' + error.message + ' (at ' + error.json_path + ')')

            errored = True

        # write out a modified (and combined if there were specimen*.toml files)
        # dataset file in json format
        if not errored:
            with open(path/metadata_file_updated, 'w') as f:
                json.dump(data, f, indent=2)
            all_data.append(data)

# Write the validated datasets out as a single JSON file
print('Writing a combined metadata file')
with open(datasets_dir/'all-datasets-automatically-generated.json', 'w') as f:
    json.dump(all_data, f, indent=2)
