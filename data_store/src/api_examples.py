"""Examples that use the echoSMS RESTful API."""

import requests
import pandas as pd
import copy
import seaborn as sns
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

# API documentation is available here:
# https://web-c589h8dkt0qi.up-de-fra1-k8s-1.apps.run-on-seenode.com/docs

baseURI = 'http://127.0.0.1:8000/'
baseURI = 'https://web-c589h8dkt0qi.up-de-fra1-k8s-1.apps.run-on-seenode.com/'

ds = []

print('Getting list of datasets')
d = requests.get(baseURI + 'v1/datasets')
if d.status_code == 200:
    print(f'Received {len(d.json())} datasets')

    # for each dataset in the reply
    for dataset_id in d.json():
        # Get the full dataset data
        print(f'  Getting {dataset_id} dataset')

        r = requests.get(baseURI + 'v1/dataset/' + dataset_id)

        if r.status_code == 200:
            row = r.json()

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

    # Get an image of one of the shapes and show it locally (or put the URL
    # into a web browser manually)
    r = requests.get(baseURI + 'v1/specimen_image/CLAY_HORNE/B')
    if r.status_code == 200:
        image = Image.open(BytesIO(r.content))
        plt.imshow(image)
        plt.axis('off')
        plt.show()

    # A plot of specimen lengt/weight, coloured by species. Quite a few of the current
    # specimens don't have a weight, so they show as zero in the plot.
    obj = sns.scatterplot(data=df, x='length', y='weight',
                          hue='vernacular_name', style='imaging_method')
    sns.move_legend(obj, 'upper right', bbox_to_anchor=(1.6, 1))
