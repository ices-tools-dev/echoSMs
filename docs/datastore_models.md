# Using datastore shapes with echoSMs

This section contains examples of using echoSMs datastore data.

## Calculating TS from a datastore specimen

Here is an example of getting model shapes from the datastore and estimating the target strength using an echoSMs model.

```py
import echosms
import requests
import numpy as np
import matplotlib.pyplot as plt

# The current location of the echoSMs datastore server
baseURI = 'https://echosms-data-store-app-ogogm.ondigitalocean.app/'

# Create an instance of the echoSMs KRM model for use below
m = echosms.KRMModel()

# Get all the datastore organisms from the CLAY_HORNE dataset.
# This returns the metadata about the specimens but no shape information.
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
```

## Converting between from echoSMs shapes

### Surface to outline

This code shows how to load an STL 3D triangular mesh and convert it into an echoSMs outline shape.
It can then be used with echoSMs models that use outlines (e.g., KRM, DWBA).

```py
from echosms import surface_to_outline, surface_from_stl, plot_specimen

# Load a example STL file (you'll need to provide your own)
shape = surface_from_stl('length_44_cm_body.stl',
                          dim_scale=1.0,
                          anatomical_type='body',
                          boundary='pressure-release')

# Flip the STL mesh around to fit the echoSMs coordinate system.
# This step will depend on how your mesh is oriented
x = shape['x']
y = shape['y']
z = shape['z']

# The shape is centered on the y and z axis
shape['x'] = [-v for v in z]
shape['y'] = [v- sum(x)/len(x)  for v in x]
shape['z'] = [v- sum(y)/len(y)  for v in y]

# Add the shape into an echoSMs specimen metadata structure so it can
# be plotted using the echoSMs plot_specimen() function
specimen = {'specimen_id': 'A',
            'specimen_condition': 'fresh',
            'length': 0.044,
            'length_units': 'm',
            'length_type': 'total length',
            'shape_type': 'surface',
            'shapes': [shape]}

plot_specimen(specimen)

# Do the conversion. For the moment, this function expects an echoSMs
# shape data structure but it may be more convenient for it to accept
# an echoSMs specimen data structure.
# Note: the particulars of how the metadata are structured may change
# as the datastore data structures are refined.
shape = surface_to_outline(specimen['shapes'][0], slice_thickness=0.005)

# Update the specimen metadata structure with the outline shape
specimen['shape_type'] = 'outline'
specimen['shapes'] = [shape]

plot_specimen(specimen)

# It's not shown here, but the next steps are to use krmorganism_from_datastore()
# or dwba_from_datastore() to convert the shape into the form that the relevant
# echoSMs models require.

```

### Outline to surface

This code shows how to convert an echoSMs outline shape into an echoSMs surface shape, using a shape from the echoSMs anatomical datastore.

```py
import requests
from echosms import outline_to_surface, plot_specimen

# Get an outline shape from the echoSMs anatomical datastore
baseURI = 'https://echosms-data-store-app-ogogm.ondigitalocean.app/'
r = requests.get(baseURI + 'v2/specimen/CLAY_HORNE_B/data')
specimen = r.json()

# Plot the outline shapes - there will be a body and swimbladder shape
plot_specimen(specimen)

# Convert the shapes to surfaces.
# For the moment, outline_to_surface expects an echoSMs shape data
# structure but it may be more convenient for it to accept an echoSMs
# specimen data structure.
surfaces = []
for shape in specimen['shapes']:
    surfaces.append(outline_to_surface(shape))

# And update the specimen dict with the shapes and shape type
specimen['shapes'] = surfaces
specimen['shape_type'] = 'surface'

# Plot the surface shapes
plot_specimen(specimen)
```
