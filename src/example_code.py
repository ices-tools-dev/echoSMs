# %%
"""Examples of using the echoSMs code to estimate scatter from objects."""

import matplotlib.pyplot as plt
import numpy as np
import trimesh

from echosms import MSSModel, PSMSModel, DCMModel, ESModel, PTDWBAModel, KAModel, DWBAModel
from echosms import HPModel, KRMModel
from echosms import BenchmarkData, JechEtAlData
from echosms import ReferenceModels
from echosms import as_dataframe, as_dataarray, boundary_type as bt
from echosms import create_dwba_spheroid, create_dwba_cylinder
from echosms import KRMdata
from echosms import DWBAdata

# Load the reference model defintiions
rm = ReferenceModels()
print('Available reference models are:\n')
print('\n'.join(rm.names()))

# Load the benchmark data (from Jech et al., 2015)
bm = BenchmarkData()


def plot_compare_freq(f1, ts1, label1, f2, ts2, label2, title):
    """Plot together two ts(f) result sets."""
    jech_index = np.nanmean(np.abs(np.array(ts1) - np.array(ts2)))
    # Plot the mss model and benchmark results
    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].plot(f1/1e3, ts1, label=label1)
    axs[0].plot(f2/1e3, ts2, '+', label=label2)
    axs[0].set_ylabel('TS re 1 m$^2$ [dB]')
    axs[0].legend(frameon=False, fontsize=6)

    # Plot difference between the two ts datasets
    axs[1].plot(f1/1e3, np.array(ts1)-np.array(ts2), color='black')
    axs[1].set_xlabel('Frequency [kHz]')
    axs[1].set_ylabel(r'$\Delta$ TS [dB]')
    axs[1].annotate(f'{jech_index:.2f} dB', (0.05, 0.80), xycoords='axes fraction',
                    backgroundcolor=[.8, .8, .8])
    plt.suptitle(title)
    plt.show()


def plot_compare_angle(theta1, ts1, label1, theta2, ts2, label2, title):
    """Plot together two ts(theta) result sets."""
    jech_index = np.nanmean(np.abs(np.array(ts1) - np.array(ts2)))

    # Plot the mss model and benchmark results
    fig, axs = plt.subplots(2, 1, sharex=True)
    axs[0].plot(theta1, ts1, label=label1)
    axs[0].plot(theta2, ts2, '+', label=label2)
    axs[0].set_ylabel('TS re 1 m$^2$ [dB]')
    axs[0].legend(frameon=False, fontsize=6)

    # Plot difference between benchmark values and newly calculated mss model values
    axs[1].plot(theta1, np.array(ts1)-np.array(ts2), color='black')
    axs[1].set_xlabel('Angle (°)')
    axs[1].set_ylabel(r'$\Delta$ TS [dB]')
    axs[1].annotate(f'{jech_index:.2f} dB', (0.05, 0.80), xycoords='axes fraction',
                    backgroundcolor=[.8, .8, .8])
    plt.suptitle(name)
    plt.show()


# %% ###############################################################################################
# Run the benchmark models and compare to the frequency-varying benchmark results.

models = ['weakly scattering sphere',
          'fixed rigid sphere',
          'pressure release sphere',
          'gas filled sphere',
          'spherical fluid shell with pressure release interior',
          'spherical fluid shell with gas interior',
          'spherical fluid shell with weakly scattering interior',
          'fixed rigid finite cylinder',
          'pressure release finite cylinder',
          'gas filled finite cylinder',
          'weakly scattering finite cylinder',
          'fixed rigid prolate spheroid',
          'pressure release prolate spheroid',
          # Gas filled is not yet supported
          # 'gas filled prolate spheroid',
          # weakly scattering takes a while to run, so leave it out for the moment
          # 'weakly scattering prolate spheroid',
          ]

