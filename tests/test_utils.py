"""Test functions in the utils.py file."""

import pytest
import echosms
import pandas
import xarray

def test_datastore_schema():
    s = echosms.datastore_schema()
    assert isinstance(s, dict)
    assert len(s) > 0


def test_names_from_aphia_id():
    """Test access to the WoRMS API."""
    s = echosms.names_from_aphia_id(126436) # Atlantic cod

    assert isinstance(s, dict)
    assert s['species'] == 'Gadus morhua'


def test_pro_rad2():
    """Test prolate spheroid radial type 2 function and derivative."""
    v = echosms.pro_rad2(m=0, n=1, c=0.5, xi=1.1)
    assert v[0] == pytest.approx(-8.743654662343038)
    assert v[1] == pytest.approx(45.545658684546964)


def test_pro_rad1():
    """Test prolate spheroid radial type 1 function and derivative."""
    v = echosms.pro_rad1(m=0, n=1, c=0.5, xi=1.1)
    assert v[0] == pytest.approx(0.17965812547973625)
    assert v[1] == pytest.approx(0.15338687455029776)


def test_ang1():
    """Test prolate spheroid angular or first kind and derivative."""
    v = echosms.pro_ang1(m=0, n=1, c=0.5, eta=0.5)
    assert v[0] == pytest.approx(0.5043763082172239)
    assert v[1] == pytest.approx(0.9961569362510381)


def test_spherical_jnpp():
    """Test second derivative of the spherical bessel function."""
    v = echosms.spherical_jnpp(0, 0.5)
    assert v == pytest.approx(-0.3087029546641392)


def test_h1():
    """Test the spherical Hankel function of the first kind and derivative."""
    v = echosms.h1(0, 0.5, derivative=False)
    assert v.real == pytest.approx(0.958851077208406)
    assert v.imag == pytest.approx(-1.7551651237807455)

    v = echosms.h1(0, 0.5, derivative=True)
    assert v.real == pytest.approx(-0.1625370306360667)
    assert v.imag == pytest.approx(4.469181324769897)

def test_theoretical_Sa():
    """Test calculation of Sa from TS."""
    v = echosms.theoretical_Sa(-42.4, -20.5, 15.0)
    print(v)
    assert v == pytest.approx(-45.421825181113626)


def test_boundary_type():
    """Test that boundary type equivalents work."""
    assert echosms.boundary_type.fixed_rigid == echosms.boundary_type.hard
    assert echosms.boundary_type.pressure_release == echosms.boundary_type.soft
    assert echosms.boundary_type.fluid_filled == echosms.boundary_type.fluid
    assert len(echosms.boundary_type) == 6 # num of unique enums

def test_neumann():
    """Test the Neumann function."""
    assert echosms.Neumann(0) == 1
    assert echosms.Neumann(1) == 2
    assert echosms.Neumann(3) == 2

def test_split_dict():
    """Test the split_dict function."""
    d = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    s = ['a', 'c']
    v = echosms.split_dict(d, s)
    assert v[0] == {'b': 2, 'd': 4}
    assert v[1] == {'a': 1, 'c': 3}


def test_as_dataarray():
    p = {'a': 1, 'b': 2}
    v = echosms.as_dataarray(p)
    assert isinstance(v, xarray.DataArray)


def test_as_dataframe():
    p = {'a': 1, 'b': 2}
    v = echosms.as_dataframe(p)
    assert isinstance(v, pandas.DataFrame)


def test_as_dict():
    p = {'a': 1, 'b': 2}
    da = echosms.as_dataarray(p)
    df = echosms.as_dataframe(p)

    assert isinstance(echosms.as_dict(da), dict)
    assert isinstance(echosms.as_dict(df), dict)
