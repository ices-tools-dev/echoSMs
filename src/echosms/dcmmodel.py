"""A class that provides the model series deformed cylinder scattering model."""

import pandas as pd
import xarray as xr
from scipy.special import jv, hankel1, jvp, h1vp, yv, yvp
import math
# from mapply.mapply import mapply
# import swifter
from echosms import Utils
from .scattermodelbase import ScatterModelBaseClass


class DCMModel(ScatterModelBaseClass):
    """Modal series deformed cylinder model (DCM).

    This class contains methods to calculate acoustic scatter from finite straight cylinders with
    various boundary conditions.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'deformed cylinder model'
        self.short_name = 'dcm'
        self.analytical_type = 'approximate analytical'
        self.model_types = ['fixed rigid', 'pressure release', 'fluid filled']
        self.shapes = ['sphere']
        self.max_frequency = 400.0e3  # [Hz]
        self.min_frequency = 1.0  # [Hz]

    def calculate_ts(self, data, model_type, multiprocess=False):
        """Calculate the scatter from a finite straight cylinder.

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
        ts: Numpy array
            Returns the target strength calculated for all input parameters.

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
            # ts = mapply(data, self.__ts_helper, args=(model_type,), axis=1)
            # Using swifter
            # ts = df.swifter.apply(self.__ts_helper, args=(model_type,), axis=1)
            ts = data.apply(self.__ts_helper, args=(model_type,), axis=1)
        else:  # this uses just one CPU
            ts = data.apply(self.__ts_helper, args=(model_type,), axis=1)

        return ts.to_numpy()

    def __ts_helper(self, *args):
        """Convert function arguments and call calculate_ts_single()."""
        p = args[0].to_dict()  # so we can use it for keyword arguments
        return self.calculate_ts_single(**p, model_type=args[1])

    def calculate_ts_single(self, medium_c, medium_rho, a, b, theta, f, model_type,
                            target_c=None, target_rho=None,
                            shell_c=None, shell_rho=None, shell_thickness=None,
                            **kwargs):
        """
        Calculate the scatter from a finite cylinder using the modal series deformed cylinder model.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho : float
            Density of the fluid medium surrounding the target [kg/m3].
        a : float
            Radius of the cylinderical target [m].
        b : float
            Length of the cylinderical target [m].
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
        The class implements the code in Section B.1 of [1].

        References
        ----------
        ..[1] Jech, J.M., Horne, J.K., Chu, D., Demer, D.A., Francis, D.T.I., Gorska, N., Jones, B.,
        Lavery, A.C., Stanton, T.K., Macaulay, G.J., Reeder, D.B., Sawada, K., 2015.
        Comparisons among ten models of acoustic backscattering used in aquatic ecosystem
        research. Journal of the Acoustical Society of America 138, 3742–3764.
        https://doi.org/10.1121/1.4937607
        """
        if theta == 0.0:
            return math.nan

        theta_rad = theta*math.pi/180.
        k = Utils.k(medium_c, f)
        K = k * math.sin(theta_rad)
        Ka = K*a
        kL = k*b

        m = range(30)  # this needs to vary with f

        # Some code varies with model type.
        match model_type:
            case 'fixed rigid':
                series = list(map(lambda m: (-1)**m * Utils.eta(m) * (jvp(m, Ka) / h1vp(m, Ka)), m))
            case 'pressure release':
                series = list(map(lambda m: (-1)**m * Utils.eta(m) *
                                  (jv(m, Ka) / hankel1(m, Ka)), m))
            case 'fluid filled':
                g = target_rho/medium_rho
                h = target_c/medium_c
                gh = g*h
                Kda = K/h*a

                def Cm(m):
                    numer = (jvp(m, Kda) * yv(m, Ka))/(jv(m, Kda) * jvp(m, Ka))\
                        - gh*(yvp(m, Ka) / jvp(m, Ka))
                    denom = (jvp(m, Kda) * jv(m, Ka))/(jv(m, Kda)*jvp(m, Ka)) - gh
                    return numer/denom
                series = list(map(lambda m: 1j**(2*m) * Utils.eta(m) / (1 + 1j*Cm(m)), m))
            case _:
                raise ValueError(f'The {self.long_name} model does not support '
                                 f'a model type of "{model_type}".')

        fbs = 1j*b/math.pi * (math.sin(kL*math.cos(theta_rad))
                              / (kL*math.cos(theta_rad))) * sum(series)

        ts = 20*math.log10(abs(fbs))

        return ts
