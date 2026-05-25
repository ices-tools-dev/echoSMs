"""Misc data store work.

1. Read all dataset metadata .TOML files and populate dataset_id and dataset_size attributes
2. Validate all datasets against the JSON schema
3. Create files in a staging directory for uploading to the server
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     'orjson',
#     'rtoml',
#     'jsonschema_rs',
#     'rich',
#     'echosms',
#     'numpy',
#     'matplotlib',
# ]
# ///

# %%
from pathlib import Path
import argparse
from tempfile import TemporaryDirectory
import orjson
import rtoml
import jsonschema_rs
from rich import print as rprint
import numpy as np
import uuid
from datetime import datetime, timezone
from echosms import plot_specimen, names_from_aphia_id, datastore_schema
from shutil import make_archive


def main():
    parser = argparse.ArgumentParser(prog='process_datastore',
        description='Converts datastore TOML files into an upload for the echoSMs datastore.')
    
    parser.add_argument('-s', '--source', required=True,
                        help='the directory that contains sub-directories '
                        'of datastore TOML files')
    parser.add_argument('-o', '--output', required=True,
                        help='the directory to write the upload package to')
    parser.add_argument('--schema', help='provide the datastore schema file directly '\
                        '(it is otherwise downloaded from the echoSMs Github repository)')
    args = parser.parse_args()

    source_dir = Path(args.source)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    temp_dir = TemporaryDirectory(prefix='echosMs')
    temp_path = Path(temp_dir.name)

    schema = datastore_schema()

    metadata_file = 'metadata.toml'
    metadata_final_filename = 'metadata_all_autogen.json'
    upload_filename = 'echosms_datastore_upload'
    upload_zip_file = output_dir / upload_filename

    def large_shape(row):
        """Identify large shape datasets."""
        if row['shape_type'] == 'voxels' and np.array(row['shapes'][0]['mass_density']).size > 1e3:
            return True

        if row['shape_type'] == 'categorised voxels' and\
        np.array(row['shapes'][0]['categories']).size > 1e3:
            return True

        if row['shape_type'] == 'surface' and len(row['shapes'][0]['x']) > 500:
            return True

    validator = jsonschema_rs.validator_for(schema, validate_formats=True, ignore_unknown_formats=False)

    # Read in all .toml files that we can find, add/update the dataset_id and dataset_size
    # attributes, flatten, and generate an image of each specimen. For specimens with large
    # shape data, save that to a seprate json file. Then write out a json file with all specimen
    # data in it (except for the large shape data).

    dataset = []
    error_count = 0
    rprint(f'Using datasets in [green]{source_dir}')
    rprint(f'Writing outputs to [green]{temp_path}\n')
    count = 1
    for path in source_dir.iterdir():
        if path.is_dir():
            if count > 2:
                break
            count += 1
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
                if data['uuid'] == '':
                    data['uuid'] = str(uuid.uuid4())
                data['version_time'] = datetime.now(timezone.utc).isoformat()
                data['dataset_size'] = sum(file.stat().st_size for file in Path(path).rglob('*'))/2**20
                data['dataset_size_units'] = 'megabyte'

                # Add in species info if not already there
                names = names_from_aphia_id(data['aphia_id'])

                for k, v in names.items():
                    if k not in data:
                        data[k] = v

                # Validate the specimen data
                errored = False
                for error in validator.iter_errors(data):
                    #print(error.instance_path)
                    #print(error.evaluation_path)
                    #print(error.schema_path)
                    rprint(f'\n[yellow] Validation error with {error.message}', end='')
                    # rprint('[orange4]' + error.message)
                    errored = True

                if errored:
                    rprint('\n[red]Validation failed ✗')
                    error_count += 1
                else:
                    rprint(' [green]Validation passed ✓', end='')

                    # Write out to a staging directory
                    rprint(' Writing specimen', end='')

                    # Make a shape image for later use
                    image_file = str(temp_path/data['uuid']) + '.png'
                    plot_specimen(data, title=data['specimen_name'], savefile=image_file, dpi=200)

                    if large_shape(data):
                        rprint(' (large shape)', end='')
                        large_shape_file = data['uuid'] + '.json'

                        # write out the shape information
                        json_bytes = orjson.dumps(data['shapes'])
                        with open(temp_path/large_shape_file, 'wb') as f:
                            f.write(json_bytes)
                        data['large_shape_ref'] = large_shape_file

                        # replace the shape info with just the metadata
                        s_metadata = []
                        for s in data['shapes']:
                            ss = {k: v for k, v in s.items()
                                    if k in ['anatomical_feature', 'name', 'boundary']}
                            s_metadata.append(ss)

                        data['shapes'] = s_metadata

                    print('')

                    dataset.append(data)

    if error_count:
        rprint(f'[red]{error_count} datasets failed the validation')

    rprint(f'[green]{len(dataset)} datasets passed the validation')

    print('\nWriting a combined metadata file')
    json_bytes = orjson.dumps(dataset)
    with open(temp_path/metadata_final_filename, 'wb') as f:
        f.write(json_bytes)

    rprint(f'Compressing all data into [green]{output_dir.with_suffix(".zip")}')
    make_archive(str(upload_zip_file), 'zip', str(temp_path))

    temp_dir.cleanup()

if __name__ == '__main__':
    main()
