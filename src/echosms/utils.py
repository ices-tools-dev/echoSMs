"""Miscellaneous utility functions."""
import numpy as np
import pandas as pd
import xarray as xr
from scipy.special import spherical_jn, spherical_yn


class Utils:
    """Miscellaneous utility functions."""

    def df_from_dict(params):
        """Convert model parameters from dict form to a Pandas DataFrame."""
        # Use meshgrid to do the Cartesian product, then reshape into a 2D array, then create a
        # Pandas DataFrame() from that
        return pd.DataFrame(np.array(
            np.meshgrid(*tuple(params.values()))).T.reshape(-1, len(params)),
            columns=params.keys())

    def xa_from_dict(params):
        """Convert model parameters from dict form to a Xarray DataArray."""
        # Convert scalars to iterables so xarray is happier later on
        for k, v in params.items():
            if not hasattr(v, '__iter__'):
                params[k] = [v]
        # Lengths of each parameter array
        sz = [len(v) for k, v in params.items()]
        # Create the DataArray
        return xr.DataArray(data=np.full(sz, np.nan), coords=params, name='ts')

    def eta(m: int):
        """Neumann number."""
        if m == 0:
            return 1
        else:
            return 2

    def k(c, f):
        """Calculate the acoustic wavenumber.

        Parameters
        ----------
        c[float]: array_like
            Sound speed [m/s]

        f: array_like (float)
            Frequency [Hz]

        Returns
        -------
        k: scalar or array_like
            The acoustic wavenumber [m-1].
        """
        return 2*np.pi*f/c

    def h1(n, z, derivative=False):
        """Spherical Hankel function of the first kind or its' derivative.

        Parameters
        ----------
        n: array_like (float)
            Order (n >= 0).
        z: array_like (float or complex)
            Argument of the Hankel function.
        derivative: bool, optional
            if True, the value of the derivative (rather than the function itself) is returned.

        Returns
        -------
        h: scalar or ndarray
            Value of the spherical Hankel function

        Notes
        -----
        The value of the Hankel function is calculated from spherical Bessel functions [1]_.

        The derivative is computed from spherical Hankel functions [2]_.

        References
        ----------
        ..[1] https://dlmf.nist.gov/10.47.E10
        ..[2] https://dlmf.nist.gov/10.51.E2
        """
        if n < 0:
            raise ValueError('Negative n values are not supported for spherical Hankel functions.')

        if not derivative:
            return spherical_jn(n, z) + 1j*spherical_yn(n, z)
        else:
            return -Utils.h1(n+1, z) + (n/z)*Utils.h1(n, z)
