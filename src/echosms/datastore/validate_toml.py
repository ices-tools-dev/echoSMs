"""Code for testing validity of TOML datastore files."""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "rtoml",
#     "jsonschema-rs",
#     "orjson",
#     "rich",
# ]
# ///

from pathlib import Path
import datetime as dt
import glob
import os
import argparse
import rtoml
from rich import print as rprint
import jsonschema_rs
import orjson
from echosms import datastore_schema


def validate_one(schema: dict, specimen: dict, file_label: str):
    """Valid a single TOML file."""

    # Add in attributes that the datastore loading process would normally provide
    if 'version_time' in specimen and specimen['version_time'] == '':
        specimen['version_time'] = dt.datetime.now(dt.timezone.utc).isoformat()
    if 'dataset_size' not in specimen:
        specimen['dataset_size'] = 0.0
    if 'dataset_size_units' not in specimen:
        specimen['dataset_size_units'] = 'megabyte'

    # Create the validator
    validator = jsonschema_rs.validator_for(schema, validate_formats=True,
                                            ignore_unknown_formats=False)

    # Validate and accumulate any errors
    error_msgs = []
    for error in validator.iter_errors(specimen):
        msg = error.message
        if len(msg) > 200:
            msg = msg[:100] + ' ... ' + msg[-100:]

        instance_path = '.'.join([str(a) for a in error.instance_path])
        schema_path = '.'.join(error.schema_path)

        error_msgs.append('  [red]Error:')
        error_msgs.append(
            f'    For attribute "{instance_path}" with schema path of '
            f'"{schema_path}"')
        error_msgs.append(f'    {msg}')

    # Provide info on pass/fail and any errors
    if error_msgs:
        rprint(f'[red]✗[/red] File [orange3]{file_label}[/orange3] is not valid')
        for m in error_msgs:
            rprint(m)
    else:
        rprint(f'[green]✓[/green] File [orange3]{file_label}[/orange3] is valid')


def main():
    """Validate TOML files."""

    parser = argparse.ArgumentParser(prog='validate',
                                     description='Validates an echoSMs datastore TOML file'\
                                        ' against the schema.',
                                     epilog='The values of some attributes are populated or '\
                                            'modified by the '\
                                            'datastore and temporary substitutes generated '\
                                            'when necessary.')

    parser.add_argument('toml_file', help='echoSMs TOML file(s) (can include wildcards; '\
                        'use ** to search in subdirectories)',
                        action='extend', nargs='+')
    parser.add_argument('-s', '--schema', help='provide the datastore schema file directly '\
                        '(it is otherwise downloaded from the echoSMs Github repository)')
    parser.add_argument('-j', '--json', action='store_true',
                        help='write the TOML file out in JSON format to the same directory '\
                             'as the TOML file (works even if the validation fails)')
    args = parser.parse_args()

    # Expand out any wildcard file inputs and discard non files.
    toml_files = []
    for f_args in args.toml_file:
        toml_files.extend([Path(f) for f in glob.glob(f_args, recursive=True)
                           if os.path.isfile(f) and Path(f).name != 'metadata.toml'])

    # Get the JSON schema
    if args.schema:
        schema = datastore_schema(args.schema)
    else:
        schema = datastore_schema()
        if schema == '':
            print('Could not get the datastore schema from Github. Try again or pass '
                  'a file in with the --schema option.')
            return

    # Parse each TOML file
    for toml in toml_files:
        try:
            specimen = rtoml.load(toml)
            # if there is also a metadata.toml file in the same directory, that needs to be
            # added to the file we're working on
            if (metadata_file := toml.parent/'metadata.toml').exists():
                specimen |= rtoml.load(metadata_file)

        except rtoml.TomlParsingError:
            rprint(f'[red]✗[/red] Could not parse [orange3]{toml.name}[/orange3]. '\
                'Is it a TOML-formatted file?')
            continue

        # Write out to json if requested
        if args.json:
            json_bytes = orjson.dumps(specimen, option=orjson.OPT_INDENT_2)
            with open(Path(toml).with_suffix('.json'), 'wb') as f:
                f.write(json_bytes)

        validate_one(schema, specimen, Path(toml.parent.name) / toml.name)


if __name__ == '__main__':
    main()
