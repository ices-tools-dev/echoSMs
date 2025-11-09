"""

"""

# convert comsol data files into echoSMs datastore form

import numpy as np
import tomli_w
from pathlib import Path

dataset_base = Path(r'C:\Users\GavinMacaulay\OneDrive - Aqualyd Limited'
                    r'\Documents\Aqualyd\Projects\2024-05 NOAA modelling'
                    r'\working\anatomical data store\datasets')

dataset_dir = dataset_base/'GJM001'
raw_dir = dataset_base/'GJM001'/'data'/'extracted_fish'

lw = {'1': (.324, .214),
      '2': (.311, .1552),
      '3': (.350, .2131),
      '4': (.340, .2248),
      '5': (.279, .0969),
      '6': (.268, .0792)}

for comsol_data in raw_dir.glob('*.txt'):

    print(f'Processing {comsol_data.name}')
    with open(comsol_data, 'r') as f:
        f.readline()  # % Grid
        xpos = np.fromstring(f.readline(), sep=' ')
        ypos = np.fromstring(f.readline(), sep=' ')
        zpos = np.fromstring(f.readline(), sep=' ')

        c = np.empty((len(xpos), len(ypos), len(zpos)))
        rho = np.empty((len(xpos), len(ypos), len(zpos)))

        f.readline()  # % Data
        for k in range(len(zpos)):
            for j in range(len(ypos)):
                c[:,j,k] = np.fromstring(f.readline(), sep=' ')

        f.readline()  # % Data
        for k in range(len(zpos)):
            for j in range(len(ypos)):
                rho[:,j,k] = np.fromstring(f.readline(), sep=' ')

        # Dont' bother reading in the HU values

        # Rotate to fit the echoSMs coordinate system
        rho_r = np.rot90(rho, k=1, axes=(1, 2))
        c_r = np.rot90(c, k=1, axes=(1, 2))

        voxel_size = []
        for pos in [ypos, zpos, xpos]:  # yes, (y, z, x) ordering is correct!
            voxel_size.append(np.mean(np.diff(pos)).tolist())

    shape = {'name': 'body',
             'voxel_size': voxel_size,
             'voxel_size_units': 'm',
             'mass_density': rho_r.tolist(),
             'mass_density_units': 'kg/m^3',
             'sound_speed_compressional': c_r.tolist(),
             'sound_speed_compressional_units': 'm/s'}

    spec_id = str(int(comsol_data.stem[3:6]))

    specimen = {'specimen_id': spec_id,
                'specimen_condition': 'thawed',
                'length_type': 'total length',
                'shape_type': 'voxels',
                'length': lw[spec_id][0],
                'length_units': 'm',
                'weight': lw[spec_id][1],
                'weight_units': 'kg',
                'shapes': [shape]}

    print('Writing TOML file')
    name = 'specimen_' + comsol_data.name[:6]
    toml_file = (dataset_dir/name).with_suffix('.toml')
    with open(toml_file, 'wb') as f:
            tomli_w.dump({'specimens': [specimen]}, f)
