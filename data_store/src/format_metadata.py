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
import uuid
from datetime import datetime, timezone
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
rprint(f'Reading datastore schema from [orange1]{schema_file.parent}')
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

        # There may be a metadata.toml file and one or more specimen*.toml files.

        meta_file = path/metadata_file
        if meta_file.exists():
            metadata = rtoml.load(meta_file)
        else:
            metadata = {}

        rprint('Reading dataset [orange1]' + path.name)

        # load each .toml file and combine into one echoSMs datastore structure
        # this can take lots of memory, but we do this on a capable machine...
        for ff in path.glob('specimen*.toml'):
            print('  Loading ' + ff.name, end='')

            data = rtoml.load(ff)  # load the specimen data
            data.update(metadata)  # add in metadata if present

            # Update things the datastore is responsible for
            data['uuid'] = str(uuid.uuid4())
            data['version_time'] = datetime.now(timezone.utc).isoformat()
            data['dataset_size'] = sum(file.stat().st_size for file in Path(path).rglob('*'))/2**20
            data['dataset_size_units'] = 'megabyte'

            # Validate the specimen data
            errored = False
            for error in validator.iter_errors(data):
                rprint(f'\n[yellow] Validation error with {error.message}', end='')
                #rprint('[orange4]' + error.message)
                errored = True

            if errored:
                rprint('\n[red]Validation failed ✗')
                error_count += 1
            else:
                rprint(' [green]Validation passed ✓', end='')

                # Write out to a staging directory
                rprint(' Writing specimen', end='')

                # Make a shape image for later use
                image_file = str(datastore_final_dir/data['uuid']) + '.png'
                plot_specimen(data, title=data['specimen_name'], savefile=image_file, dpi=200)

                if large_shape(data):
                    rprint(' (large shape)', end='')
                    s = data['shapes']
                    data['shapes'] = data['uuid'] + '.json'

                    json_bytes = orjson.dumps(s)
                    with open(datastore_final_dir/data['shapes'], 'wb') as f:
                        f.write(json_bytes)
                print('')

                dataset.append(data)

if error_count:
    rprint(f'[red]{error_count} datasets failed the verification')

print('\nWriting a combined metadata file')
json_bytes = orjson.dumps(dataset)
with open(datastore_final_dir/metadata_final_filename, 'wb') as f:
    f.write(json_bytes)

rprint(f'Compressing all data into [green]{datastore_final_dir.with_suffix(".zip")}')
make_archive(str(datastore_final_dir), 'zip', datastore_final_dir)
