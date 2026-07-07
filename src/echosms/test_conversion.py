""" """

from echosms import outline_to_surface, DATASTORE_URI

import requests

# Force use of IPV4 as sometimes IPV6 get() calls are very slow to complete
requests.packages.urllib3.util.connection.HAS_IPV6 = False

d = requests.get(DATASTORE_URI + 'v2/specimens?shape_type=outline')

for spec in d.json():
    print('Converting ' + spec['specimen_name'])

    dd = requests.get(DATASTORE_URI + 'v2/specimen/' + spec['uuid'] + '/data')

    specimen = dd.json()

    # convert all shapes in the specimen
    surfaces = []
    for s in specimen['shapes']:
        try:
            surfaces.append(outline_to_surface(s))
        except ValueError as e:
            print(f'\t{s["anatomical_feature"]}: {e}')
            continue

    specimen['shapes'] = surfaces
    specimen['shape_type'] = 'surface'

    # plot_specimen(specimen)
