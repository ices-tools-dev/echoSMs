"""Miscellaneous utility functions."""
from collections.abc import Iterable
import numpy as np
import pandas as pd
import xarray as xr
from scipy.special import spherical_jn, spherical_yn
from collections import namedtuple


def as_dataframe(params: dict) -> pd.DataFrame:
    """Convert model parameters from dict form to a Pandas DataFrame.

    Parameters
    ----------
    params :
        A dictionary containing model parameters.

    Returns
    -------
    :
        Returns a Pandas DataFrame generated from the Cartesian product of all items in the
        input dict. DataFrame column names are obtained from the dict keys.

    """
    # Use meshgrid to do the Cartesian product then create a Pandas DataFrame from that, having
    # flattened the multidimensional arrays and using a dict to provide column names.
    # This preserves the differing dtypes in each column compared to other ways of
    # constructing the DataFrame).
    return pd.DataFrame({k: t.flatten()
                         for k, t in zip(params.keys(), np.meshgrid(*tuple(params.values())))})


def as_dataarray(params: dict) -> xr.DataArray:
    """Convert model parameters from dict form to a Xarray DataArray.

    Parameters
    ----------
    params :
        A dictionary containing model parameters.

    Returns
    -------
    :
        Returns a multi-dimensional DataArray generated from the Cartesian product of all items
        in the input dict. The array is named `ts`, the values are initialised to `nan`, the
        dimension names are the dict keys, and the coordinate variables are the dict values.

    """
    # Convert scalars to iterables so xarray is happy
    for k, v in params.items():
        if not isinstance(v, Iterable) or isinstance(v, str):
            params[k] = [v]

    sz = [len(v) for k, v in params.items()]
    return xr.DataArray(data=np.full(sz, np.nan), coords=params, name='ts',
                        attrs={'units': 'dB', 'dB_reference': '1 m^2'})


def eta(m: int) -> int:
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
    return 2*np.pi*f/c


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


def prolate_swf(m: int, lnum: int, c: float, xi: float, eta: Iterable[float],
                norm=False) -> tuple:
    """Calculate prolate spheroidal wave function values.

    Parameters
    ----------
    m : int
        Order m
    lnum : int
        Number of values to calculate for degree l (ell). Will provide
        values of l = m, m+1, m+2, ..., m+lnum-1
    c : float
        Size parameter, equal to kd/2 where k is the wavenumber and d the
        prolate spheroid interfocal distance
    xi : float
        Radial coordinate value to calculate the prolate radial function at [°].
    eta : iterable[float]
        Values of angular coordinate eta for which the prolate spheroidal angular
        function will be calculated.
    norm: bool
        If `True` the angular functions of the first kind and their derivatives
        are normalised by the square root of the normalization of the corresponding
        associated Legendre function. If `False`, the angular functions have the
        same norm as the corresponding associated Legendre function (that is,
        the Meixner and Schafke normalization scheme). This norm becomes very
        large as `m` becomes large.
    angular : bool
        Whether to return values for the angular functions.
    radial : bool
        Whether to return values for the radial functions.
    angular_derivative : bool
        Whether to return values for the derivative of the angular functions.
    radial_derivative : bool
        Whether to return values for the derivative of the radial functions.

    Returns
    -------
    R1 : ndarray[float]
        Radial prolate spheroidal values of the first kind for all values of l (ell).
    R2 : ndarray[float]
        Radial prolate spheroidal values of the second kind for all values of l (ell).
    R1d : ndarray[float]
        Derivative of the radial prolate spheroidal values of the first kind for all
        values of l (ell).
    R2d : ndarray[float]
        Derivative of the radial prolate spheroidal values of the second kind for all
        values of l (ell).
    S1 : ndarray[float]
        Angular prolate spheroidal values of the first kind for all values of l (ell)
        and eta.
    S1d : ndarray[float]
        Derivative of the angular prolate spheroidal values of the first kind for
        all values of l (ell) and eta.
    Racc : ndarray[int]
        Estimated accuracy of the radial values (number of significant digits) for all
        values of l (ell).
    Sacc : ndarray[int]
        Estimated accuracy of the angular values (number of significant digits) for
        all values of l (ell) and eta.

    Raises
    ------
    ValueError
        If any input arguments are invalid.

    Notes
    -----
    This method encapsulates the prolate spheroidal wave function code for non complex
    arguments (van Buren & Boisvert, 2002, and van Buren & Boisvert, 2024), available on
    [github](https://github.com/MathieuandSpheroidalWaveFunctions). This code is in Fortran90
    and was interfaced to Python using `numpy.f2py` then wrapped with the current method to
    provide a convenient interface for use in the [`PSMSModel`][psmsmodel] class.

    References
    ----------
    Van Buren, A. L., & Boisvert, J. E. (2002). Accurate calculation of prolate spheroidal
    radial functions of the first kind and their first derivatives. Quarterly of Applied
    Mathematics, 60(3), 589-599. <https://doi.org/10.1090/qam/1914443>

    Van Buren, A. L., & Boisvert, J. E. (2004). Improved Calculation of Prolate Spheroidal
    Radial Functions of the Second Kind and Their First Derivatives. Quarterly of Applied
    Mathematics, 62(3), 493-507. <https://doi.org/10.1090/qam/2086042>

    """
    # no point importing this unless we need this function.
    from spheroidalwavefunctions import prolate_swf

    # TODO: more input validity checking
    if c < 0:
        raise ValueError('c must be not be negative.')

    if m < 0:
        raise ValueError('m must not be negative')

    if lnum < 0:
        raise ValueError('lnum must not be negative.')

    if xi < 0.0:
        raise ValueError('xi must not be negative.')

    # if xi-1 == 0, then ioprad must be set to 1 (or 0) since r2 and r2d are infinite
    ioprad = 1 if xi-1.0 < 1e-7 else 2

    a = prolate_swf(c=c, m=m, lnum=lnum, x1=xi-1.0, ioprad=ioprad, iopang=2,
                    iopnorm=int(norm), arg=eta)

    swf = namedtuple('swf', ['r1c', 'ir1e', 'r1dc', 'ir1de', 'r2c', 'ir2e', 'r2dc', 'ir2de',
                             'naccr', 's1c', 'is1e', 's1dc', 'is1de', 'naccs'])

    p = swf._make(a)

    # convert characteristic and exponent form of the values into floats.
    R1 = p.r1c * np.float_power(10.0, p.ir1e)
    R2 = p.r2c * np.float_power(10.0, p.ir2e)
    R1d = p.r1dc * np.float_power(10.0, p.ir1de)
    R2d = p.r2dc * np.float_power(10.0, p.ir2de)
    S1 = p.s1c * np.float_power(10.0, p.is1e)
    S1d = p.s1dc * np.float_power(10.0, p.is1de)

    return R1, R2, R1d, R2d, S1, S1d, p.naccr, p.naccs
