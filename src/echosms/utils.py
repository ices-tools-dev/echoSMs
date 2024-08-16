"""Miscellaneous utility functions."""
import numpy as np
import pandas as pd
import xarray as xr
from scipy.special import spherical_jn, spherical_yn


def df_from_dict(params: dict) -> pd.DataFrame:
    """Convert model parameters from dict form to a Pandas DataFrame.

    Parameters
    ----------
    params :
        A dictionary containing model parameters.

    Returns
    -------
    :
        Returns a Pandas DataFrame generated from the Cartesian product of all items in the
        input dict.

    """
    # Use meshgrid to do the Cartesian product, then reshape into a 2D array, then create a
    # Pandas DataFrame() from that
    return pd.DataFrame(np.array(
        np.meshgrid(*tuple(params.values()))).T.reshape(-1, len(params)),
        columns=params.keys())


def da_from_dict(params: dict) -> xr.DataArray:
    """Convert model parameters from dict form to a Xarray DataArray.

    Parameters
    ----------
    params :
        A dictionary containing model parameters.

    Returns
    -------
    :
        Returns a multi-dimensional DataArray generated from the Cartesian product of all items
        in the input dict.

    """
    # Convert scalars to iterables so xarray is happier later on
    for k, v in params.items():
        if not hasattr(v, '__iter__'):
            params[k] = [v]
    # Lengths of each parameter array
    sz = [len(v) for k, v in params.items()]
    # Create the DataArray
    return xr.DataArray(data=np.full(sz, np.nan), coords=params, name='ts')


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
    else:
        return 2


def k(c: float, f: float) -> float:
    """Calculate the acoustic wavenumber.

    Parameters
    ----------
    c :
        Sound speed [m/s]

    f :
        Frequency [Hz]

    Returns
    -------
    k :
        The acoustic wavenumber [m⁻¹].
    """
    return 2*np.pi*f/c


def h1(n: int, z: float, derivative=False) -> complex:
    """Spherical Hankel function of the first kind or its' derivative.

    Parameters
    ----------
    n :
        Order (n >= 0).
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
    else:
        return -h1(n+1, z) + (n/z) * h1(n, z)
