import csv
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scipy.special import h1vp, hankel1, jv, jvp

import echosms


def cylinder(a=.001, L=.1, n=11, c=345., rho=1.2):
    return echosms.KRMshape(echosms.boundary_type.pressure_release,
                           np.linspace(-L/2, L/2, n), np.full(n, 2*a),
                           np.full(n, a), np.full(n, -a), c, rho)


def mode_reference(ka, g, h):
    # Pressure and normal-velocity continuity at r=a give this system for b_0 and the
    # internal amplitude; eliminating the latter gives Clay (1992), Eqns (A6)-(A7).
    A = [[hankel1(0, ka), -jv(0, ka/h)],
         [h1vp(0, ka), -jvp(0, ka/h)/(g*h)]]
    b, _ = np.linalg.solve(A, [-jv(0, ka), -jvp(0, ka)])
    return -1j*b/np.pi  # Broadside amplitude per unit length, chi = -pi/4.


def test_krm_volume():
    s = cylinder(n=2)
    assert s.volume() == pytest.approx(np.pi*.001**2*.1)
    s = replace(s, w=np.array([0., .002]), z_U=np.array([0., .001]),
                z_L=np.array([0., -.001]))
    assert s.volume() == pytest.approx(np.pi*.001**2*.1/3)
    s = cylinder(n=1001)
    r = .001*np.sqrt(1-(2*s.x/.1)**2)
    s = replace(s, w=2*r, z_U=r, z_L=-r)
    assert s.volume() == pytest.approx(4*np.pi*.05*.001**2/3, rel=1e-5)
    s = cylinder(n=4)
    s = replace(s, x=np.array([-.05, -.049, .01, .05]))
    assert s.volume() == pytest.approx(np.pi*.001**2*.1)
    s = replace(s, w=np.array([.001, .002, .003, .004]),
                z_U=np.array([.001, .003, .002, .004]),
                z_L=np.array([-.002, -.001, -.004, -.003]))
    for order in [[3, 2, 1, 0], [2, 0, 3, 1]]:
        reordered = replace(s, **{k: getattr(s, k)[order] for k in ['x', 'w', 'z_U', 'z_L']})
        for k in ['x', 'w', 'z_U', 'z_L']:
            np.testing.assert_array_equal(getattr(s, k), getattr(reordered, k))
        assert reordered.volume() == pytest.approx(s.volume())


@pytest.mark.parametrize('x', [[0.], [0., 0.], [0., 2., 0.], [0., np.nan, 1.]])
def test_krm_invalid_cross_sections(x):
    with pytest.raises(ValueError):
        replace(cylinder(n=len(x)), x=np.array(x))


def test_krm_modal_curve():
    m = echosms.KRMModel()
    ka = np.geomspace(.0005, .149, 150)
    expected = np.array([mode_reference(x, 1.2/1025, 345/1500) for x in ka])
    actual = np.array([m._mode_solution(1.2/1025, 345/1500, x/.001, .001, 1., np.pi/2)
                       for x in ka])
    np.testing.assert_allclose(actual, expected, rtol=1e-11, atol=1e-14)
    assert m._mode_solution(1., 1., 50., .001, .1, np.pi/2) == 0.


@pytest.mark.parametrize('medium', ['body', 'water'])
def test_krm_transition(medium):
    m = echosms.KRMModel()
    body = cylinder(a=.01, c=1575., rho=1070.)
    s = cylinder()
    fish = echosms.KRMorganism('', '', body, [s])
    c, rho = (body.c, body.rho) if medium == 'body' else (1500., 1025.)
    R = (s.rho*s.c-body.rho*body.c)/(s.rho*s.c+body.rho*body.c)  # Eqn (9)
    T = 1-((body.rho*body.c-1025*1500)/(body.rho*body.c+1025*1500))**2
    for ka in [.149999, .150001]:
        f = ka*c/(2*np.pi*.001)
        p = {'medium_c': 1500., 'medium_rho': 1025., 'theta': 90., 'f': f,
                 'high_ka_medium': medium, 'low_ka_medium': medium}
        actual = m._scattering_length(**p, organism=fish)\
            - m._scattering_length(**p, organism=replace(fish, inclusions=[]))
        if ka < .15:
            expected = .1*mode_reference(ka, s.rho/rho, s.c/c)
        else:
            q = ka*c/1500
            expected = -.1j*R*T/(2*np.sqrt(np.pi))*q/(q+.083)*np.sqrt(ka+1)\
                * np.exp(-1j*(2*ka+q/(40+q)-1.05))
        assert actual == pytest.approx(expected, rel=1e-11)


