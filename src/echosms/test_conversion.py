""" """

from echosms import outline_to_surface, plot_specimen

import requests

api_URL = 'https://echosms-data-store-app-ogogm.ondigitalocean.app'

# Force use of IPV4 as sometimes IPV6 get() calls are very slow to complete
requests.packages.urllib3.util.connection.HAS_IPV6 = False

d = requests.get(api_URL + '/v2/specimens?shape_type=outline')

for spec in d.json():
    print('Converting ' + spec['id'])

    dd = requests.get(api_URL + '/v2/specimen/' + spec['id'] + '/data')

    specimen = dd.json()

    # convert all shapes in the specimen
    surfaces = []
    for s in specimen['shapes']:
        try:
            surfaces.append(outline_to_surface(s))
        except ValueError as e:
            print(f'{spec["id"]} - {s["anatomical_type"]}: {e}')
            continue

    specimen['shapes'] = surfaces
    specimen['shape_type'] = 'surface'

    # plot_specimen(specimen)

# %%
# this one causes an invalid surface mesh
spec_id = 'NOAA_KRM_280187_Corvina_20140331_003_Broadside'
d = requests.get(api_URL + '/v2/specimen/' + spec_id + '/data')
specimen = d.json()
surface = outline_to_surface(specimen['shapes'][1])
