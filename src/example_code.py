"""Examples of using the echoSMs code to estimate scatter from objects."""

import matplotlib.pyplot as plt
import numpy as np

from echosms.scattermodels import MSSModel, PSMSModel
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
# Run the modal series solution model and plot the results along with the relevant benchmark data.

theta = np.array([90.0])  # [deg]
freqs = np.linspace(12, 400, num=200) * 1000.0  # [Hz]

mss = MSSModel()
print(f'The {mss.short_name} model supports boundary types of {mss.model_types}.')

# Get the model parameters used in Jech et al. (2015) for a particular model.
# m is a dictionary that contains parameters that the calculate_ts() functions expect.
m = rm.get_model_parameters('weakly scattering sphere')

# Calculate the TS using the MSS model and the weakly scattering sphere model parameters.
ts, f, theta = mss.calculate_ts(**m, theta=theta, freqs=bmf['Frequency_kHz']*1e3)

# Plot the mss model and benchmark results
plt.plot(f/1e3, ts, label='New code')
plt.plot(bmf['Frequency_kHz'], bmf['Sphere_WeaklyScattering'], label='Benchmark')
plt.xlabel('Frequency [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB]')
plt.legend()
plt.show()

# Plot difference between benchmark values and newly calculated mss model values
plt.plot(f*1e-3, ts[:, 0]-bmf['Sphere_WeaklyScattering'])
plt.xlabel('Frequency [kHz]')
plt.ylabel(r'$\Delta$ TS [dB]')
plt.title('New TS - benchmark TS')
plt.show()

# %%
####################################################################################################
# Run the prolate spheroid modal series model.

psms = PSMSModel()
print(f'This model supports boundary types of {psms.model_types}.')

m = rm.get_model_parameters('weakly scattering prolate spheroid')
theta = np.array([90.0])
freqs = np.linspace(12, 50, num=20) * 1000.0  # [Hz]

TS, f, theta = psms.calculate_ts(**m, theta=theta, freqs=[10e3])
