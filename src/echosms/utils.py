"""Miscellaneous utility functions."""
import sys
from collections.abc import Iterable
import numpy as np
from math import pi as π
import xarray as xr
import pandas as pd
from scipy.special import spherical_jn, spherical_yn
from collections import namedtuple
from spheroidalwavefunctions import prolate_swf
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


swf_t = namedtuple('swf', ['r1c', 'ir1e', 'r1dc', 'ir1de', 'r2c', 'ir2e', 'r2dc', 'ir2de',
                           'naccr', 's1c', 'is1e', 's1dc', 'is1de', 'naccs'])

class boundary_type(StrEnum):
    """Scattering model boundary types."""

    fixed_rigid = 'fixed-rigid'
    """Fixed-rigid boundary condition, where the normal velocity is zero at the
    object's boundary."""

    pressure_release = 'pressure-release'
    """Pressure-release boundary condition, where the acoustic pressure is zero at the
    object's boundary."""

    fluid_filled = 'fluid-filled'
    """Fluid-filled boundary condition, where the acoustic pressure and normal velocity are
    both non-zero at the object's boundary."""

    elastic = 'elastic'
    """The scattering object supports compressional and shear waves."""

    fluid_shell_fluid_interior = 'fluid shell fluid interior'
    """The object has a fluid interior surrounded by a fluid shell."""

    fluid_shell_pressure_release_interior = "fluid shell pressure release interior"
    """The object has a pressure release interior surrounded by a fluid shell."""

    hard = 'fixed-rigid'
    """A synonym for `fixed_rigid`."""

    soft = 'pressure-release'
    """A synonym for `pressure_release`."""

    fluid = 'fluid-filled'
    """A synonym for `fluid_filled`."""

def theoretical_Sa(ts: float | np.ndarray, eba: float, r: float, nautical=False)\
                   -> float | np.ndarray:
    """Theoretical area backscattering strength (Sₐ) of a target.

    Parameters
    ----------
    ts :
        The target strength of the object [dB re 1 m²].
    eba :
        Ten times the logarithm to the base 10 of the transducer's equivalent two-way beam angle (ψ, sr).
        In formula form this is: eba = 10 log<sub>10</sub>(ψ) dB (re 1 sr).
    r :
        The range from the transducer to the target [m]. Used for acoustic beam spreading.
    nautical :
        If `True`, the nautical area scattering strength (S<sub>A</sub>) is returned instead of the
        area backscattering strength (Sₐ).

    Returns
    -------
    :
        The theoretical Sₐ [dB re 1 m² m⁻²] or S<sub>A</sub> [dB re 1 m² nmi⁻²] of the input `ts`.

    Raises
    ------
    ValueError
        If an input value is out of bounds.

    Notes
    -----
    While the calculation is valid for any target, the theoretical area strengths are most relevant
    when calibrating an echosounder using a sphere. The difference between
    the theoretical and measured can be used to calculate the calibration gain for an
    echosounder (when the sphere is on-axis).
    """
    if eba > 0.0:
        raise ValueError('A positive eba value is not supported.')
    if r <= 0.0:
        raise ValueError('An r value less than or equal to 0 is not supported.')

    factor = 10.0*np.log10(4.0*π*1852.0**2) if nautical else 0.0
    return ts - eba - 20.0*np.log10(r) + factor


def Neumann(m: int) -> int:
    """Neumann number.

    Parameters
    ----------
    m :
        The input integer.

    Returns
    -------
    :
        The Neumann number.
    """
    if m == 0:
        return 1
    return 2


def wavenumber(c: float, f: float) -> float:
    """Calculate the acoustic wavenumber.

    Parameters
    ----------
    c :
        Sound speed [m/s]

    f :
        Frequency [Hz]

    Returns
    -------
    :
        The acoustic wavenumber [m⁻¹].
    """
    return 2*π*f/c


def wavelength(c: float, f: float) -> float:
    """Calculate the acoustic wavelength.

    Parameters
    ----------
    c :
        Sound speed [m/s]

    f :
        Frequency [Hz]

    Returns
    -------
    :
        The acoustic wavelength [m].
    """
    return c/f


