"""Calculate backscatter by a fluid sphere using Anderson (1950).

JASA, 22: 426-431, https://doi.org/10.1121/1.1906621
"""

import sys
from pathlib import Path
import numpy as np
from scipy.special import spherical_jn, spherical_yn
import matplotlib.pyplot as plt

###
# physical parameters of the sphere and surrounding water
# from Jech et al. (2015)
# weakly-scattering sphere
# speed of sound in water (m/s)
c_water = 1477.4
# speed of sound in the sphere (m/s)
c_sphere = 1480.3

# radius of the sphere (m)
# from Jech et al. (2015)
a = 0.01

# from Jech et al. (2015)
# weakly-scattering sphere
# density of the water (kg/m^3)
rho_water = 1026.8
# density of the sphere (kg/m^3)
rho_sphere = 1028.9

# sound speed (h) and density (g) contrasts
g = rho_sphere/rho_water
h = c_sphere/c_water

###
# model parameters
# minimum order, always = 0
order_min = 0
# maximum order
# the maximum order can be change to improve precision
order_max = 20
# number of orders
order_n = order_max+2
orders = range(order_min, order_n, 1)

# minimum acoustic frequency (Hz)
freq_min = 12000.0
# maximum acousic frequency (Hz)
freq_max = 200000.0
# frequency step (Hz)
freq_step = 2000.0
# the number of frequencies
freq_n = int((freq_max-freq_min)/freq_step)+1
# frequencies (Hz) at which to calculate scattering
freq_Hz = np.arange(freq_min, freq_max+freq_step, freq_step)

###
# print the parameters and confirm calculations
print('water density: {}, sound-speed water: {}'.format(rho_water, c_water))
print('sphere density: {}, sound-speed sphere: {}'.format(rho_sphere, c_sphere))
print('g: {}, h: {}'.format(round(g, 3), round(h, 3)))
print('sphere radius: {}'.format(a))
print('ka range: {} to {}'.format(round(2*np.pi*freq_min*a/c_water, 3),
                                  round(2*np.pi*freq_max*a/c_water, 3)))
answ = input('Continue? [y/n]')
if answ == 'n':
    sys.exit()

###
# set up output variables
# reflectivity coefficient
refl = []
# ka
ka = []

# real component
real = 0.0
# imaginary component
imag = 0.0
###
# reflectivity coefficient
# Bessel functions from SciPy
# spherical Bessel function of the 2nd kind is the Neumann function
# Anderson uses Neumann function notation
for f in freq_Hz:
    ka_sphere = (2*np.pi*f/c_sphere)*a
    ka_water = (2*np.pi*f/c_water)*a
    ka.append(ka_water)
    for m in range(order_max):
        sphjkas = (m/ka_sphere)*spherical_jn(m, ka_sphere)-spherical_jn(m+1, ka_sphere)
        sphjkaw = (m/ka_water)*spherical_jn(m, ka_water)-spherical_jn(m+1, ka_water)
        sphykas = (m/ka_sphere)*spherical_yn(m, ka_sphere)-spherical_yn(m+1, ka_sphere)
        sphykaw = (m/ka_water)*spherical_yn(m, ka_water)-spherical_yn(m+1, ka_water)
        alphaw = (2.*m+1.)*sphjkaw
        alphas = (2.*m+1.)*sphjkas
        beta = (2.*m+1)*sphykaw
        numer = (alphas/alphaw)*(spherical_yn(m, ka_water)/spherical_jn(m, ka_sphere)) - \
                ((beta/alphaw)*(g*h))
        denom = (alphas/alphaw)*(spherical_jn(m, ka_water)/spherical_jn(m, ka_sphere))-(g*h)
        cscat = numer/denom
        real = real+((-1.)**m)*(2.*m+1)/(1.+cscat**2)
        imag = imag+((-1.)**m)*(2.*m+1)*cscat/(1.+cscat**2)

    refl.append((2/ka_water)*np.sqrt(real**2+imag**2))
    imag = 0.0
    real = 0.0

# convert to numpy arrays
refl = np.array(refl, dtype=float)
ka = np.array(ka, dtype=float)

# convert to target strength (TS dB re m^2)
# S is the cross-sectional area of the sphere
S = np.pi*a**2
# 4pi is for backscatter
TS = 10*np.log10(refl**2*S)-10*np.log10(4*np.pi)

###
# plot reflectivity
# plt.plot(ka, refl)
# plt.plot(freq_Hz/1000., refl)
# plot TS
plt.plot(freq_Hz/1000., TS)
plt.show(block=False)

# write to a file
outfile = Path('./Anderson_output.csv')
with open(str(outfile), 'w', encoding='utf-8') as ofl:
    hdr = 'f_kHz,R,TS\n'
    ofl.write(hdr)
    for i in range(freq_n):
        ofl.write(','.join([str(round(freq_Hz[i]/1000, 1)),
                            str(round(refl[i], 9)), str(round(TS[i], 3))])+'\n')
