"""Play around with echoSMs code."""

import matplotlib.pyplot as plt
import numpy as np

from echosms.scattermodels import MSSModel, PSMSModel
from echosms.benchmarkdata import BenchMarkData
from echosms.referencemodels import ReferenceModels

rm = ReferenceModels()
print('Available reference models are:')
for n in rm.model_names():
    print('\t' + n)

bm = BenchMarkData()
bmf = bm.dataset_freq()

# %%
####################################################################################################
# Run the modal series solution model and plot the results along with the relevant benchmark data.

theta = np.array([90.0])  # [deg]
freqs = np.linspace(12, 400, num=200) * 1000.0  # [Hz]

mss = MSSModel()
print(f'The {mss.short_name} model supports boundary types of {mss.model_types}.')

m = rm.get_model_parameters('weakly scattering sphere')

ts, f, theta = mss.calculate_ts(**m, theta=theta, freqs=bmf['Frequency_kHz']*1e3)

plt.plot(f/1e3, ts, label='New code')
plt.plot(bmf['Frequency_kHz'], bmf['Sphere_WeaklyScattering'], label='Benchmark')
plt.xlabel('Frequency [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB]')
plt.legend()
plt.show()

# plot difference between benchmark values and newly calculated values
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
