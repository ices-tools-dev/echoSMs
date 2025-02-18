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
# This is likely to be sufficient to pick up when changes to model code change the output.


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

    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), f"Incorrect TS value"


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

    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), f"Incorrect TS value"


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
    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), f"Incorrect TS value"


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
    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), f"Incorrect TS value"


###########################################################
# KAModel


###########################################################
# HPModel
@pytest.mark.parametrize('model, f, ts', 
                         [('fixed rigid', 38e3, -46.2576),
                          ('elastic', 38e3, -58.1926),
                          ('fluid filled', 38e3, -94.4968),])
def test_hpmodel(model, f, ts):
    mod = echosms.HPModel()
    p = {'boundary_type': model, 'shape': 'sphere', 'medium_c': 1500, 'a': 0.01, 'f': f}
    match model:
        case 'fixed rigid':
            print(mod.calculate_ts(p))
            assert np.allclose(mod.calculate_ts(p), ts, atol=0.0001), f"Incorrect TS value"
        case 'elastic':
            p |= {'medium_rho': 1024, 'target_c': 1600, 'target_rho': 1600}
            print(mod.calculate_ts(p))
            assert np.allclose(mod.calculate_ts(p), ts, atol=0.0001), f"Incorrect TS value"
        case 'fluid filled':
            p |= {'medium_rho': 1024, 'target_c': 1510, 'target_rho': 1025}
            print(mod.calculate_ts(p))
            assert np.allclose(mod.calculate_ts(p), ts, atol=0.0001), f"Incorrect TS value"


###########################################################
# PTDWBAModel


###########################################################
# SDWBAModel


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

    assert np.allclose(mod.calculate_ts(m), [ts], atol=0.0001), f"Incorrect TS value"
