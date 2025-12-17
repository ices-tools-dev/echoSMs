"""Convert echoSMs shape format.

Converts old echoSMs KRM and DWBA shape data format into the new echoSMs
anatomical data store metadata and shape formats.
"""
import collections
import copy
import numpy as np
from datetime import date
from echosms import KRMdata, DWBAdata, outline_from_krm, boundary_type as bt
import tomli_w
import requests
from pathlib import Path


datastore_dir = Path(r'C:\Users\GavinMacaulay\OneDrive - Aqualyd Limited\Documents\Aqualyd'
                     r'\Projects\2024-05 NOAA modelling\working\anatomical data store')

worms_url = 'https://www.marinespecies.org/rest/AphiaRecordByAphiaID/'

# Datset template
dataset_t = {  # 'dataset_id': "",
             'description': "",
             'anatomical_category': "organism",
             'date_first_added': date.today().strftime('%Y-%m-%d'),
             'date_last_modified': date.today().strftime('%Y-%m-%d'),
             'aphiaID': 1,
             'class': "",
             'order': "",
             'family': "",
             'genus': "",
             'species': "",
             'vernacular_name': "",
             'reference': '',
             # 'activity_name': "",
             # 'location': "",
             # 'latitude': np.nan,
             # 'longitude': np.nan,
             # 'depth': np.nan,
             'date_collection': "unknown",
             'date_image': "",
             'investigators': [],
             'data_collection_description': "",
             'note': "",
             'imaging_method': "unknown",
             'shape_method': "unknown",
             'shape_method_processing': "unknown",
             'model_type': "",
             'sound_speed_method': "unknown",
             'mass_density_method': "unknown",
             'specimens': []}

if 'aphiaID_cache' not in locals():
    aphiaID_cache = {}

########################
# KRM models
d = KRMdata()

# group the models into datasets using the 'aphiaid' (aka species) attribute.
dd = collections.defaultdict(list)

for n in d.names():
    m = d.model(n)
    dd[m.aphiaid].append(m.name)

datasets = []
for aphiaid in dd.keys():

    # populate dataset metadata
    dataset = copy.deepcopy(dataset_t)
    dataset['aphiaID'] = aphiaid
    dataset['shape_method'] = 'unknown'
    dataset['model_type'] = 'KRM'
    dataset['description'] = 'Shape data for KRM models'
    dataset['note'] = 'Shape obtained from the KRM shapes available at '
    'https://www.fisheries.noaa.gov/data-tools/krm-model. '
    'This is not necessarily the original source of the shape.'

    # create models in the dataset
    for n in dd[aphiaid]:
        m = d.model(n)

        if m.aphiaid not in aphiaID_cache:
            print(f'Querying WoRMS for aphiaID {m.aphiaid}')
            r = requests.get(worms_url + str(m.aphiaid))
            if r.status_code == 200:
                aphiaID_cache[m.aphiaid] = r.json()
            else:
                print('Failed to get record for aphiaID = {m.aphiaid}')

        for attr in ['class', 'order', 'family', 'genus']:
            dataset[attr] = aphiaID_cache[m.aphiaid][attr]
        dataset['species'] = aphiaID_cache[m.aphiaid]['scientificname']

        dataset['vernacular_name'] = m.vernacular_name
        dataset['reference'] = m.source

        specimen = {'specimen_id': m.name, 'specimen_condition': 'unknown',
                    'length': m.length,
                    'length_units': 'm',
                    'sex': 'unknown',
                    'length_type': 'unknown', 'shape_type': 'outline',
                    'shapes': []}

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
                                     anatomical_type=a_type)
            shape['mass_density'] = len(inc.x) * [inc.rho]
            shape['mass_density_units'] = 'kg/m^3'
            shape['sound_speed_compressional'] = len(inc.x) * [inc.c]
            shape['sound_speed_compressional_units'] = 'm/s'
            shape['shape_units'] = "m"
            specimen['shapes'].append(shape)

        dataset['specimens'].append(specimen)

    datasets.append(dataset)

# ############################
# DWBA models
d = DWBAdata()
dd = collections.defaultdict(list)

for n in d.names():
    m = d.model(n)
    dd[m.aphiaid].append(m.name)

for aphiaid in dd.keys():

    # populate dataset metadata
    dataset = copy.deepcopy(dataset_t)
    dataset['aphiaID'] = aphiaid
    dataset['shape_method'] = 'unknown'
    dataset['model_type'] = 'DWBA'
    dataset['description'] = ''
    dataset['model_type'] = 'DWBA'
    dataset['note'] = 'Shape obtained from the SDWBA.jl github repository. '
    'This is not necessarily the original source of the shape.'

    for n in dd[aphiaid]:
        m = d.model(n)

        if m.aphiaid not in aphiaID_cache:
            print(f'Querying WoRMS for aphiaID {m.aphiaid}')
            r = requests.get(worms_url + str(m.aphiaid))
            if r.status_code == 200:
                aphiaID_cache[m.aphiaid] = r.json()
            else:
                print('Failed to get record for aphiaID = {m.aphiaid}')

        for attr in ['class', 'order', 'family', 'genus']:
            dataset[attr] = aphiaID_cache[m.aphiaid][attr]
        dataset['species'] = aphiaID_cache[m.aphiaid]['scientificname']

        dataset['vernacular_name'] = m.vernacular_name
        dataset['reference'] = m.source

        specimen = {'specimen_id': m.name, 'specimen_condition': 'unknown',
                    'length': m.length,
                    'length_units': 'm',
                    'sex': 'unknown',
                    'length_type': 'unknown', 'shape_type': 'outline',
                    'shapes': []}

        shape = {'anatomical_type': 'body',
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

        dataset['specimens'].append(specimen)
    datasets.append(dataset)

# Convert the arrays to lists (to facilitate exporting to json and toml)
datasets_cp = copy.deepcopy(datasets)
for ds in datasets_cp:
    for ss in ds['specimens']:
        for s in ss['shapes']:
            for k in s.keys():
                if isinstance(s[k], np.ndarray):
                    s[k] = s[k].tolist()

for ds in datasets_cp:
    if ds['model_type'] == 'DWBA':
        prefix = 'SDWBA.jl_github'
    else:
        prefix = 'NOAA_KRM'

    dataset_name = f'{prefix}_{ds["aphiaID"]}'
    dataset_file = datastore_dir/'datasets'/dataset_name/'metadata.toml'
    Path.mkdir(dataset_file.parent, parents=True, exist_ok=True)
    with open(dataset_file, 'wb') as f:
        tomli_w.dump(ds, f)
