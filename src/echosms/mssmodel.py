"""A class that provides the modal series solution scattering model."""

import numpy as np
import pandas as pd
import xarray as xr
from mapply.mapply import mapply
# import swifter
from scipy.special import spherical_jn, spherical_yn
from echosms import Utils
from .scattermodelbase import ScatterModelBaseClass


class MSSModel(ScatterModelBaseClass):
    """Modal series solution (MSS) scattering model.

    This class contains methods to calculate acoustic scatter from spheres and shells with various
    boundary conditions.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'modal series solution'
        self.short_name = 'mss'
        self.analytical_type = 'exact'
        self.model_types = ['fixed rigid', 'pressure release', 'fluid filled',
                            'fluid shell fluid interior', 'fluid shell pressure release interior']
        self.shapes = ['sphere']
        self.max_frequency = 400.0e3  # [Hz]
        self.min_frequency = 1.0  # [Hz]

    def calculate_ts(self, data, model_type, multiprocess=False):
        """Calculate the scatter from a sphere.

        Parameters
        ----------
        data: Pandas DataFrame or Xarray DataArray or dictionary
            If a DataFrame, must contain column names as per the function parameters in the
            calculate_ts_single() function in this class. Each row in the DataFrame will generate
            one TS output. If a DataArray, must contain coordinate names as per the function
            parameters in calculate_ts_single(). The TS will be calculated for all combinations of
            the coordinate variables. If dictionary, it will be converted to a DataFrame first.

        model_type: string
            The type of model boundary to apply. Valid values are given in the model_types class
            variable.

        Returns
        -------
        ts: array_like
            Returns the target strength calculated for all input parameters. Returns an iterable.

        """
        if isinstance(data, dict):
            data = Utils.df_from_dict(data)
        elif isinstance(data, pd.DataFrame):
            pass
        elif isinstance(data, xr.DataArray):
            # For the moment just convert DataArrays into DataFrames
            data = data.to_dataframe().reset_index()
        else:
            raise ValueError(f'Data type of {type(data)} is not supported'
                             ' (only dictionaries, Pandas DataFrames and Xarray DataArrays are).')

        if multiprocess:
            # Using mapply:
            ts = mapply(data, self.__ts_helper, args=(model_type,), axis=1)
            # Using swifter
            # ts = df.swifter.apply(self.__ts_helper, args=(model_type,), axis=1)
        else:  # this uses just one CPU
            ts = data.apply(self.__ts_helper, args=(model_type,), axis=1)

        # Should convert this to match the input data form (e.g., array for dict, Series for
        # DataFrame and DataArray for DataArray).
        return ts.to_numpy()

    def __ts_helper(self, *args):
        """Convert function arguments and call calculate_ts_single()."""
        p = args[0].to_dict()  # so we can use it for keyword arguments
        return self.calculate_ts_single(**p, model_type=args[1])

    def calculate_ts_single(self, medium_c, medium_rho, a, theta, f, model_type,
                            target_c=None, target_rho=None, **kwargs):
        """
        Calculate the scatter using the mss model for one set of parameters.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho : float
            Density of the fluid medium surrounding the target [kg/m3].
        a : float
            Radius of the spherical target [m].
        theta : float
            Pitch angle(s) to calculate the scattering at [degrees]. An angle of 0 is head on,
            90 is dorsal, and 180 is tail on.
        f : float
            Frequencies to calculate the scattering at [Hz].
        model_type : str
            The model type. Supported model types are given in the model_types class variable.
        target_c : float, optional
            Sound speed in the fluid inside the sphere [m/s].
            Only required for `model_type` of ``fluid filled``
        target_rho : float, optional
            Density of the fluid inside the sphere [kg/m^3].
            Only required for `model_type` of ``fluid filled``

        Returns
        -------
        ts : the target strength (re 1 m2) of the target [dB].

        Notes
        -----
        The class implements the code in Section A.1 of [1].

        References
        ----------
        ..[1] Jech, J.M., Horne, J.K., Chu, D., Demer, D.A., Francis, D.T.I., Gorska, N., Jones, B.,
        Lavery, A.C., Stanton, T.K., Macaulay, G.J., Reeder, D.B., Sawada, K., 2015.
        Comparisons among ten models of acoustic backscattering used in aquatic ecosystem
        research. Journal of the Acoustical Society of America 138, 3742–3764.
        https://doi.org/10.1121/1.4937607
        """
        k0 = Utils.k(medium_c, f)
        ka = k0*a
        n = np.arange(0, round(ka+20))

        # Some code varies with model type.
        match model_type:
            case 'fixed rigid':
                A = list(map(lambda x: -spherical_jn(x, ka, True) / Utils.h1(x, ka, True), n))
            case 'pressure release':
                A = list(map(lambda x: -spherical_jn(x, ka) / Utils.h1(x, ka), n))
            case 'fluid filled':
                k1a = Utils.k(target_c, f)*a
                gh = target_rho/medium_rho * target_c/medium_c

                def Cn(n):
                    return\
                        ((spherical_jn(n, k1a, True) * spherical_yn(n, ka))
                            / (spherical_jn(n, k1a) * spherical_jn(n, ka, True))
                            - gh * (spherical_yn(n, ka, True) / spherical_jn(n, ka, True)))\
                        / ((spherical_jn(n, k1a, True) * spherical_jn(n, ka))
                           / (spherical_jn(n, k1a) * spherical_jn(n, ka, True)) - gh)

                A = -1/(1 + 1j*np.asarray(list(map(Cn, n)), dtype=complex))
            case 'fluid shell fluid interior' | 'fluid shell pressure release interior':
                raise ValueError(f'Model type of {model_type} is not yet implemented.')
            case _:
                raise ValueError(f'The {self.long_name} model does not support '
                                 f'a model type of "{model_type}".')

        fbs = -1j/k0 * np.sum((-1)**n * (2*n+1) * A)
        ts = 20*np.log10(np.abs(fbs))

        return ts
