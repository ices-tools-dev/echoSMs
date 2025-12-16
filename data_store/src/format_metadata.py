"""Misc data store work.

1. Read all dataset metadata .TOML files and populate dataset_id and dataset_size attributes
2. Validate all datasets against the JSON schema
3. Create files in a staging directory for uploading to the server

"""
# /// script
# dependencies = ['orjson', 'rtoml', 'jsonschema_rs', 'rich', 'echosms', 'numpy']
# ///
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

def large_shape(row):
    """Identify large shape datasets."""
    if row['shape_type'] == 'voxels' and np.array(row['shapes'][0]['mass_density']).size > 1e3:
        return True

    if row['shape_type'] == 'categorised voxels' and\
       np.array(row['shapes'][0]['categories']).size > 1e3:
        return True

    if row['shape_type'] == 'surface' and len(row['shapes'][0]['x']) > 500:
        return True


# json schema for the echoSMs anatomical data store
rprint(f'Reading datastore schema from [orange]{schema_file.parent}')
with open(schema_file, 'rb') as f:
    json_bytes = f.read()
    schema = orjson.loads(json_bytes)

validator = jsonschema_rs.validator_for(schema)

# Read in all .toml files that we can find, add/update the dataset_id and dataset_size
# attributes, flatten, and generate an image of each specimen. For specimens with large
# shape data, save that to a seprate json file. Then write out a json file with all specimen
# data in it (except for the large shape data).

dataset = []
error_count = 0
rprint(f'Using datasets in [green]{datasets_dir}')
rprint(f'Writing outputs to [green]{datastore_final_dir}\n')
for path in datasets_dir.iterdir():
    if path.is_dir():

        # There should be a metadata.toml file and zero or more specimen*.toml files.
        meta_files = [path/metadata_file]

        if not (path/meta_files[0]).exists():
            continue

        rprint('Reading dataset [orange1]' + path.name)

        # Add any specimen*.toml files to the list
        meta_files.extend(list(path.glob('specimen*.toml')))

        # load each .toml file and combine into one echoSMs datastore structure
        # this can take lots of memory, but we do this on a capable machine...
        for ff in meta_files:
            print('  Loading ' + ff.name)
            if ff.name == metadata_file:
                data = rtoml.load(ff)
                if 'specimens' not in data:
                    data['specimens'] = []
            else:
                specimen = rtoml.load(ff)
                data['specimens'].extend(specimen['specimens'])

        data['dataset_id'] = path.name
        data['dataset_size'] = sum(file.stat().st_size for file in Path(path).rglob('*'))/2**20
        data['dataset_size_units'] = 'megabyte'

        errored = False
        for error in validator.iter_errors(data):
            rprint(f'[yellow] Validation error with {error.schema_path}')
            #rprint('[orange4]' + error.message)
            errored = True

        if errored:
            rprint('  [red]Validation failed ✗')
            error_count += 1
        else:
            rprint('  [green]Validation passed ✓')
            # Flatten and write out to a staging directory
            for sp in data['specimens']:

                anatomical_types = [sh['anatomical_type'] for sh in sp['shapes']]

                row = {'id': data['dataset_id'] + '_' + sp['specimen_id']} |\
                    {'anatomical_types': anatomical_types} |  data | sp

                rprint(f'    Writing specimen [orange4]{row["specimen_id"]:s}', end='')

                # Remove unneeded columns in the flattened version
                for r in ['specimens',]:
                    row.pop(r)

                # Make a shape image for later use
                image_file = str(datastore_final_dir/row['id']) + '.png'
                plot_specimen(row, title=row['id'], savefile=image_file, dpi=200)

                if large_shape(row):
                    rprint(' (large shape)', end='')
                    s = row['shapes']
                    row['shapes'] = row['id'] + '.json'

                    json_bytes = orjson.dumps(s)
                    with open(datastore_final_dir/row['shapes'], 'wb') as f:
                        f.write(json_bytes)
                print('')

                dataset.append(row)

if error_count:
    rprint(f'[red]{error_count} datasets failed the verification')

print('\nWriting a combined metadata file')
json_bytes = orjson.dumps(dataset)
with open(datastore_final_dir/metadata_final_filename, 'wb') as f:
    f.write(json_bytes)

rprint(f'Compressing all data into [green]{datastore_final_dir.with_suffix(".zip")}')
make_archive(str(datastore_final_dir), 'zip', datastore_final_dir);
