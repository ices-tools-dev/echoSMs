"""Misc data store work.

1. Read all dataset metadata and populate dataset_id and dataset_size attributes
2. Validate all datasets against the JSON schema
3. Create a single file that contains all dataset metadata for use in the web API server

"""
# %%
from pathlib import Path
import tomllib
import json
import jsonschema

datastore_dir = Path(r'C:\Users\GavinMacaulay\OneDrive - Aqualyd Limited\Documents\Aqualyd\Projects'
                     r'\2024-05 NOAA modelling\working\anatomical data store')
echosms_dir = Path(r'C:\Users\GavinMacaulay\OneDrive - Aqualyd Limited\Documents\Aqualyd\Projects'
                   r'\2024-05 NOAA modelling\working\echoSMs')

datasets_dir = datastore_dir/'datasets'
schema_file = echosms_dir/'data_store'/'schema'/'v1'/'anatomical_data_store.json'

# json schema for the echoSMs anatomical data store
with open(schema_file, 'rb') as f:
    schema = json.load(f)

# Read in all .toml files that we can find, add/update the dataset_id and dataset_size
# attributes and write out as a json file. Also create a single json file that contains
# all datsets that we can serve from using FastAPI.
all_data = []

for path in datasets_dir.iterdir():
    if path.is_dir():
        meta_files = path.glob('*.toml')
        for mf in meta_files:
            with open(mf, 'rb') as f:
                data = tomllib.load(f)
            data['dataset_id'] = path.name
            data['dataset_size'] = sum(file.stat().st_size for file in Path(path).rglob('*'))/2**20
            print(f'Validating dataset in {mf}')
            v = jsonschema.Draft202012Validator(schema)
            errored = False
            for error in sorted(v.iter_errors(data), key=str):
                print(error.message + ' (at ' + error.json_path + ')')
                errored = True

            # write out a modified dataset file in json format
            if not errored:
                with open(mf.with_stem(mf.stem + '_updated').with_suffix('.json'), 'w') as f:
                    json.dump(data, f, indent=2)
                all_data.append(data)

# Write the validated datasets out as a single JSON file
print('Writing a combined metadata file (datasets.json)')
with open(datasets_dir/'datasets-automatically-generated.json', 'w') as f:
    json.dump(all_data, f, indent=2)
