"""Play arond with echoSMs code."""

import matplotlib.pyplot as plt
import numpy as np

from src.echosms.scattermodels import MSSModel, PSMSModel
from src.echosms.benchmarkdata import BenchMarkData
from src.echosms.referencemodels import ReferenceModels

rm = ReferenceModels()
print('Available reference models are:')
for n in rm.model_names():
    print('\t' + n)

bm = BenchMarkData()
bmf = bm.dataset_freq()

# %%
####################################################################################################
theta = np.array([90.0])
freqs = np.linspace(12, 400, num=200) * 1000.0

mss = MSSModel()
print(f'The {mss.short_name} model supports boundary types of {mss.model_types}.')

m = rm.get_model_parameters('weakly scattering sphere')

f, theta, TS = mss.calculate_ts(**m, theta=theta, freqs=bmf['Frequency_kHz']*1e3)

plt.plot(f/1e3, TS, label='New code')
plt.plot(bmf['Frequency_kHz'], bmf['Sphere_WeaklyScattering'], label='Benchmark')
plt.xlabel('Frequency [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB]')
plt.legend()
plt.show()

# plot difference between benchmark values and newly calculated values
plt.plot(f*1e-3, TS[:, 0]-bmf['Sphere_WeaklyScattering'])
plt.xlabel('Frequency [kHz]')
plt.ylabel(r'$\Delta$ TS [dB]')
plt.title('New TS - benchmark TS')
plt.show()

# %%
####################################################################################################
psms = PSMSModel()
print(f'This model supports boundary types of {psms.model_types}.')

m = rm.get_model_parameters('weakly scattering prolate spheroid')
theta = np.array([90.0])

f, theta, TS = psms.calculate_ts(**m, theta=theta, freqs=[10e3])