def h1(n: int, z: float, derivative=False) -> complex:
    """Spherical Hankel function of the first kind or its' derivative.

    Parameters
    ----------
    n :
        Order (n ≥ 0).
    z :
        Argument of the Hankel function.
    derivative :
        if True, the value of the derivative (rather than the function itself) is returned.

    Returns
    -------
    :
        Value of the spherical Hankel function

    Raises
    ------
    ValueError
        For negative n values.

    Notes
    -----
    The value of the Hankel function is calculated from spherical Bessel functions [1].

    The derivative is computed from spherical Hankel functions [2].

    References
    ----------
    [1] <https://dlmf.nist.gov/10.47.E10>

    [2] <https://dlmf.nist.gov/10.51.E2>
    """
    if n < 0:
        raise ValueError('Negative n values are not supported for spherical Hankel functions.')

    if not derivative:
        return spherical_jn(n, z) + 1j*spherical_yn(n, z)
    return -h1(n+1, z) + (n/z) * h1(n, z)


def spherical_jnpp(n: int, z: float) -> float:
    """Second derivative of the spherical Bessel function.

    Parameters
    ----------
    n :
        Order (n ≥ 0)
    z :
        Argument of the Bessel function.

    Returns
    -------
    :
        The second derivative of the spherical Bessel function.

    """
    return 1./z**2 * ((n**2-n-z**2)*spherical_jn(n, z) + 2.*z*spherical_jn(n+1, z))


def split_dict(d: dict, s: list) -> tuple[dict, dict]:
    """Split a dict into two dicts based on a list of keys.

    Parameters
    ----------
    d : dict
        Dict to be split.

    s: list
        List of dict keys to use for splitting `d`.

    Returns
    -------
    : tuple(dict, dict)
        The `input` dict split into two dicts based on the keys in `s`. The first tuple item
        contains the items that do not have keys in `s`.
    """
    contains = {k: v for k, v in d.items() if k in s}
    ncontains = {k: v for k, v in d.items() if k not in s}
    return ncontains, contains


def as_dataarray(params: dict, no_expand: list = []) -> xr.DataArray:
    """Convert model parameters from dict form to a Xarray DataArray.

    Parameters
    ----------
    params :
        The model parameters.

    no_expand :
        Key values of the non-expandable model parameters in `params`.

    Returns
    -------
    :
        Returns a multi-dimensional DataArray generated from the Cartesian product of all
        expandable items in the input dict. Non-expandable items are added to the DataArray
        attrs property. Expandable items are those that can be sensibly expanded into
        DataArray coordinates. Not all models have non-expandable items.
        The array is named `ts`, the values are initialised to `nan`, the
        dimension names are the dict keys, and the coordinate variables are the dict values.

    """
    expand, nexpand = split_dict(params, no_expand)

    # Convert scalars to iterables so xarray is happy
    for k, v in expand.items():
        if not isinstance(v, Iterable) or isinstance(v, str):
            expand[k] = [v]

    sz = [len(v) for k, v in expand.items()]
    return xr.DataArray(data=np.full(sz, np.nan), coords=expand, name='ts',
                        attrs={'units': 'dB', 'dB_reference': '1 m^2',
                               'parameters': nexpand})


def as_dataframe(params: dict, no_expand: list = []) -> pd.DataFrame:
    """Convert model parameters from dict form to a Pandas DataFrame.

    Parameters
    ----------
    params :
        The model parameters.

    no_expand :
        Key values of the non-expandable model parameters in `params`.

    Returns
    -------
    :
        Returns a Pandas DataFrame generated from the Cartesian product of all expandable
        items in the input dict. DataFrame column names are obtained from the dict keys.
        Non-expandable items are added to the DataFrame attrs property. Expandable items are
        those that can be sensibly expanded into DataFrame columns. Not all models have
        non-expandable items.

    """
    expand, nexpand = split_dict(params, no_expand)

    # Use meshgrid to do the Cartesian product then create a Pandas DataFrame from that, having
    # flattened the multidimensional arrays and using a dict to provide column names.
    # This preserves the differing dtypes in each column compared to other ways of
    # constructing the DataFrame).
    df = pd.DataFrame({k: t.flatten()
                       for k, t in zip(expand.keys(), np.meshgrid(*tuple(expand.values())))})
    df.attrs = {'parameters': nexpand}
    return df


