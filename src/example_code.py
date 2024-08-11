"""Examples of using the echoSMs code to estimate scatter from objects."""

import matplotlib.pyplot as plt
import numpy as np

from echosms import MSSModel, PSMSModel
from echosms import BenchMarkData
from echosms import ReferenceModels
from echosms import Utils

# Load the reference model defintiions
rm = ReferenceModels()
print('Available reference models are:')
for n in rm.model_names():
    print('\t' + n)

# Load the benchmark data (from Jech et al., 2015)
bm = BenchMarkData()
bmf = bm.dataset_freq()

mss = MSSModel()
print(f'The {mss.short_name} model supports boundary types of {mss.model_types}.')

# %% ###############################################################################################
# Run the modal series solution model and compare to the benchmark values

# This is the mapping between model name from ReferenceModels and the appropriate column of data in
# BenchMarkData.
models = [('weakly scattering sphere', 'Sphere_WeaklyScattering'),
          ('fixed rigid sphere', 'Sphere_Rigid'),
          ('pressure release sphere', 'Sphere_PressureRelease'),
          ('gas filled sphere', 'Sphere_Gas'),
          ('spherical fluid shell with pressure release interior', 'ShellSphere_PressureRelease'),
          ('spherical fluid shell with gas interior', 'ShellSphere_Gas'),
          ('spherical fluid shell with weakly scattering interior', 'ShellSphere_WeaklyScattering')]

for model in models:
    # Get the model parameters used in Jech et al. (2015) for a particular model.
    s = rm.get_model_specification(model[0])
    m = rm.get_model_parameters(model[0])  # the subset of s with string items removed

    # Add frequencies and angle to the model parameters
    m['f'] = bmf['Frequency_kHz']*1e3  # [Hz] Use f from the benchmark to make it easy to compare
    m['theta'] = 90.0

    # and run these
    ts = mss.calculate_ts(m, model_type=s['model_type'])

    # Plot the mss model and benchmark results
    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].plot(m['f']/1e3, ts, label='echoSMs')
    axs[0].plot(bmf['Frequency_kHz'], bmf[model[1]], label='Benchmark')
    axs[0].set_ylabel('TS re 1 m$^2$ [dB]')
    axs[0].legend(frameon=False, fontsize=6)

    # Plot difference between benchmark values and newly calculated mss model values
    axs[1].plot(m['f']*1e-3, ts-bmf[model[1]], color='black')
    axs[1].set_xlabel('Frequency [kHz]')
    axs[1].set_ylabel(r'$\Delta$ TS [dB]')

    plt.suptitle(model[0])

# %% ###############################################################################################

# How to calculate a single TS using the MSS model
m = rm.get_model_parameters('weakly scattering sphere')
mss.calculate_ts_single(**m, theta=90.0, f=12000, model_type='fluid filled')

# %% ###############################################################################################

# Can add more variations to the model parameters
m = rm.get_model_parameters('weakly scattering sphere')
m['f'] = np.linspace(12, 200, num=800) * 1e3  # [Hz]
m['target_rho'] = np.arange(1020, 1030, 1)  # [kg/m^3]
m['theta'] = [0, 90.0, 180.0]
# can convert this to a dataframe
models_df = Utils.df_from_dict(m)
# could also make a DataFrame of parameters that are not just the combination of all input
# parameters. This offers a way to specify a more tailored set of model parameters.

print(f'Running {len(models_df)} models')
# and run
ts = mss.calculate_ts(models_df, model_type='fluid filled', multiprocess=True)

# And can then add the ts to the params dataframe for ease of selecting and plotting the results
models_df['ts'] = ts

# plot some of the results
for rho in m['target_rho']:
    r = models_df.query('target_rho == @rho and theta==90')
    plt.plot(r['f']/1e3, r['ts'], label=f'{rho:.0f}')

plt.xlabel('Freq [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB] ')
plt.legend(title='Density [kg m$^{-3}$]')

# %% ###############################################################################################
# Example of model parameters not from the benchmarks
params = {'medium_rho': [1000, 1250, 1500],
          'medium_c': np.arange(1400, 1600, 100),
          'f': np.linspace(12, 100, num=400) * 1000,
          'theta': np.arange(0, 180, 1),
          'a': 0.07,
          'target_c': 1450,
          'target_rho': 1250}

# Instead of converting those to a dataframe, an xarray can be used.
params_xa = Utils.xa_from_dict(params)

# how many models runs would that be?
print(f'Running {np.prod(params_xa.shape)} models!')

# and is called the same way as for the dataframe
ts = mss.calculate_ts(params_xa, model_type='fluid filled', multiprocess=True)

# %% ###############################################################################################
# Run the prolate spheroid modal series model.

psms = PSMSModel()
print(f'This model supports boundary types of {psms.model_types}.')

models_ps = [('fixed rigid prolate spheroid', 'ProlateSpheroid_Rigid'),
             ('pressure release prolate spheroid', 'ProlateSpheroid_PressureRelease'),
             ('gas filled prolate spheroid', 'ProlateSpheroid_Gas'),
             ('weakly scattering prolate spheroid', 'ProlateSpheroid_WeaklyScattering')]

# Notes:
# - There are no benchmark results for ProlateSpheroid_Gas as the model did not converge.
# - ProlateSpheroid_PressureRelease and _Rigid benchmark results are only available up to 80 kHz

for model in models_ps:
    # Get the model parameters used in Jech et al. (2015) for a particular model.
    s = rm.get_model_specification(model[0])
    m = rm.get_model_parameters(model[0])  # the subset of s with string items removed

    # Add frequencies and angle to the model parameters
    m['f'] = bmf['Frequency_kHz']*1e3  # [Hz] Use f from the benchmark to make it easy to compare
    m['theta'] = 90.0

    # and run these
    ts = psms.calculate_ts(m, model_type=s['model_type'])

    # Plot the mss model and benchmark results
    fig, axs = plt.subplots(2, 1, sharex=True)
    # axs[0].plot(m['f']/1e3, ts, label='echoSMs')
    axs[0].plot(bmf['Frequency_kHz'], bmf[model[1]], label='Benchmark')
    axs[0].set_ylabel('TS re 1 m$^2$ [dB]')
    # axs[0].legend(frameon=False, fontsize=6)

    # Plot difference between benchmark values and newly calculated mss model values
    # axs[1].plot(m['f']*1e-3, ts-bmf[model[1]], color='black')
    # axs[1].set_xlabel('Frequency [kHz]')
    # axs[1].set_ylabel(r'$\Delta$ TS [dB]')

    plt.suptitle(model[0])
