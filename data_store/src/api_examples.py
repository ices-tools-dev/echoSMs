"""Examples that use the echoSMS RESTful API."""

import requests
import pandas as pd
import copy
import seaborn as sns

baseURI = 'http://127.0.0.1:8000/'

ds = []

d = requests.get(baseURI + 'v1/datasets')
if d.status_code == 200:
    # for each dataset in the reply
    for dataset_id in d.json():
        # Get the full dataset data
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

    df = pd.DataFrame(data=ds).set_index(['dataset_id', 'specimen_id'])

    obj = sns.scatterplot(data=df, x='length', y='weight',
                          hue='vernacular_name', style='imaging_method')
    sns.move_legend(obj, 'upper right', bbox_to_anchor=(1.5, 1))

    print(df[['vernacular_name', 'model_type', 'shape_data_types']])