for name in models:
    # Get the model parameters used in Jech et al. (2015) for a particular model.
    s = rm.specification(name)
    m = rm.parameters(name)

    # create the appropriate model instance
    match s['benchmark_model']:
        case 'mss':
            mod = MSSModel()
        case 'psms':
            mod = PSMSModel()
        case 'dcm':
            mod = DCMModel()
        case _:
            pass

    # Add frequencies that have non nan benchmark TS values to the model parameters
    bm_f, bm_ts = bm.freq_data(name)
    not_nan = ~np.isnan(bm_ts)

    m['f'] = bm_f[not_nan]
    bm_ts = bm_ts[not_nan]

    # No benchmark TS is available for this model, so add some sensible frequencies in
    if name == 'gas filled prolate spheroid':
        m['f'] = np.arange(12, 82, 2)*1e3

    m['theta'] = 90.0  # not needed for the mss model

    # and run the models
    ts = mod.calculate_ts(m, progress=True)

    # Cope with there being no benchmark TS for this model
    if name == 'gas filled prolate spheroid':
        bm_ts = m['f'] * np.nan

    plot_compare_freq(m['f'], ts, s['benchmark_model'], m['f'], bm_ts, 'Benchmark', name)

# %% ###############################################################################################
# Run the benchmark models and compare to the angle-varying benchmark results.
models = ['fixed rigid finite cylinder',
          'pressure release finite cylinder',
          'gas filled finite cylinder',
          'weakly scattering finite cylinder',
          'fixed rigid prolate spheroid',
          'pressure release prolate spheroid',
          # Gas filled is not yet tested to be correct
          'gas filled prolate spheroid',
          'weakly scattering prolate spheroid']

for name in models:
    # Get the model parameters used in Jech et al. (2015) for a particular model.
    s = rm.specification(name)
    m = rm.parameters(name)

    # create the appropriate model instance
    match s['benchmark_model']:
        case 'mss':
            mod = MSSModel()
        case 'psms':
            mod = PSMSModel()
        case 'dcm':
            mod = DCMModel()
        case _:
            pass

    # Add frequencies and angle to the model parameters
    m['f'] = 38000  # [Hz]
    bm_angle, bm_ts = bm.angle_data(name)
    m['theta'] = bm_angle

    # and run these
    ts = mod.calculate_ts(m, progress=True)

    plot_compare_angle(m['theta'], ts, 'echoSMs', m['theta'], bm_ts, 'Benchmark', name)

# %% ###############################################################################################
# Run non-benchmark models and compare to the relevant benchmark results.
####################################################################################################

# %% ##################################################
# Test the KAModel
# mesh = trimesh.load(r'..\docs\resources\herring.stl')
# mesh = trimesh.creation.cylinder(radius=0.01, height=0.07, sections=500)

name = 'fixed rigid sphere'
s = rm.specification(name)

mesh = trimesh.creation.icosphere(radius=s['a'], subdivisions=4)
m = {}
m['medium_c'] = s['medium_c']
m['phi'] = 0
m['theta'] = 90.0
m['mesh'] = mesh
m['boundary_type'] = bt.pressure_release

# Get the benchmark TS values
bm_f, bm_ts = bm.freq_data(name)
not_nan = ~np.isnan(bm_ts)

m['f'] = bm_f[not_nan]
bm_ts = bm_ts[not_nan]

mod = KAModel()

# and run the models
ts = mod.calculate_ts(m, progress=True)

plot_compare_freq(m['f'], ts, 'KA', m['f'], bm_ts, 'Benchmark', name)

#############################################################
# Now compare the echoSMs KA to the KA result in the paper
jetal = JechEtAlData()
ka_ts = jetal.data['Figure_01_Rigid-sphere']['Francis_Kirchhoff_TS']
plot_compare_freq(m['f'], ts, 'KA echoSMs', m['f'], ka_ts, 'KA paper', name)

# and again for a finite cylinder
name = 'fixed rigid finite cylinder'
s = rm.specification(name)
ka_ts = jetal.data['Figure_06_Rigid-Cylinder']['Francis_Kirchhoff_TS']

