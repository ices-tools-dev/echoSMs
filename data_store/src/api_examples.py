"""Examples that use the echoSMS RESTful API."""
# /// script
# dependencies = ['requests', 'pandas', 'seaborn', 'Pillow', 'matplotlib']
# ///

import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pprint

# API documentation is available here:
# https://echosms-data-store-app-ogogm.ondigitalocean.app/docs

baseURI = 'http://127.0.0.1:8000/'
baseURI = 'https://echosms-data-store-app-ogogm.ondigitalocean.app/'

# %%
# Examples using the v2 version of the API

print('Getting all specimen metadata')
d = requests.get(baseURI + 'v2/specimens')

if d.status_code == 200:
    df = pd.DataFrame(data=d.json())
    print(df[['vernacular_names', 'model_type']])

    # A plot of specimen length/weight, coloured by species.
    # Filter out data where weight is NaN (i.e., not present)
    obj = sns.scatterplot(data=df[df['weight'].notnull()],
                          x='length', y='weight',
                          hue='species', style='imaging_method')
    obj.set_title('Specimens with length and weight values')
    # Move legend to outside of the axes
    sns.move_legend(obj, 'upper right', bbox_to_anchor=(1.6, 1))
    plt.show()


# %%
# An example showing how to get multiple specimen metadata and shapes from the datastore
# and store (and access) them locally.

# Get all specimens with shape type of 'outline'.
d = requests.get(baseURI + 'v2/specimens?shape_type=outline')

if d.status_code == 200:
    ds = []
    for s in d.json():  # iterate over all specimens with in the datastore
        print(f'Getting all data for specimen {s["specimen_name"]}')
        specimen = requests.get(baseURI + '/v2/specimen/' + s['uuid'] + '/data')
        ds.append(specimen.json())

    # Put into a Pandas dataframe
    df = pd.DataFrame(data=ds)

    # Save the dataframe to a compressed file for later use
    df.to_pickle('downloaded_anatomical_datastore.gz')

    # That file can be read back and used without
    # online access to the echoSMs datastore API
    dff = pd.read_pickle('downloaded_anatomical_datastore.gz')

    # An example of querying the dataframe
    print(dff.query('genus == "Gadus"')[['vernacular_names', 'shape_type', 'imaging_method']])

    # The shape data is in the 'shape' column, for example:
    pprint.pprint(dff.iloc[0]['shapes'])
