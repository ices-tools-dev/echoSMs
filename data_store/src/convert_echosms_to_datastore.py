"""Convert echoSMs shape format.

Converts old echoSMs KRM and DWBA shape data format into the new echoSMs
anatomical data store metadata and shape formats.
"""
import collections
import copy
import numpy as np
from echosms import KRMdata, DWBAdata
from plot_specimen import plot_specimen
import tomli_w

# Datset template
dataset_t = {'dataset_id': "",
             'description': "",
             'anatomical_category': "",
             'anatomical_features': [],
             'date_first_added': "",
             'date_last_modified': "",
             'aphiaID': np.nan,
             'class': "",
             'order': "",
             'family': "",
             'genus': "",
             'species': "",
             'vernacular_name': "",
             'reference': '',
             'activity_name': "",
             'location': "",
             'latitude': np.nan,
             'longitude': np.nan,
             'depth': np.nan,
             'date_collection': "",
             'date_image': "",
             'investigator': [],
             'data_collection_description': "",
             'note': "",
             'imaging_method': "",
             'shape_method': "",
             'shape_method_processing': "",
             'model_type': "",
             'sound_speed_method': "",
             'mass_density_method': "",
             'shape_data_type': "outline",
             'dataset_size': np.nan,
             'specimens': []}

########################
# KRM models
d = KRMdata()

# group the models into datasets using the 'source' attribute.
dd = collections.defaultdict(list)

for n in d.names():
    m = d.model(n)
    dd[m.source].append(m.name)

datasets = []
for ds in dd.keys():

    # populate dataset metadata
    dataset = copy.deepcopy(dataset_t)
    dataset['reference'] = ds
    dataset['shape_method'] = 'outline'
    dataset['model_type'] = 'KRM'

    # create models in the dataset
    for n in dd[ds]:
        m = d.model(n)

        specimen = {'specimen_id': m.name, 'specimen_condition': '',
                    'length': np.nan, 'weight': np.nan,
                    'length_type': '', 'shapes': []}

        shape = {'shape': 'body',
                 'boundary': m.body.boundary,
                 'x': m.body.x,
                 'y': np.full(m.body.x.shape, 0.0),
                 'height': m.body.z_U - m.body.z_L,
                 'width': m.body.w,
                 'mass_density': m.body.rho,
                 'sound_speed_compressional': m.body.c}
        shape['z'] = shape['height']/2 + m.body.z_L
        specimen['shapes'].append(shape)

        for inc in m.inclusions:
            shape = {'shape': 'inclusion',
                     'boundary': inc.boundary,
                     'x': inc.x,
                     'y': inc.x * 0.0,
                     'height': inc.z_U - inc.z_L,
                     'width': inc.w,
                     'mass_density': inc.rho,
                     'sound_speed_compressional': inc.c}
            shape['z'] = shape['height']/2 + inc.z_L
            specimen['shapes'].append(shape)

        dataset['specimens'].append(specimen)

    datasets.append(dataset)

############################
# DWBA models
d = DWBAdata()
dd = collections.defaultdict(list)

for n in d.names():
    m = d.model(n)
    dd[m.source].append(m.name)

for ds in dd.keys():

    # populate dataset metadata
    dataset = copy.deepcopy(dataset_t)
    dataset['reference'] = ds
    dataset['shape_method'] = 'outline'
    dataset['model_type'] = 'DWBA'

    for n in dd[ds]:
        m = d.model(n)

        specimen = {'specimen_id': m.name, 'specimen_condition': '',
                    'length': np.nan, 'weight': np.nan,
                    'length_type': '', 'shapes': []}

        shape = {'shape': 'body',
                 'boundary': 'fluid',
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

with open('all_datasets.toml', 'wb') as f:
    for ds in datasets_cp:
        tomli_w.dump(ds, f)
