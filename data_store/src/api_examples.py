"""Examples that use the echoSMS RESTful API."""
# /// script
# dependencies = ['requests', 'pandas', 'seaborn', 'Pillow', 'matplotlib']
# ///

import requests
import pandas as pd
import copy
import seaborn as sns
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

# API documentation is available here:
# https://echosms-data-store-app-ogogm.ondigitalocean.app/docs

baseURI = 'http://127.0.0.1:8000/'
baseURI = 'https://echosms-data-store-app-ogogm.ondigitalocean.app/'

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
                        row[a] = 0.0
                ds.append(copy.deepcopy(row))

    # Put data datasets into a DataFrame for easier viewing
    df = pd.DataFrame(data=ds).set_index(['dataset_id', 'specimen_id'])
    print(df[['vernacular_name', 'model_type', 'shape_data_types']])

    # A plot of specimen length/weight, coloured by species. Quite a few of the current
    # specimens don't have a weight, so they show as zero in the plot.
    obj = sns.scatterplot(data=df, x='length', y='weight',
                          hue='vernacular_name', style='imaging_method')
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