def as_dict(params: dict | pd.DataFrame | xr.DataArray) -> dict:
    """Convert model parameters from DataFrame or DataArray to dict.

    Parameters
    ----------
    params:
        The model parameters

    Raises
    ------
    TypeError:
        If the input data type is not supported.

    Returns
    -------
    :
        A dict containing the model parameters.
    """
    if isinstance(params, dict):
        return params

    # Get the non-expandable model parameters
    p = params.attrs['parameters'] if 'parameters' in params.attrs else {}

    if isinstance(params, xr.DataArray):
        return dict(zip(params.coords, params.indexes.values())) | p
    elif isinstance(params, pd.DataFrame):
        # params.attrs = {}  # otherwise to_dict() exposes a bug in pandas?
        return params.to_dict(orient='series') | p

    raise TypeError('Only dict, DataFrame, or DataArray are accepted.')


def pro_ang1(m: int, n: int, c: float, eta: float, norm=False) -> tuple[float, float]:
    """Prolate spheroidal angular function of the first kind and derivative.

    Calculates the prolate spheroidal angular function of the first kind and its'
    derivative with respect to `eta`.

    Parameters
    ----------
    m :
        The order parameter (≥ 0)
    n :
        The degree parameter (≥ `m`).
    c :
        The size parameter.
    eta :
        The angular coordinate, η, where |η| ≤ 1.
    norm :
        If `False`, returned values are not normalised (i.e., the Meixner-Schäfke normlalisation
        scheme is used). For large `m` this norm becomes very large. If `True` the returned values
        are scaled by the square root of the normalisation of the corresponding Legendre function.
        This avoids the large values that occur when `norm` is `False`.

    Returns
    -------
    :
        The value of the prolate spheroidal angular function and its' derivative.

    Notes
    -----
    This method uses the prolate spheroidal wave function code for non complex
    arguments (van Buren & Boisvert, 2002, and van Buren & Boisvert, 2024), available on
    [github](https://github.com/MathieuandSpheroidalWaveFunctions). This code is in Fortran90
    and was interfaced to Python using `numpy.f2py` then wrapped with the current method to
    provide a similar calling convention as the Scipy function of the same name.

    References
    ----------
    Van Buren, A. L., & Boisvert, J. E. (2002). Accurate calculation of prolate spheroidal
    radial functions of the first kind and their first derivatives. Quarterly of Applied
    Mathematics, 60(3), 589-599. <https://doi.org/10.1090/qam/1914443>

    Van Buren, A. L., & Boisvert, J. E. (2004). Improved Calculation of Prolate Spheroidal
    Radial Functions of the Second Kind and Their First Derivatives. Quarterly of Applied
    Mathematics, 62(3), 493-507. <https://doi.org/10.1090/qam/2086042>
    """
    if m < 0:
        raise ValueError('The m parameter must be positive.')
    if n < m:
        raise ValueError('The n parameter must be greater than or equal to the m parameter.')
    if abs(eta) > 1.0:
        raise ValueError('The eta parameter must be less than or equal to 1')

    a = prolate_swf.profcn(c=c, m=m, lnum=n-m+2, x1=0.0, ioprad=0, iopang=2,
                           iopnorm=int(norm), arg=[eta])
    p = swf_t._make(a)
    if np.isnan(p.s1c[n-m]) or np.isnan(p.s1dc[n-m]):
        # print('Root - trying again.')
        a = prolate_swf.profcn(c=c, m=m, lnum=n-m+2, x1=0.0, ioprad=0, iopang=2,
                               iopnorm=int(norm), arg=[eta+sys.float_info.epsilon])
        p = swf_t._make(a)

    s = p.s1c[n-m] * np.float_power(10.0, p.is1e[n-m])
    sp = p.s1dc[n-m] * np.float_power(10.0, p.is1de[n-m])

    return s[0], sp[0]


