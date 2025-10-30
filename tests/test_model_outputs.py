"""Functions to test that models produce the correct results."""
import pytest
import numpy as np
import echosms


@pytest.fixture
def rm():
    """Provide a ReferenceModels instance."""
    return echosms.ReferenceModels()


# Test that models return correct TS values.

# Generally, each model is run for it's various boundary conditions at one size and frequency.
# This is likely to be sufficient to pick up when changes to model code changes the output.


###########################################################
# MSSModel
@pytest.mark.parametrize("reference_model, f, ts",
                    [('fixed rigid sphere', 38e3, -49.0894),
                     ('pressure release sphere', 38e3, -44.9979),
                     ('gas filled sphere', 38e3, -44.9889),
                     ('weakly scattering sphere', 38e3, -94.1345),
                     ('spherical fluid shell with pressure release interior', 38e3, -45.7530),
                     ('spherical fluid shell with gas interior', 38e3, -45.7758),
                     ('spherical fluid shell with weakly scattering interior', 38e3, -88.2482),])
def test_mssmodel(rm, reference_model, f, ts):
    mod = echosms.MSSModel()
    m = rm.parameters(reference_model)
    m['f'] = f

    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), "Incorrect TS value"


###########################################################
# DCMModel
@pytest.mark.parametrize("reference_model, f, theta, ts",
                         [('fixed rigid finite cylinder', 38e3, 90, -33.6223),
                          ('pressure release finite cylinder', 38e3, 90, -31.5363),
                          ('gas filled finite cylinder', 38e3, 90, -31.5626),
                          ('weakly scattering finite cylinder', 38e3, 90, -84.8007),])
def test_dcmmodel(rm, reference_model, f, theta, ts):
    mod = echosms.DCMModel()
    m = rm.parameters(reference_model)
    m['f'] = f
    m['theta'] = theta

    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), "Incorrect TS value"


###########################################################
# PSMSModel
@pytest.mark.parametrize("reference_model, f, theta, ts",
                         [('fixed rigid prolate spheroid', 38e3, 90, -30.0710),
                          ('pressure release prolate spheroid', 38e3, 90, -28.6241),
                          ('gas filled prolate spheroid', 38e3, 90, -28.6236),
                          ('weakly scattering prolate spheroid', 38e3, 90, -77.2005)])
def test_psmsmodel(rm, reference_model, f, theta, ts):
    mod = echosms.PSMSModel()
    m = rm.parameters(reference_model)
    m['f'] = f
    m['theta'] = theta

    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), "Incorrect TS value"


###########################################################
# ESModel
@pytest.mark.parametrize("reference_model, f, ts",
                         [('WC38.1 calibration sphere', 38e3, -42.3297),
                          ('Cu60 calibration sphere', 38e3, -33.5507),])
def test_esmodel(rm, reference_model, f, ts):
    mod = echosms.ESModel()
    m = rm.parameters(reference_model)
    m['f'] = f
    print(mod.calculate_ts(m))
    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), "Incorrect TS value"


###########################################################
# KRMModel
@pytest.mark.parametrize("fname, f, ts",
                         [('Sardine', 38e3, -46.6249),
                          ('Cod', 38e3, -34.1059),])
def test_krmmodel(rm, fname, f, ts):
    fish = echosms.KRMdata().model(fname)
    m = {'medium_c': 1490, 'medium_rho': 1030, 'organism': fish, 'theta': 90,
         'f': f, 'high_ka_medium': 'water', 'low_ka_medium': 'water'}
    mod = echosms.KRMModel()
    print(mod.calculate_ts(m))
    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), "Incorrect TS value"


###########################################################
# KAModel
def test_kamodel(rm):
    import trimesh
    name = 'fixed rigid sphere'
    s = rm.specification(name)

    p = {'medium_c': s['medium_c'], 'phi': 0, 'theta': 90.0,
         'mesh': trimesh.creation.icosphere(radius=s['a'], subdivisions=4),
         'boundary_type': 'pressure-release', 'f': 38e3}

    mod = echosms.KAModel()
    assert np.allclose(mod.calculate_ts(p), -44.4474, atol=0.0001), "Incorrect TS value"


