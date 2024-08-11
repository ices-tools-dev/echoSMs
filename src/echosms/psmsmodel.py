"""A class that provides the prolate spheroidal modal series scattering model."""

import numpy as np
import pandas as pd
import xarray as xr
# from mapply.mapply import mapply
# import swifter
from scipy.special import pro_ang1, pro_rad1, pro_rad2
from echosms import Utils
from scipy.integrate import quad
from .scattermodelbase import ScatterModelBaseClass


class PSMSModel(ScatterModelBaseClass):
    """Prolate spheroidal modal series (PSMS) scattering model."""

    def __init__(self):
        super().__init__()
        self.long_name = 'prolate spheroidal modal series'
        self.short_name = 'psms'
        self.analytical_type = 'exact'
        self.model_types = ['fixed rigid', 'pressure release', 'fluid filled']
        self.shapes = ['prolate spheroid']
        self.max_frequency = 200.0e3  # [Hz]
        self.min_frequency = 1.0  # [Hz]

    def calculate_ts(self, data, model_type, multiprocess=False):
        """Calculate the scatter from a prolate spheroid.

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

    def calculate_ts_single(self, medium_c, medium_rho, a, b, theta, freq, model_type,
                            target_c=None, target_rho=None):
        """Prolate spheroid modal series (PSMS) solution model.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho : float
            Density of the fluid medium surrounding the target [kg/m3].
        a : float
            Prolate spheroid major axis radius [m].
        b : float
            Prolate spheroid minor axis radius [m].
        theta : float or array of float
            Pitch angle(s) to calculate the scattering at [degrees]. An angle of 0 is head on,
            90 is dorsal, and 180 is tail on.
        freqs : float or array of float
            Frequencies to calculate the scattering at [Hz].
        model_type : str
            The model type. Supported model types are given in the model_types class variable.
        target_c : float, optional
            Sound speed in the fluid inside the target [m/s].
            Only required for `model_type` of ``fluid filled``
        target_rho : float, optional
            Density of the fluid inside the target [kg/m^3].
            Only required for `model_type` of ``fluid filled``

        Returns
        -------
        ts : the target strength (re 1 m2) of the target [dB].

        Notes
        -----
        The backscattered target strength of a pressure release or fluid-filled prolate spheroid
        is calculated using the PSMS method of Furusawa [1] and corrections [2].

        .. [1] Furusawa, M. (1988). "Prolate spheroidal models for predicting general
            trends of fish target strength," J. Acoust. Soc. Jpn. 9, 13-24.
        .. [2] Furusawa, M., Miyanohana, Y., Ariji, M., and Sawada, Y. (1994).
            “Prediction of krill target strength by liquid prolate spheroid
            model,” Fish. Sci., 60, 261–265.
        """
        match model_type:
            case 'pressure release' | 'fluid filled':
                pass
            case 'fixed rigid':
                raise ValueError(f'Model type "{model_type}" has not yet been implemented '
                                 f'for the {self.long_name} model.')
            case _:
                raise ValueError(f'The {self.long_name} model does not support '
                                 f'a model type of "{model_type}".')

        if model_type == 'fluid filled':
            hc = target_c / medium_c
            rh = target_rho / medium_rho

        # The wavenumber for the surrounding fluid
        k0 = 2*np.pi*freq/medium_c
        # The semi-focal length of the prolate spheroid (same as for an ellipse)
        q = np.sqrt(a*a - b*b)
        # An alternative to ka is kq, the wavenumber multiplied by the focal length
        h0 = k0 * q
        # Epsilon is a characteristic of the spheroid, whereby a = xi0 * q,
        # hence converting this to use a and b gives:
        xi0 = (1.0 - (b/a)**2)**(-.5)
        # Phi, the port/starboard angle is fixed for this code
        phi_inc = np.pi  # radians, incident direction
        phi_bs = 0  # radians, backscattered direction

        # Approximate limits on the summations
        m_max = int(np.ceil(2*k0*b))
        n_max = int(m_max + np.ceil(h0/2))

        # Terms in the summation smaller than this will cause the iteration to
        # stop. Even and odd values of (m-n) are treated separately.
        # The value is quite low as some of the summations start out low then rise
        # quite a lot. This value will get rid of the summations that don't add
        # much.
        tol = -50  # [dB]
        check_after = 20  # iterations

        f = 0.0
        f_all = []
        idx = 1
        for m in range(m_max+1):
            # epsilon is the Neumann factor, a rather obtuse way of saying this:
            epsilon = 1 if m == 0 else 2

            # reset the tolerance flags for the new m
            even_reached_tol = False
            odd_reached_tol = False

            for n in range(m, n_max+1):
                even = True if (m-n) % 2 == 0 else False

                if (even and even_reached_tol) or (not even and odd_reached_tol):
                    continue

                # s_bs = aswfb(m, n, h0, cos(theta), 1)
                # s_inc = aswfb(m, n, h0, cos(pi - theta), 1)
                s_bs = pro_ang1(m, n, h0, np.cos(theta))
                s_inc = pro_ang1(m, n, h0, np.cos(np.pi - theta))

                match model_type:
                    case 'fluid filled':
                        # r_type1A, dr_type1A, r_type2A, dr_type2A = rswfp(m, n, h0, xi0, 3)
                        # r_type1B, dr_type1B, _, _ = rswfp(m, n, h0/hc, xi0, 3)
                        # print(m,n,h0,xi0,flush=True)
                        r_type1A, dr_type1A = pro_rad1(m, n, h0, xi0)
                        r_type2A, dr_type2A = pro_rad2(m, n, h0, xi0)
                        r_type1B, dr_type1B, _, _ = pro_rad1(m, n, h0/hc, xi0)

                        eeA = r_type1A - rh*r_type1B/dr_type1B*dr_type1A
                        eeB = eeA + 1j*(r_type2A - rh*r_type1B/dr_type1B*dr_type2A)
                        aa = -eeA/eeB  # Furusawa (1988) Eq. 5 p 15
                    case 'pressure release':
                        # r_type1, _, r_type2, _ = rswfp(m, n, h0, xi0, 3)
                        r_type1, _ = pro_rad1(m, n, h0, xi0)
                        r_type2, _ = pro_rad2(m, n, h0, xi0)
                        aa = -r_type1/(r_type1 + 1j*r_type2)
                    case 'fixed rigid':
                        pass  # see eqn of (3) of Furusawa, 1988

                # This definition of the norm of S is in Yeh (1967), and is equation
                # 21.7.11 in Abramowitz & Stegun (10th printing) as the
                # Meixner-Schãfke normalisation scheme. Note that the RHS of
                # 21.7.11 doesn't give correct results compared to doing the actual
                # integration. Note also that the plain Matlab quad() function
                # fails to give correct answers also in some cases, so the quadgk()
                # function is used.
                #
                # Yeh, C. (1967). "Scattering of Acoustic Waves by a Penetrable
                #   Prolate Spheroid I Liquid Prolate Spheroid," J. Acoust. Soc.
                #   Am. 42, 518-521.
                #
                # Abramowitz, M., and Stegun, I. A. (1964). Handbook of
                #   Mathematical Functions with Formulas, Graphs, and Mathematical
                #   Tables (Dover, New York), 10th ed.

                # Matlab code uses quadgk as plain quad didn't work....
                n_mn = quad(self.aswfa2, -1, 1, args=(m, n, h0), epsrel=1e-5)

                x = epsilon / n_mn * s_inc * aa * s_bs * np.cos(m*(phi_bs - phi_inc))
                f += x

                tsx = 20*np.log10(abs(2/(1j*k0)*x) / (2*a))

                if n > (m+check_after):
                    if even and (tsx < tol):
                        even_reached_tol = True
                    elif not even and (tsx < tol):
                        odd_reached_tol = True

                # Apply the final factor and normalise to make it independent of
                # the physical size of the spheroid
                f_all.append(abs(2.0 / (1j*k0) * f) / (2.0*a))
                idx = idx + 1

            # end the iterations if the overall TS change is small
            if idx >= check_after:
                if (20*np.log10(f_all[-1]) - 20*np.log10(f_all[-2])) < 0.01:
                    break

        return np.numpy(20*np.log10(2*a*f_all))

        def aswfa2(self, eta, m, n, h0):
            """Need eta argument to be first for use in quad()."""
            # Calculates the square of S_mn for the given values of eta.
            return pro_ang1(m, n, h0, eta)[0]**2