def pro_rad1(m: int, n: int, c: float, xi: float) -> tuple[float, float]:
    """Prolate spheroidal radial function of the first kind and derivative.

    Calculates the prolate spheroidal radial function of the first kind and its'
    derivative with respect to `xi`.

    Parameters
    ----------
    m :
        The order parameter (≥ 0).
    n :
        The degree parameter (≥ `m`).
    c :
        The size parameter.
    xi :
        The radial coordinate, ξ, where ξ ≥ 1.

    Returns
    -------
    :
        The value of the prolate spheroidal radial function and its' derivative.

    Notes
    -----
    This method uses the prolate spheroidal wave function code for non complex
    arguments (van Buren & Boisvert, 2002, and van Buren & Boisvert, 2024), available on
    [github](https://github.com/MathieuandSpheroidalWaveFunctions). This code is in Fortran90
    and was interfaced to Python using `numpy.f2py` then wrapped with the current method to
    provide a similar calling convention as the Scipy function of the same name.

    References
    ----------
    Van Buren, A. L., & Boisvert, J. E. (2002). Accurate calculation of prolate spheroidal
    radial functions of the first kind and their first derivatives. Quarterly of Applied
    Mathematics, 60(3), 589-599. <https://doi.org/10.1090/qam/1914443>

    Van Buren, A. L., & Boisvert, J. E. (2004). Improved Calculation of Prolate Spheroidal
    Radial Functions of the Second Kind and Their First Derivatives. Quarterly of Applied
    Mathematics, 62(3), 493-507. <https://doi.org/10.1090/qam/2086042>
    """
    if m < 0:
        raise ValueError('The m parameter must be positive.')
    if n < m:
        raise ValueError('The n parameter must be greater than or equal to the m parameter.')
    if xi < 1.0:
        raise ValueError('The xi parameter must be greater than or equal to 1')

    a = prolate_swf.profcn(c=c, m=m, lnum=n-m+2, x1=xi-1.0, ioprad=1, iopang=0, iopnorm=0, arg=[0])
    p = swf_t._make(a)
    s = p.r1c * np.float_power(10.0, p.ir1e)
    sp = p.r1dc * np.float_power(10.0, p.ir1de)

    return s[n-m], sp[n-m]


def pro_rad2(m: int, n: int, c: float, xi: float) -> tuple[float, float]:
    """Prolate spheroidal radial function of the second kind and derivative.

    Calculates the prolate spheroidal radial function of the second kind and its'
    derivative with respect to `xi`.

    Parameters
    ----------
    m :
        The order parameter (≥ 0).
    n :
        The degree parameter (≥ `m`).
    c :
        The size parameter.
    xi :
        The radial coordinate, ξ, where ξ ≥ 1.

    Returns
    -------
    :
        The value of the prolate spheroidal radial function and its' derivative.

    Notes
    -----
    This method uses the prolate spheroidal wave function code for non complex
    arguments (van Buren & Boisvert, 2002, and van Buren & Boisvert, 2024), available on
    [github](https://github.com/MathieuandSpheroidalWaveFunctions). This code is in Fortran90
    and was interfaced to Python using `numpy.f2py` then wrapped with the current method to
    provide a similar calling convention as the Scipy function of the same name.

    References
    ----------
    Van Buren, A. L., & Boisvert, J. E. (2002). Accurate calculation of prolate spheroidal
    radial functions of the first kind and their first derivatives. Quarterly of Applied
    Mathematics, 60(3), 589-599. <https://doi.org/10.1090/qam/1914443>

    Van Buren, A. L., & Boisvert, J. E. (2004). Improved Calculation of Prolate Spheroidal
    Radial Functions of the Second Kind and Their First Derivatives. Quarterly of Applied
    Mathematics, 62(3), 493-507. <https://doi.org/10.1090/qam/2086042>
    """
    if m < 0:
        raise ValueError('The m parameter must be positive.')
    if n < m:
        raise ValueError('The n parameter must be greater than or equal to the m parameter.')
    if xi < 1.0:
        raise ValueError('The xi parameter must be greater than or equal to 1')

    ioprad = 1 if xi-1.0 < 1e-10 else 2

    # Add +2 to lnum instead of +1 as it exposes a bug in the Fortran code - if n = 0, zeros
    # are returned instead of the correct value.
    a = prolate_swf.profcn(c=c, m=m, lnum=n-m+2, x1=xi-1.0,
                           ioprad=ioprad, iopang=0, iopnorm=0, arg=[0])
    p = swf_t._make(a)

    if ioprad == 1:
        s = np.inf
        sp = np.inf
    else:
        s = p.r2c * np.float_power(10.0, p.ir2e)
        sp = p.r2dc * np.float_power(10.0, p.ir2de)

    return s[n-m], sp[n-m]
