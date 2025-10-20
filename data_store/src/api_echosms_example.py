"""An example of how to use echoSMs with model shapes from the echoSMs datastore API."""
# /// script
# dependencies = ['echosms', 'requests', 'numpy', 'matplotlib']
# ///

import echosms
import requests
import numpy as np
import matplotlib.pyplot as plt

# The current location of the echoSMs datastore server
baseURI = 'https://echosms-data-store-app-ogogm.ondigitalocean.app/'

# Create an instance of the echoSMs KRM model for use below
m = echosms.KRMModel()

# Get all the datastore organisms from the CLAY_HORNE dataset. This returns the metadata
# about the specimens but no shape information.
r = requests.get(baseURI + 'v2/specimens/?dataset_id=CLAY_HORNE')

for o in r.json():
    print(f'Processing specimen {o["specimen_id"]} from the {o["dataset_id"]} dataset')

    # Get the organism data (including the shape) from the datastore
    r = requests.get(baseURI + 'v2/specimen/' + o['id'] + '/data')
    if r.status_code != 200:
        print(f'Request for data from specimen {o["id"]} failed - skipping')
        continue

    # Get the model data out of the requests object
    s = r.json()

    # Assemble the echoSMs model parameters
    p = {'medium_c': 1500,  # [m/s]
         'medium_rho': 1024,  # [kg/m^3]
         'theta': 90.0,  # [deg] dorsal aspect
         'f': np.arange(10, 201, 1)*1e3,  # [Hz]
         'organism': echosms.krmorganism_from_datastore(s['shapes'])}

    # Calculate the TS using those parameters
    ts = m.calculate_ts(p)

    # Add to a plot of all the TS results
    plt.plot(p['f']*1e-3, ts, label=s['specimen_id'])

plt.legend(title='Specimens')
plt.title('Dataset ' + s['dataset_id'])
plt.xlabel('Frequency [kHz]')
plt.ylabel('TS [dB re 1 m$^2$]')
plt.show()