###########################################################
# HPModel
@pytest.mark.parametrize('model, f, ts',
                         [('fixed-rigid', 38e3, -46.2576),
                          ('elastic', 38e3, -58.1926),
                          ('fluid-filled', 38e3, -94.4968),])
def test_hpmodel(model, f, ts):
    mod = echosms.HPModel()
    p = {'boundary_type': model, 'shape': 'sphere', 'medium_c': 1500, 'a': 0.01, 'f': f}
    match model:
        case 'fixed-rigid':
            assert np.allclose(mod.calculate_ts(p), ts, atol=0.0001), "Incorrect TS value"
        case 'elastic':
            p |= {'medium_rho': 1024, 'target_c': 1600, 'target_rho': 1600}
            assert np.allclose(mod.calculate_ts(p), ts, atol=0.0001), "Incorrect TS value"
        case 'fluid-filled':
            p |= {'medium_rho': 1024, 'target_c': 1510, 'target_rho': 1025}
            assert np.allclose(mod.calculate_ts(p), ts, atol=0.0001), "Incorrect TS value"


###########################################################
# PTDWBAModel
def test_ptdwbamodel(rm):
    name = 'weakly scattering sphere'
    p = rm.parameters(name)

    # make a 3d matrix of 0's and 1's and set to 1 for the sphere
    # and 0 for not the sphere
    p['voxel_size'] = (0.0001, 0.0001, 0.0001)  # [m]
    x = np.arange(-p['a'], p['a'], p['voxel_size'][0])
    (X, Y, Z) = np.meshgrid(x, x, x)

    p['volume'] = (np.sqrt(X**2 + Y**2 + Z**2) <= p['a']).astype(int)
    p['theta'] = 90
    p['phi'] = 0
    p['rho'] = [p['medium_rho'], p['target_rho']]
    p['c'] = [p['medium_c'], p['target_c']]
    p['f'] = 38e3

    # remove unneeded parameters
    p = {k: v for k, v in p.items()
         if k not in ['boundary_type', 'a', 'medium_rho', 'medium_c', 'target_rho', 'target_c']}

    mod = echosms.PTDWBAModel()
    print(mod.calculate_ts(p))
    assert np.allclose(mod.calculate_ts(p), -94.0733, atol=0.0001), "Incorrect TS value"


###########################################################
# DWBAModel
@pytest.mark.parametrize("reference_model, f, theta, ts",
                         [('weakly scattering sphere', 38e3, 90, -94.0910),
                          ('weakly scattering prolate spheroid', 38e3, 90, -77.1887),
                          ('weakly scattering finite cylinder', 38e3, 90, -84.7720)])
def test_dwbamodel(rm, reference_model, f, theta, ts):
    m = rm.parameters(reference_model)

    match rm.specification(reference_model)['shape']:
        case 'prolate spheroid':
            rv_pos, rv_tan, a = echosms.create_dwba_spheroid(m['a'], m['b'])
        case 'sphere':
            rv_pos, rv_tan, a = echosms.create_dwba_spheroid(m['a'], m['a'])
        case 'finite cylinder':
            rv_pos, rv_tan, a = echosms.create_dwba_cylinder(m['a'], m['b'])
    m.pop('boundary_type')
    m.pop('b', None)
    m |= {'theta': theta, 'phi': 0, 'a': a, 'rv_pos': rv_pos, 'rv_tan': rv_tan, 'f': f}

    mod = echosms.DWBAModel()

    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), "Incorrect TS value"


###########################################################
# Stochastic option on the DWBAModel
def test_sdwbamodel():
    krill = echosms.DWBAdata().model('Generic krill (McGehee 1998)')

    p = {'medium_c': 1500, 'medium_rho': 1024, 'phi': 0,
         'target_c': 1501, 'target_rho': 1025, 'a': krill.a, 'rv_pos': krill.rv_pos,
         'rv_tan': krill.rv_tan, 'f': 38000, 'theta': 90,
         'phase_sd': 20, 'num_runs': 100}

    mod = echosms.DWBAModel()
    print(mod.calculate_ts(p))

    # Need wider bounds on the closeness check here because of the stochastic
    # part of the SDWBA model.
    assert np.allclose(mod.calculate_ts(p), -115.7, atol=0.5), "Incorrect TS value"