# default cylinder from trimesh lies along the z axis, so need to rotate it to lie along the x axis,
# hence the transform.
mesh = trimesh.creation.cylinder(
    radius=s['a'], height=s['b'],
    transform=trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0], [0, 0, 0]))
mesh = mesh.subdivide().subdivide()  # needed for better accuracy at higher frequencies
m['mesh'] = mesh
# m['mesh'].export('cylinder.stl')  # to view in a separate package (e.g., MeshLab)

ts = mod.calculate_ts(m, progress=True)
plot_compare_freq(m['f'], ts, 'KA echoSMs', m['f'], ka_ts, 'KA paper', name)

# %% ###################################################
# Run the DWBA model and compare to the benchmark results

model_names = ['weakly scattering sphere', 'weakly scattering prolate spheroid',
               'weakly scattering finite cylinder']
for name in model_names:

    m = rm.parameters(name)

    match rm.specification(name)['shape']:
        case 'prolate spheroid':
            rv_pos, rv_tan, a = create_dwba_spheroid(m['a'], m['b'])
        case 'sphere':
            rv_pos, rv_tan, a = create_dwba_spheroid(m['a'], m['a'])
        case 'finite cylinder':
            rv_pos, rv_tan, a = create_dwba_cylinder(m['a'], m['b'])

    m.pop('boundary_type')
    m.pop('b', None)

    # Get benchmark model for comparison
    f, bm_ts = bm.freq_data(name)

    m |= {'theta': 90, 'phi': 0, 'a': a, 'rv_pos': rv_pos, 'rv_tan': rv_tan, 'f': f}

    mod = DWBAModel()
    ts_dwba = mod.calculate_ts(m, progress=True)

    plot_compare_freq(f, bm_ts, 'benchmark', f, ts_dwba, 'dwba', name)

#########################################################
# And then compare to the angle varying benchmark results
models = ['weakly scattering prolate spheroid', 'weakly scattering finite cylinder']

for name in models:
    s = rm.specification(name)
    m = rm.parameters(name)

    match rm.specification(name)['shape']:
        case 'prolate spheroid':
            rv_pos, rv_tan, a = create_dwba_spheroid(m['a'], m['b'])
        case 'finite cylinder':
            rv_pos, rv_tan, a = create_dwba_cylinder(m['a'], m['b'])

    m.pop('boundary_type')
    m.pop('b', None)
    theta, bm_ts = bm.angle_data(name)

    m |= {'theta': theta, 'phi': 0, 'a': a, 'rv_pos': rv_pos, 'rv_tan': rv_tan, 'f': 38000}

    mod = DWBAModel()
    ts_dwba = mod.calculate_ts(m, progress=True)

    plot_compare_angle(theta, ts_dwba, 'DWBA', theta, bm_ts, 'Benchmark', name)

##########################################################
# And the DWBA and SDWBA on a real shape
dd = DWBAdata()

krill = dd.model('Generic krill (McGehee 1998)')

m = {'medium_c': 1500, 'medium_rho': 1024, 'phi': 0,
     'target_c': 1501, 'target_rho': 1025, 'a': krill.a, 'rv_pos': krill.rv_pos,
     'rv_tan': krill.rv_tan}

# m |= {'f': np.arange(12000, 120000, 1000), 'theta': 90}
m |= {'f': 38000, 'theta': np.arange(0, 360, 1)}
mod = DWBAModel()
dwba_ts = mod.calculate_ts(m)

# and then a SDWBA version of the same
m |= {'phase_sd': 20, 'num_runs': 100}
sdwba_ts = mod.calculate_ts(m, progress=True)

plt.plot(m['theta'], sdwba_ts, label='sdwba')
plt.plot(m['theta'], dwba_ts, label='dwba')
plt.legend()

