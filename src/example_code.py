# %%
"""Examples of using the echoSMs code to estimate scatter from objects."""

import matplotlib.pyplot as plt
import numpy as np

from echosms import MSSModel, PSMSModel, DCMModel
from echosms import BenchmarkData
from echosms import ReferenceModels
from echosms import as_dataframe, as_dataarray

# Load the reference model defintiions
rm = ReferenceModels()
print('Available reference models are:')
for n in rm.names():
    print('\t' + n)

# Load the benchmark data (from Jech et al., 2015)
bm = BenchmarkData()
bmf = bm.freq_dataset
bmt = bm.angle_dataset

# %% ###############################################################################################
# Run the benchmark models and compare to the frequency-varying benchmark results.

# This is the mapping between model name from ReferenceModels and the appropriate column of data in
# BenchMarkData and which model to use.
models = {'mss': [('weakly scattering sphere', 'Sphere_WeaklyScattering'),
                  ('fixed rigid sphere', 'Sphere_Rigid'),
                  ('pressure release sphere', 'Sphere_PressureRelease'),
                  ('gas filled sphere', 'Sphere_Gas'),
                  ('spherical fluid shell with pressure release interior',
                   'ShellSphere_PressureRelease'),
                  ('spherical fluid shell with gas interior', 'ShellSphere_Gas'),
                  ('spherical fluid shell with weakly scattering interior',
                   'ShellSphere_WeaklyScattering')],
          'dcm': [('fixed rigid finite cylinder', 'Cylinder_Rigid'),
                  ('pressure release finite cylinder', 'Cylinder_PressureRelease'),
                  ('gas filled finite cylinder', 'Cylinder_Gas'),
                  ('weakly scattering finite cylinder', 'Cylinder_WeaklyScattering')],
          # 'psms': [('fixed rigid prolate spheroid', 'ProlateSpheroid_Rigid'),
          #          ('pressure release prolate spheroid', 'ProlateSpheroid_PressureRelease'),
          #          ('gas filled prolate spheroid', 'ProlateSpheroid_Gas'),
          #          ('weakly scattering prolate spheroid', 'ProlateSpheroid_WeaklyScattering')]
          }

for model, names in models.items():
    if model == 'mss':
        mod = MSSModel()
    elif model == 'psms':
        mod = PSMSModel()
    elif model == 'dcm':
        mod = DCMModel()
    else:
        pass

    print(f'The {mod.short_name.upper()} ({mod.long_name}) model supports boundary '
          f'types of {mod.boundary_types}.')

    for name in names:
        # Get the model parameters used in Jech et al. (2015) for a particular model.
        s = rm.specification(name[0])
        m = rm.parameters(name[0])

        # Add frequencies and angle to the model parameters
        m['f'] = bm.freq_dataset['Frequency_kHz']*1e3  # [Hz]
        m['theta'] = 90.0

        # and run these
        ts = mod.calculate_ts(m)

        jech_index = np.mean(np.abs(ts - bmf[name[1]]))

        # Plot the mss model and benchmark results
        fig, axs = plt.subplots(2, 1, sharex=True)
        axs[0].plot(m['f']/1e3, ts, label='echoSMs')
        axs[0].plot(bmf['Frequency_kHz'], bmf[name[1]], label='Benchmark')
        axs[0].set_ylabel('TS re 1 m$^2$ [dB]')
        axs[0].legend(frameon=False, fontsize=6)

        # Plot difference between benchmark values and newly calculated mss model values
        axs[1].plot(m['f']*1e-3, ts-bmf[name[1]], color='black')
        axs[1].set_xlabel('Frequency [kHz]')
        axs[1].set_ylabel(r'$\Delta$ TS [dB]')
        axs[1].annotate(f'{jech_index:.2f} dB', (0.05, 0.80), xycoords='axes fraction',
                        backgroundcolor=[.8, .8, .8])
        plt.suptitle(name[0])
        plt.show()

