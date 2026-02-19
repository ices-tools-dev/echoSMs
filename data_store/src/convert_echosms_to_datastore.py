"""Convert echoSMs shape format.

Converts old echoSMs KRM and DWBA shape data format into the new echoSMs
anatomical data store metadata and shape formats.
"""
import copy
import numpy as np
from datetime import datetime, timezone
from echosms import KRMdata, DWBAdata, outline_from_krm, boundary_type as bt
import tomli_w
import requests
import uuid
from pathlib import Path


datastore_dir = Path(r'C:\Users\GavinMacaulay\OneDrive - Aqualyd Limited\Documents\Aqualyd'
                     r'\Projects\2024-05 NOAA modelling\working\anatomical data store')

worms_url = 'https://www.marinespecies.org/rest/AphiaRecordByAphiaID/'

# Datset template
specimen_t = {'uuid': '',
             'dataset_uuid': '',
             'description': [''],
             'anatomical_category': "organism",
             'version_time': '',
             'version_number': 1,
             'version_note': 'Initial version',
             'version_investigators': [],
             'aphia_id': 1,
             'class': "",
             'order': "",
             'family': "",
             'genus': "",
             'species': "",
             'vernacular_names': [""],
             'reference': '',
             'date_collection': "unknown",
             'date_image': "",
             'data_collection_description': "",
             'notes': [],
             'imaging_method': "unknown",
             'shape_method': "unknown",
             'shape_method_processing': "unknown",
             'model_type': "",
             'sound_speed_method': "unknown",
             'mass_density_method': "unknown",
             'shapes': []}

if 'aphiaID_cache' not in locals():
    aphiaID_cache = {}

########################
# KRM models
d = KRMdata()

specimens = []
# All the echoSMs KRM model are grouped into the same dataset
dataset_uuid = str(uuid.uuid4())

# create models from the echoSMs KRM data
for model_name in d.names():
    m = d.model(model_name)

    specimen = copy.deepcopy(specimen_t)
    specimen['dataset_uuid'] = dataset_uuid
    specimen['uuid'] = str(uuid.uuid4())
    specimen['aphia_id'] = m.aphiaid
    specimen['shape_method'] = 'unknown'
    specimen['model_type'] = 'KRM'
    specimen['description'] = ['Shape data for KRM models']
    specimen['notes'] = ['Shape obtained from the KRM shapes available at '
    'https://www.fisheries.noaa.gov/data-tools/krm-model. ',
    'This is not necessarily the original source of the shape.']

    if m.aphiaid not in aphiaID_cache:
        print(f'Querying WoRMS for aphiaID {m.aphiaid}')
        r = requests.get(worms_url + str(m.aphiaid))
        if r.status_code == 200:
            aphiaID_cache[m.aphiaid] = r.json()
        else:
            print('Failed to get record for aphiaID = {m.aphiaid}')

    for attr in ['class', 'order', 'family', 'genus']:
        specimen[attr] = aphiaID_cache[m.aphiaid][attr]
    specimen['species'] = aphiaID_cache[m.aphiaid]['scientificname']

    specimen['vernacular_names'] = [m.vernacular_name]
    specimen['reference'] = m.source
    specimen['version_time'] = datetime.now(timezone.utc).isoformat()

    specimen.update({'specimen_name': m.name, 'specimen_condition': 'unknown',
                     'straightened': True, 'smoothed': False, 'rotated': True,
                     'length': m.length,
                     'length_units': 'm',
                     'sex': 'unknown',
                     'length_type': 'unknown', 'shape_type': 'outline',
                     'shapes': []})

    shape = outline_from_krm(m.body.x, m.body.z_U, m.body.z_L,
                             m.body.w, boundary=m.body.boundary)
    shape['mass_density'] = len(m.body.x) * [m.body.rho]
    shape['mass_density_units'] = 'kg/m^3'
    shape['sound_speed_compressional'] = len(m.body.x) * [m.body.c]
    shape['sound_speed_compressional_units'] = 'm/s'
    shape['shape_units'] = "m"
    specimen['shapes'].append(shape)

    for inc in m.inclusions:
        a_type = 'swimbladder' if inc.rho < 100 else 'bone'
        shape = outline_from_krm(inc.x, inc.z_U, inc.z_L,
                                 inc.w, boundary=inc.boundary,
                                 anatomical_feature=a_type)
        shape['mass_density'] = len(inc.x) * [inc.rho]
        shape['mass_density_units'] = 'kg/m^3'
        shape['sound_speed_compressional'] = len(inc.x) * [inc.c]
        shape['sound_speed_compressional_units'] = 'm/s'
        shape['shape_units'] = "m"
        specimen['shapes'].append(shape)

    specimens.append(specimen)