# %% ###############################################################################################
# Use the ES model on a calibration sphere
name = 'WC38.1 calibration sphere'
p = rm.parameters(name)
p['f'] = np.arange(10, 100, 0.05) * 1e3  # [kHz]

es = ESModel()
ts = es.calculate_ts(p, progress=True)

plt.plot(p['f']*1e-3, ts)
plt.xlabel('Freq [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB] ')
plt.title(name)
plt.show()

# Can readily modify the parameters for a different sphere
p['a'] = 0.012/2
ts = es.calculate_ts(p)
plt.plot(p['f']*1e-3, ts)
plt.xlabel('Freq [kHz]')
plt.ylabel('TS re 1 m$^2$ [dB] ')
plt.title('WC12 calibration sphere')
plt.show()

# %% ###############################################################################################
# Try the high-pass model
mod = HPModel()
p = {'boundary_type': bt.fixed_rigid, 'shape': 'sphere', 'medium_c': 1500, 'a': 0.01,
     'f': np.arange(1, 400, 1)*1e3}
fixed_rigid = mod.calculate_ts(p)
p['boundary_type'] = bt.elastic
p |= {'medium_rho': 1024, 'target_c': 1600, 'target_rho': 1600}
elastic = mod.calculate_ts(p)
p['boundary_type'] = bt.fluid_filled
p |= {'medium_rho': 1024, 'target_c': 1510, 'target_rho': 1025}
fluid = mod.calculate_ts(p)

plt.semilogx(p['f']/1e3, fixed_rigid, label='fixed rigid')
plt.semilogx(p['f']/1e3, elastic, label='elastic')
plt.semilogx(p['f']/1e3, fluid, label='fluid filled')
plt.legend()
plt.xlabel('Frequency [kHz]')
plt.ylabel('TS re 1m$2$ [dB]')

# %% ###############################################################################################
# Try the KRM model and compare to the NOAA online KRM calculator results
mod = KRMModel()

fishes = ['Sardine', 'Cod', 'Bocaccio', 'SkipjackTuna_46.54cm']

for fname in fishes:
    fish = KRMdata().model(fname)
    fish.plot()

    # Create the dict that echoSMs models use and add required parameters
    p = {'medium_c': 1490, 'medium_rho': 1030, 'organism': fish, 'theta': 90,
         'f': np.arange(12, 121, 1)*1e3,
         'high_ka_medium': 'water', 'low_ka_medium': 'water'}
    # Note 'water' is used for the high_ka_medium and low_ka_medium parameters to
    # match the TS in the available from KRMdata() class (which came from the
    # online NOAA KRM calculator). To see the results when 'body' is used, uncomment these two
    # lines:
    # p['high_ka_medium'] = 'body'
    # p['low_ka_medium'] = 'body'

    krm_ts = mod.calculate_ts(p, progress=True)

    # Get the TS from the NOAA KRM webpage (cached locally)
    noaa_ts = KRMdata.ts(fname)
    plot_compare_freq(p['f'], krm_ts,
                      'KRM echoSMs', p['f'], noaa_ts[' TS (dB).1'], 'KRM NOAA', fname)

# %% ###############################################################################################
# Some other ways to run models.

mss = MSSModel()

# Can add more variations to the model parameters
m = rm.parameters('weakly scattering sphere')
m['f'] = np.linspace(12, 200, num=800) * 1e3  # [Hz]
m['target_rho'] = np.arange(1020, 1030, 1)  # [kg/m^3]
m['theta'] = [0, 90.0, 180.0]
# can convert this to a dataframe
models_df = as_dataframe(m, mss.no_expand_parameters)
# could also make a DataFrame of parameters that are not just the combination of all input
# parameters. This offers a way to specify a more tailored set of model parameters.

print(f'Running {len(models_df)} models')
# and run. This will return a Series
ts = mss.calculate_ts(models_df, multiprocess=True, progress=True)
models_df['ts'] = ts

