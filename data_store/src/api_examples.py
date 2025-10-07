"""Examples that use the echoSMS RESTful API."""
# /// script
# dependencies = ['requests', 'pandas', 'seaborn', 'Pillow', 'matplotlib']
# ///

import requests
import pandas as pd
import numpy as np
import copy
import seaborn as sns
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

# API documentation is available here:
# https://echosms-data-store-app-ogogm.ondigitalocean.app/docs

baseURI = 'http://127.0.0.1:8000/'
baseURI = 'https://echosms-data-store-app-ogogm.ondigitalocean.app/'

# %%
# Examples using the v1 version of the API
ds = []

print('Getting list of datasets')
d = requests.get(baseURI + 'v1/datasets')

if d.status_code == 200:
    print(f'Received {len(d.json())} datasets')

    # for each dataset in the reply
    for dataset_id in d.json():
        # Get the full dataset data
        r = requests.get(baseURI + 'v1/dataset/' + dataset_id)

        if r.status_code == 200:
            row = r.json()
            plural = '' if len(row['specimens']) == 1 else 's'
            print(f'  Got {dataset_id} dataset ({row["vernacular_name"]})'
                  f' with {len(row["specimens"])} specimen' + plural)
            # create a row for each specimen in the dataset
            to_copy = ['specimen_id', 'length', 'weight']
            for s in row['specimens']:
                for a in to_copy:
                    if a in s:
                        row[a] = s[a]
                    elif a == 'weight':  # default value for weight not present
                        row[a] = np.nan
                ds.append(copy.deepcopy(row))

    # Put data datasets into a DataFrame for easier viewing
    df = pd.DataFrame(data=ds).set_index(['dataset_id', 'specimen_id'])
    print(df[['vernacular_name', 'model_type', 'shape_types']])

    # A plot of specimen length/weight, coloured by species.
    # Filter out data where weight is NaN (i.e., not present)
    obj = sns.scatterplot(data=df[df['weight'].notnull()], x='length', y='weight',
                          hue='vernacular_name', style='imaging_method')
    obj.set_title('Specimens with length and weight values')
    # Move legend to outside of the axes
    sns.move_legend(obj, 'upper right', bbox_to_anchor=(1.6, 1))
    plt.show()

    # Get an image of one of the shapes and show it locally (or put the URL
    # into a web browser manually)
    print('Getting a specimen shape image...')
    r = requests.get(baseURI + 'v1/specimen_image/CLAY_HORNE/B')

    if r.status_code == 200:
        plt.imshow(Image.open(BytesIO(r.content)))
        plt.axis('off')
        plt.show()

# %%
# Examples using the v2 version of the API

print('Getting specimen metadata')
d = requests.get(baseURI + 'v2/specimens')

if d.status_code == 200:
    df = pd.DataFrame(data=d.json())
    print(df[['vernacular_name', 'model_type']])

    # A plot of specimen length/weight, coloured by species.
    # Filter out data where weight is NaN (i.e., not present)
    obj = sns.scatterplot(data=df[df['weight'].notnull()],
                          x='length', y='weight',
                          hue='vernacular_name', style='imaging_method')
    obj.set_title('Specimens with length and weight values')
    # Move legend to outside of the axes
    sns.move_legend(obj, 'upper right', bbox_to_anchor=(1.6, 1))
    plt.show()

    # Get an image of one of the shapes and show it locally (or put the URL
    # into a web browser manually)
    print('Getting a specimen shape image...')
    r = requests.get(baseURI + 'v2/specimen/' + 'CLAY_HORNE_B' + '/image')

    if r.status_code == 200:
        plt.imshow(Image.open(BytesIO(r.content)))
        plt.axis('off')
        plt.show()


# %%
# An example showing how to get all specimens metadata and shapes from the datastore
# and store (and access) them locally.

d = requests.get(baseURI + 'v2/specimens')

if d.status_code == 200:
    ds = []
    for s in d.json():  # iterate over all specimens in the datastore
        ds.append(s)

        print(f'Getting shape(s) for specimen {s["id"]}')
        shape = requests.get(baseURI + '/v2/specimen/' + s['id'] + '/shape')
        ds[-1]['shapes'] = shape.json()

    # Put into a Pandas dataframe
    df = pd.DataFrame(data=ds)

    # Save the dataframe to a compressed file for later use
    df.to_pickle('echosms_anatomical_datastore.gz')

    # That file can be read back and used without
    # online access to the echoSMs datastore API
    dff = pd.read_pickle('echosms_anatomical_datastore.gz')

    # An example of querying the dataframe
    print(dff.query('genus == "Gadus"')[['id', 'vernacular_name', 'shape_type', 'imaging_method']])

    # The shape data is in the 'shape' column, for example:
    print(dff.iloc[0]['shapes'])