@pytest.mark.parametrize('medium', ['body', 'water'])
@pytest.mark.parametrize('theta', [75., 90.])
def test_krm_equivalent_cylinder(medium, theta):
    m = echosms.KRMModel()
    body = cylinder(a=.04, c=1575., rho=1070.)
    s = cylinder(n=2)
    fish = echosms.KRMorganism('', '', body, [s])
    p = {'medium_c': 1500., 'medium_rho': 1025., 'theta': theta, 'f': 1000., 'low_ka_medium': medium}
    k = 2*np.pi*p['f']/(body.c if medium == 'body' else p['medium_c'])
    g = s.rho/(body.rho if medium == 'body' else p['medium_rho'])
    h = s.c/(body.c if medium == 'body' else p['medium_c'])
    delta = k*.1*np.cos(np.radians(theta))
    expected = .1*mode_reference(k*.001, g, h)*np.sinc(delta/np.pi)  # Clay (1992), Eqn (15)
    actual = m._scattering_length(**p, organism=fish)\
        - m._scattering_length(**p, organism=replace(fish, inclusions=[]))
    assert actual == pytest.approx(expected, rel=1e-11)


@pytest.mark.parametrize(('high', 'low'), [('body', 'body'), ('water', 'water'),
                                         ('body', 'water'), ('water', 'body')])
@pytest.mark.parametrize('f', [1000., 38000.])
def test_krm_scaling(high, low, f):
    m = echosms.KRMModel()
    fish = echosms.KRMorganism('', '', cylinder(a=.01, c=1575., rho=1070.), [cylinder()])
    p = {'medium_c': 1500., 'medium_rho': 1025., 'theta': 80., 'f': f,
             'high_ka_medium': high, 'low_ka_medium': low}
    original = m._scattering_length(**p, organism=fish)
    scaled = [replace(s, x=2*s.x, w=2*s.w, z_U=2*s.z_U, z_L=2*s.z_L)
              for s in [fish.body, *fish.inclusions]]
    assert m._scattering_length(**(p | {'f': f/2}), organism=replace(
        fish, body=scaled[0], inclusions=scaled[1:])) == pytest.approx(2*original, rel=1e-11)


def test_krm_matched_body():
    m = echosms.KRMModel()
    body = cylinder(a=.1, c=1500., rho=1025.)
    fish = echosms.KRMorganism('', '', body, [])
    p = {'medium_c': 1500., 'medium_rho': 1025., 'theta': 90., 'f': 50*1500/(2*np.pi)}
    assert m.calculate_ts_single(**p, organism=fish) == -np.inf


@pytest.mark.parametrize(('zu', 'zl'), [(.01, -.01), (.012, -.008), (.03, .01)])
def test_krm_body_equations_15_16(zu, zl):
    m = echosms.KRMModel()
    s = cylinder(a=.01, n=2, c=1575., rho=1070.)
    s = replace(s, z_U=np.full(2, zu), z_L=np.full(2, zl))
    fish = echosms.KRMorganism('', '', s, [])
    k = 2*np.pi*38000/1500
    kb = k/1.05
    R = (1070*1575-1025*1500)/(1070*1575+1025*1500)
    psi = -np.pi*kb*zu/(2*(kb*zu+.4))  # Eqn (15): use z_U, not half-height.
    expected = -.1j*R/(2*np.sqrt(np.pi))*np.sqrt(k*.01)\
        * (np.exp(-2j*k*zu) - (1-R**2)*np.exp(-2j*k*zu+2j*kb*(zu-zl)+1j*psi))
    assert m._scattering_length(1500., 1025., 90., 38000., fish)\
        == pytest.approx(expected, rel=1e-11)
