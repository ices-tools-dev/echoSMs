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
angles = np.array([-np.pi])
freqs = np.linspace(12, 400, num=200) * 1000.0

mss = MSSModel()
print(f'This model supports boundary types of {mss.model_types}.')

m = rm.get_model_parameters('weakly scattering sphere')

f, angle, TS = mss.calculate_ts(**m, angles=angles, freqs=bmf['Frequency_kHz']*1e3)

plt.plot(f/1e3, TS, label='New code')
plt.plot(bmf['Frequency_kHz'], bmf['Sphere_WeaklyScattering'], label='Benchmark')
plt.xlabel('Frequency [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB]')
plt.legend()
plt.show()

# plot difference between benchmark values and newly calculated values
plt.plot(f*1e-3, TS-bmf['Sphere_WeaklyScattering'])
plt.xlabel('Frequency [kHz]')
plt.ylabel(r'$\Delta$ TS [dB]')
plt.title('New TS - benchmark TS')

# %%
####################################################################################################
psms = PSMSModel()
print(f'This model supports boundary types of {psms.boundary_types}.')
f, angle, TS = psms.calculate_ts(water_c, water_rho, sphere_r,
                                 angles, bmf['Frequency_kHz']*1e3, 'fluid filled',
                                 target_c=target_c, target_rho=target_rho, b=0.05)