# %% ###############################################################################################
# Run the benchmark models and compare to the angle-varying benchmark results.
models = {'dcm': [('fixed rigid finite cylinder', 'Cylinder_Rigid'),
                  ('pressure release finite cylinder', 'Cylinder_PressureRelease'),
                  ('gas filled finite cylinder', 'Cylinder_Gas'),
                  ('weakly scattering finite cylinder', 'Cylinder_WeaklyScattering')]
          }

for model, names in models.items():
    if model == 'mss':
        mod = MSSModel()
    elif model == 'psms':
        mod = PSMSModel()
    elif model == 'dcm':
        mod = DCMModel()
    else:
        pass

for name in names:
    # Get the model parameters used in Jech et al. (2015) for a particular model.
    s = rm.specification(name[0])
    m = rm.parameters(name[0])

    # Add frequencies and angle to the model parameters
    m['f'] = 38000  # [Hz]
    m['theta'] = bmt['Angle_deg']

    # and run these
    ts = mod.calculate_ts(m)

    jech_index = np.mean(np.abs(ts - bmt[name[1]]))

    # Plot the mss model and benchmark results
    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].plot(m['theta'], ts, label='echoSMs')
    axs[0].plot(bmt['Angle_deg'], bmt[name[1]], label='Benchmark')
    axs[0].set_ylabel('TS re 1 m$^2$ [dB]')
    axs[0].legend(frameon=False, fontsize=6)

    # Plot difference between benchmark values and newly calculated mss model values
    axs[1].plot(m['theta'], ts-bmt[name[1]], color='black')
    axs[1].set_xlabel('Angle (°)')
    axs[1].set_ylabel(r'$\Delta$ TS [dB]')
    axs[1].annotate(f'{jech_index:.2f} dB', (0.05, 0.80), xycoords='axes fraction',
                    backgroundcolor=[.8, .8, .8])
    plt.suptitle(name[0])
    plt.show()

# %% ###############################################################################################
# Some other ways to run models.

mss = MSSModel()

# Can add more variations to the model parameters
m = rm.parameters('weakly scattering sphere')
m['f'] = np.linspace(12, 200, num=800) * 1e3  # [Hz]
m['target_rho'] = np.arange(1020, 1030, 1)  # [kg/m^3]
m['theta'] = [0, 90.0, 180.0]
# can convert this to a dataframe
models_df = as_dataframe(m)
# could also make a DataFrame of parameters that are not just the combination of all input
# parameters. This offers a way to specify a more tailored set of model parameters.

print(f'Running {len(models_df)} models')
# and run
ts = mss.calculate_ts(models_df, multiprocess=True)

# And can then add the ts to the params dataframe for ease of selecting and plotting the results
models_df['ts'] = ts

# plot some of the results
for rho in m['target_rho']:
    r = models_df.query('target_rho == @rho and theta==90')
    plt.plot(r['f']/1e3, r['ts'], label=f'{rho:.0f}')

plt.xlabel('Freq [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB] ')
plt.legend(title='Density [kg m$^{-3}$]')
plt.show()

# %% ###############################################################################################
# Example of model parameters not from the benchmarks
params = {'medium_rho': [1000, 1250, 1500],
          'medium_c': np.arange(1400, 1600, 100),
          'f': np.linspace(12, 100, num=400) * 1000,
          'theta': np.arange(0, 180, 1),
          'a': 0.07,
          'boundary_type': 'fluid filled',
          'target_c': 1450,
          'target_rho': 1250}

# Instead of converting those to a dataframe, an xarray can be used.
params_xa = as_dataarray(params)

# how many models runs would that be?
print(f'Running {np.prod(params_xa.shape)} models!')

# and is called the same way as for the dataframe
if False:  # cause it takes a long time to run (as multiprocess is not enabled internally)
    ts = mss.calculate_ts(params_xa, multiprocess=True)

# and it can be inserted into params_xa
# TODO once the data is returned in an appropriate form