# Alternatively, the ts results can be added to the dataframe that is passed in:
# ts = mss.calculate_ts(models_df, multiprocess=True, result_type='expand')

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
          'boundary_type': bt.fluid_filled,
          'target_c': 1450,
          'target_rho': 1250}

mss = MSSModel()

# Instead of converting params to a dataframe, an xarray can be used.
params_xa = as_dataarray(params, mss.no_expand_parameters)

# how many models runs would that be?
print(f'Running {np.prod(params_xa.shape)} models!')

# and is called the same way as for the dataframe. Use multiprocessing for this one as there
# are a lot of models to run.
mss.calculate_ts(params_xa, multiprocess=True, progress=False)

# Xarray selections and dimenions names can then be used
plt.plot(params_xa.f, params_xa.sel(theta=90, medium_rho=1000, medium_c=1600))

# %% ###############################################################################################
# Example of PT-DWBA model

# The benchmark sphere model
name = 'weakly scattering sphere'
m = rm.parameters(name)

# make a 3d matrix of 0's and 1's and set to 1 for the sphere
# and 0 for not the sphere
m['voxel_size'] = (0.0001, 0.0001, 0.0001)  # [m]
x = np.arange(-m['a'], m['a'], m['voxel_size'][0])
(X, Y, Z) = np.meshgrid(x, x, x)

m['volume'] = (np.sqrt(X**2 + Y**2 + Z**2) <= m['a']).astype(int)
m['theta'] = 90
m['phi'] = 0
m['rho'] = [m['medium_rho'], m['target_rho']]
m['c'] = [m['medium_c'], m['target_c']]
bm_f, bm_ts = bm.freq_data(name)
m['f'] = bm_f
# remove unneeded parameters
m = {k: v for k, v in m.items()
     if k not in ['boundary_type', 'a', 'medium_rho', 'medium_c', 'target_rho', 'target_c']}

pt = PTDWBAModel()
dwba_ts = pt.calculate_ts(m, progress=True)

plot_compare_freq(m['f'], dwba_ts, 'PT-DWBA', m['f'], bm_ts, 'Benchmark', name)

# So, this PT_DWBA on a weakly scattering sphere is also different from the benchmark
# TS values. Hmmmm. Now look at the difference between the PT-DWBA and MSS model runs...

mss = MSSModel()
mm = rm.parameters(name)
bm_f, bm_ts = bm.freq_data(name)
mm['f'] = bm_f
mm['theta'] = 90.0

mss_ts = mss.calculate_ts(mm, progress=True)

plot_compare_freq(mm['f'], dwba_ts, 'PT-DWBA', mm['f'], mss_ts, 'MSS', name)

########################################################
# And then the same thing, but for the prolate spheroid
name = 'weakly scattering prolate spheroid'
m = rm.parameters(name)
m['voxel_size'] = (0.0001, 0.0001, 0.0001)  # [m]
x = np.arange(-m['a'], m['a'], m['voxel_size'][0])
y = np.arange(-m['b'], m['b'], m['voxel_size'][0])
z = np.arange(-m['b'], m['b'], m['voxel_size'][0])
(X, Y, Z) = np.meshgrid(x, y, z, indexing='ij')

m['volume'] = ((Y**2 + Z**2)/m['b']**2 + X**2/m['a']**2) <= 1
m['theta'] = 90
m['phi'] = 0
m['rho'] = [m['medium_rho'], m['target_rho']]
m['c'] = [m['medium_c'], m['target_c']]
bm_f, bm_ts = bm.freq_data(name)
m['f'] = bm_f
# remove unneeded parameters
m = {k: v for k, v in m.items()
     if k not in ['boundary_type', 'a', 'b', 'medium_rho', 'medium_c', 'target_rho', 'target_c']}

pt = PTDWBAModel()
dwba_ts = pt.calculate_ts(m, multiprocess=False, progress=True)

plot_compare_freq(m['f'], dwba_ts, 'PT-DWBA', m['f'], bm_ts, 'Benchmark', name)