# ############################
# DWBA models
d = DWBAdata()
# All the echoSMs DWBA model are grouped into the same dataset
dataset_uuid = str(uuid.uuid4())

for model_name in d.names():
    m = d.model(model_name)

    # populate dataset metadata
    specimen = copy.deepcopy(specimen_t)
    specimen['dataset_uuid'] = dataset_uuid
    specimen['uuid'] = str(uuid.uuid4())
    specimen['aphia_id'] = m.aphiaid
    specimen['shape_method'] = 'unknown'
    specimen['model_type'] = 'DWBA'
    specimen['description'] = ['Some DWBA shapes found on the internet.']
    specimen['model_type'] = 'DWBA'
    specimen['notes'] = ['Shape obtained from the SDWBA.jl github repository. '
    'This is not necessarily the original source of the shape.']

    if m.aphiaid not in aphiaID_cache:
        print(f'Querying WoRMS for aphiaID {m.aphiaid}')
        r = requests.get(worms_url + str(m.aphiaid))
        if r.status_code == 200:
            aphiaID_cache[m.aphiaid] = r.json()
        else:
            print('Failed to get record for aphiaID = {m.aphiaid}')

    for attr in ['class', 'order', 'family', 'genus']:
        specimen[attr] = aphiaID_cache[m.aphiaid][attr]
    specimen['species'] = aphiaID_cache[m.aphiaid]['scientificname']

    specimen['vernacular_names'] = [m.vernacular_name]
    specimen['reference'] = m.source

    specimen.update({'specimen_name': m.name, 'specimen_condition': 'unknown',
                     'straightened': True, 'smoothed': True, 'rotated': True,
                     'length': m.length,
                     'length_units': 'm',
                     'sex': 'unknown',
                     'length_type': 'unknown', 'shape_type': 'outline',
                     'shapes': []})

    shape = {'anatomical_feature': 'body',
             'shape_units': 'm',
             'boundary': bt.fluid_filled,
             'x': m.rv_pos[:, 0],
             'y': m.rv_pos[:, 1],
             'z': m.rv_pos[:, 2],
             'height': m.a*2,
             'width': m.a*2,
             'mass_density_ratio': m.g,
             'sound_speed_ratio': m.h}
    specimen['shapes'].append(shape)

    specimens.append(specimen)

# Convert the arrays to lists (to facilitate exporting to json and toml)
specimens_cp = copy.deepcopy(specimens)
for ds in specimens_cp:
    for s in ds['shapes']:
        for k in s.keys():
            if isinstance(s[k], np.ndarray):
                s[k] = s[k].tolist()

# Write out each specimen to a echoSMS datastore format toml file
for sp in specimens_cp:
    if sp['model_type'] == 'DWBA':
        directory = 'SDWBA.jl_github'
    else:
        directory = 'NOAA_KRM'

    file_name = datastore_dir/'datasets'/directory/('specimen_' + sp['uuid'])
    # Add .toml suffix even when the name already has a full stop in it
    file_name = file_name.with_name(f'{file_name.name}.toml')
    Path.mkdir(file_name.parent, parents=True, exist_ok=True)
    with open(file_name, 'wb') as f:
        tomli_w.dump(sp, f)
