"""Examples of using the echoSMs code to estimate scatter from objects."""

import matplotlib.pyplot as plt
import numpy as np

from echosms.scattermodels import MSSModel, PSMSModel, Utils
from echosms.benchmarkdata import BenchMarkData
from echosms.referencemodels import ReferenceModels

# Load the reference model defintiions
rm = ReferenceModels()
print('Available reference models are:')
for n in rm.model_names():
    print('\t' + n)

# Load the benchmark data (from Jech et al., 2015)
bm = BenchMarkData()
bmf = bm.dataset_freq()

# %%
####################################################################################################
# Run the modal series solution model with different parameters.

mss = MSSModel()
print(f'The {mss.short_name} model supports boundary types of {mss.model_types}.')

# Get the model parameters used in Jech et al. (2015) for a particular model.
# m is a dictionary that contains model parameters
s = rm.get_model_specification('weakly scattering sphere')
m = rm.get_model_parameters('weakly scattering sphere')  # a subset of s

# Calculate a single TS using the MSS model and the weakly scattering sphere model parameters.
ts = mss.calculate_ts_single(**m, theta=90.0, f=12000, model_type=s['model_type'])

# Add some variation to the model parameters
m['f'] = bmf['Frequency_kHz']*1e3  # [Hz]
m['theta'] = 90.0
# and run these parameters
ts = mss.calculate_ts(m, model_type='fluid filled')  # does model_type override the one in m?

# Plot the mss model and benchmark results
plt.plot(m['f']/1e3, ts, label='New code')
plt.plot(bmf['Frequency_kHz'], bmf['Sphere_WeaklyScattering'], label='Benchmark')
plt.xlabel('Frequency [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB]')
plt.legend()
plt.show()

# Plot difference between benchmark values and newly calculated mss model values
plt.plot(m['f']*1e-3, ts-bmf['Sphere_WeaklyScattering'])
plt.xlabel('Frequency [kHz]')
plt.ylabel(r'$\Delta$ TS [dB]')
plt.title('New TS - benchmark TS')
plt.show()

# Add more variations to the model parameters
m['f'] = np.linspace(12, 200, num=800) * 1e3  # [Hz]
m['target_rho'] = np.arange(1020, 1030, 1)  # [kg/m^3]
m['theta'] = [0, 90.0, 180.0]
params_df = Utils.df_from_dict(m)
# and run
ts = mss.calculate_ts(params_df, model_type='fluid filled')

# Add the ts to the params dataframe for ease of selecting and plotting the results
results = params_df
results['ts'] = ts

# plot some of the results
for rho in m['target_rho']:
    r = results.query('target_rho == @rho and theta==90')
    plt.plot(r['f']/1e3, r['ts'], label=f'{rho:.0f}')

plt.xlabel('Freq [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB] ')
plt.legend(title='Density [kg m$^{-3}$]')


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
# and is called the same way as for the dataframe
ts = mss.calculate_ts(params_xa, model_type='fluid filled')

# %%
####################################################################################################
# Run the prolate spheroid modal series model.

psms = PSMSModel()
print(f'This model supports boundary types of {psms.model_types}.')

m = rm.get_model_parameters('weakly scattering prolate spheroid')
theta = np.array([90.0])
freqs = np.linspace(12, 50, num=20) * 1000.0  # [Hz]

TS, f, theta = psms.calculate_ts(**m, theta=theta, freqs=[10e3])
