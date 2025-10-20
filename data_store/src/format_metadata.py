"""Misc data store work.

1. Read all dataset metadata .TOML files and populate dataset_id and dataset_size attributes
2. Validate all datasets against the JSON schema
3. Create files in a staging directory for uploading to the server

"""
# %%
from pathlib import Path
import orjson
import rtoml
import jsonschema_rs
from rich import print as rprint
import numpy as np
from echosms import plot_specimen
from shutil import make_archive

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
    json_bytes = f.read()
    schema = orjson.loads(json_bytes)

validator = jsonschema_rs.validator_for(schema)

# Read in all .toml files that we can find, add/update the dataset_id and dataset_size
# attributes and accumulate in a DataFrame. Write this out at the end as json. Exclude
# any shape data that is considered large.

# Note: this loop below reads all data into memory at once - this will eventually cause problems
# with out of memory errors. The solution is to do the large model detection in this loop rather
# than the subsequent loop.

all_data = []

for path in datasets_dir.iterdir():
    if path.is_dir():

        # if path.name != 'test_categorial':
        #     continue

        # There should be a metadata.toml file and zero or more specimen*.toml files.
        meta_files = [path/metadata_file]

        if not (path/meta_files[0]).exists():
            continue

        rprint('[orange1]Reading dataset: ' + path.name)

        # Add any specimen*.toml files to the list
        meta_files.extend(list(path.glob('specimen*.toml')))

        # load each .toml file and combine into one echoSMs datastore structure
        # this can take lots of memory, but we do this on a capable machine...
        for ff in meta_files:
            if ff.name == metadata_file:
                print('Loading ' + ff.name)
                data = rtoml.load(ff)
                if 'specimens' not in data:
                    data['specimens'] = []
            else:
                print('Loading ' + ff.stem)
                specimen = rtoml.load(ff)
                data['specimens'].extend(specimen['specimens'])

        data['dataset_id'] = path.name
        data['dataset_size'] = sum(file.stat().st_size for file in Path(path).rglob('*'))/2**20
        data['shape_types'] = list({s['shape_type'] for s in data['specimens']})

        rprint(f'Validating dataset in [cyan]{path.name}')
        errored = False
        for error in validator.iter_errors(data):
            print(f'Error in dataset {path.name} at {error.json_path}')
            rprint('[orange4]' + error.message + ' (at ' + error.json_path + ')')
            errored = True

        if not errored:
            all_data.append(data)

# Flatten the read in data and write out to a staging directory
dataset = []
rprint('\n[orange1]Creating shape plots and final data files:')
for ds in all_data:
    for sp in ds['specimens']:
        row = {'id': ds['dataset_id'] + '_' + sp['specimen_id']} | ds | sp
        print(f'Processing specimen with id {row["id"]}')
        # Remove unneeded columns in the flattened version
        for r in ['specimens', 'shape_types']:
            row.pop(r)

        # Make a shape image for later use
        image_file = str(datastore_final_dir/row['id']) + '.png'
        plot_specimen(row, title=row['id'], savefile=image_file, dpi=200)

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
            rprint(f'    [cyan]{row["id"]} has a large shape')
            s = row['shapes']
            row['shapes'] = row['id'] + '.json'

            json_bytes = orjson.dumps(s)
            with open(datastore_final_dir/row['shapes'], 'wb') as f:
                f.write(json_bytes)

        dataset.append(row)

print('Writing a combined metadata file')
json_bytes = orjson.dumps(dataset)
with open(datastore_final_dir/metadata_final_filename, 'wb') as f:
    f.write(json_bytes)

print(f'Compressing all data to {datastore_final_dir.with_suffix(".zip")}')
make_archive(str(datastore_final_dir), 'zip', datastore_final_dir);
