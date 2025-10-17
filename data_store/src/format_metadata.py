"""Misc data store work.

1. Read all dataset metadata .TOML files and populate dataset_id and dataset_size attributes
2. Validate all datasets against the JSON schema
3. Create files in a staging directory for uploading to the server

"""
# %%
from pathlib import Path
import tomllib
import json
import jsonschema
from rich import print as rprint
import numpy as np
from echosms import plot_specimen

datastore_source_dir = Path(r'C:\Users\GavinMacaulay\OneDrive - Aqualyd Limited'
                            r'\Documents\Aqualyd\Projects\2024-05 NOAA modelling'
                            r'\working\anatomical data store')

datastore_final_dir = Path(r'E:\temp\echosms_datastore_final')
datastore_final_dir.mkdir(exist_ok=True)

echosms_dir = Path(r'E:\repositories\echoSMs')

datasets_dir = datastore_source_dir/'datasets'
schema_file = echosms_dir/'data_store'/'schema'/'v1'/'anatomical_data_store.json'

metadata_file = 'metadata.toml'

metadata_final_filename = 'metadata_all_autogen.json'

# json schema for the echoSMs anatomical data store
with open(schema_file, 'rb') as f:
    schema = json.load(f)
v = jsonschema.Draft202012Validator(schema)

# Read in all .toml files that we can find, add/update the dataset_id and dataset_size
# attributes and accumulate in a DataFrame. Write this out at the end as json. Exclude
# any shape data that is considered large.

all_data = []

for path in datasets_dir.iterdir():
    if path.is_dir():

        # if path.name != 'test_categorial':
        #     continue

        # There should be a metadata.toml file and zero or more specimen*.toml files.
        meta_files = [path/metadata_file]

        if not (path/meta_files[0]).exists():
            continue

        # Add any specimen*.toml files to the list
        meta_files.extend(list(path.glob('specimen*.toml')))

        # load each .toml file and combine into one echoSMs datastore structure
        # this can take lots of memory, but we do this on a capable machine...
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
            rprint('[orange4]' + error.message + ' (at ' + error.json_path + ')')

            errored = True

        if not errored:
            all_data.append(data)


# Flatten the read in data and write out to a staging directory
dataset = []

for ds in all_data:
    for sp in ds['specimens']:
        row = {'id': ds['dataset_id'] + '_' + sp['specimen_id']} | ds | sp
        # Remove unneeded columns in the flattened version
        for r in ['specimens', 'shape_types']:
            row.pop(r)

        # Make a shape image for later use
        image_file = (datastore_final_dir/row['id']).with_suffix('.png')
        buf = plot_specimen(row, title=row['id'], stream=True, dpi=200)
        with open(image_file, 'wb') as f:
            f.write(buf)

        large = False

        # Flag large shape datasets
        if row['shape_type'] == 'voxels' and np.array(row['shapes'][0]['mass_density']).size > 1e3:
            large = True

        if row['shape_type'] == 'categorised voxels' and\
           np.array(row['shapes'][0]['categories']).size > 1e3:
            large = True

        if row['shape_type'] == 'surface' and len(row['shapes'][0]['x']) > 500:
            large = True

        if large:
            print(f'{row["id"]} has a large shape')
            s = row['shapes']
            row['shapes'] = row['id'] + '.json'

            with open(datastore_final_dir/row['shapes'], 'w') as f:
                json.dump(s, f, indent=2)  # could zip these up!

        dataset.append(row)

print('Writing a combined metadata file')
with open(datastore_final_dir/metadata_final_filename, 'w') as f:
    json.dump(dataset, f, indent=2)
