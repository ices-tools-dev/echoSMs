"""Code for testing validation of TOML datastore files."""
# /// script
# dependencies = ['requests', 'rtoml', 'jsonschema_rs', 'orjson']
# ///
from pathlib import Path
import requests
import rtoml
import jsonschema_rs
import orjson

# Get schema from github
schema_url = 'https://raw.githubusercontent.com/ices-tools-dev/echoSMs/refs/heads/main/data_store/schema/v1/anatomical_data_store.json'
schema = requests.get(schema_url).json()

# Get schema from local file
schema_file = Path(r'C:\Users\GavinMacaulay\Data - not synced\Code\echoSMs\data_store\schema\v1')
schema_file = schema_file/'anatomical_data_store.json'

with open(schema_file, 'rb') as f:
    json_bytes = f.read()
    schema = orjson.loads(json_bytes)


validator = jsonschema_rs.validator_for(schema,
                                        validate_formats=True,
                                        ignore_unknown_formats=False)

toml_file = Path('metadata.toml')

specimen = rtoml.load(toml_file)

json_bytes = orjson.dumps(specimen)
with open('metadata.json', 'wb') as f:
    f.write(json_bytes)

error_count = 0
for i, error in enumerate(validator.iter_errors(specimen)):
    error_count += 1
    msg = error.message
    if len(msg) > 200:
        msg = msg[:100] + ' ... ' + msg[-100:]
    instance_path = '.'.join([str(a) for a in error.instance_path])
    schema_path = '.'.join(error.schema_path)

    print(f'Error {i}:')
    print(f'\tFor attribute "{instance_path}" with schema path of "{schema_path}"')
    print(f'\t{msg}')

    # print(error.kind.name)
    # print(error.kind.as_dict().keys())
if error_count == 0:
    print('Input data is valid.')

#ee = validator.evaluate(specimen)

# if not ee.valid:
#     e = ee.list()['details']
#     for eee in e:
#         if not eee['valid']:
#             print(eee['evaluationPath'], eee['instanceLocation'])
# else:
#     print('Input data is valid.')

# if not validator.is_valid(specimen):
#     for i, error in enumerate(validator.iter_errors(specimen)):
#         print(i)
#         #print(f'{error}')
# else:
#     print('Input data is valid.')
