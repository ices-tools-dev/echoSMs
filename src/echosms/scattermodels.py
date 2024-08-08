"""Classes that provide acoustic scattering models."""

import numpy as np
import pandas as pd
import xarray as xr
from mapply.mapply import mapply
# import swifter
from scipy.special import spherical_jn, spherical_yn, pro_ang1, pro_rad1, pro_rad2, jv, yv
from scipy.integrate import quad

# pylint: disable=too-many-arguments


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
        # Convert scalars to iterables for xarray to be happier later on
        for k, v in params.items():
            if not hasattr(v, '__iter__'):
                params[k] = [v]
        # Lengths of each parameter array
        sz = [len(v) for k, v in params.items()]
        # Create the DataArray
        return xr.DataArray(data=np.full(sz, np.nan), coords=params, name='ts')

    def k(c, f):
        """Calculate the acoustic wavenumber."""
        return 2*np.pi*f/c

    def h1(n, z, derivative=False):
        """Spherical Hankel function of the first kind or its' derivative."""
        if n < 0:
            raise ValueError('Negative n values are not valid for spherical Hankel functions.')

        if not derivative:
            return np.sqrt(np.pi/(2*z)) * jv(n+0.5, z)\
                + (np.sqrt(np.pi/(2*z)) * yv(n+0.5, z))*1j
        else:
            hn = (np.sqrt((np.pi) / (2*z))) * jv(n + 1/2, z)\
                + 1j * (np.sqrt(np.pi / (2*z))) * yv(n + 1/2, z)

            if n == 0:
                hn_plus1 = (np.sqrt(np.pi / (2*z))) * jv(n + 3/2, z)\
                    + 1j * (np.sqrt(np.pi / (2*z))) * yv(n + 3/2, z)
                return ((n / z) * hn - hn_plus1)
            elif n > 0:
                hn_minus1 = (np.sqrt(np.pi / (2*z))) * jv(n - 1/2, z)\
                    + 1j * (np.sqrt(np.pi / (2*z))) * yv(n - 1/2, z)
                return (hn_minus1 - ((n + 1) / z) * hn)


class ScatterModelBaseClass:
    """Base class for a class that provides a scattering model.

    All scattering models should inherit from this class and have a name that
    ends with 'Model'.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.long_name = ''  # the name in words
        self.short_name = ''  # an abbreviation
        self.analytical_type = ''  # 'exact', 'approximate'
        self.model_types = []  # 'fixed rigid', 'pressure release', 'fluid filled'
        self.shapes = []  # the target shapes that this model can simulate
        self.max_frequency = np.nan  # [Hz]
        self.min_frequency = np.nan  # [Hz]


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

    def calculate_ts(self, data, model_type):
        """Calculate the scatter using parameters from a Pandas DataFrame or Xarray DataArray.

        Parameters
        ----------
        data: Pandas DataFrame or Xarray DataArray or dictionary
            If a DataFrame, must contain columns names as per the function parameters in the
            calculate_ts_single() function in this class. Each row in the DataFrame will generate
            one TS output. If a DataArray, must contain coordinate names as per the function
            parameters in calculate_ts_single(). The TS will be calculated for all combinations of
            the coordinate variables. If dictionary, it will be converted to a DataFrame first.

        model_type: string
            The type of model boundary to apply. Valid values are given in the model_types class
            variable.

        Returns
        -------
        ts: array
            Returns the target strength calculated for all input parameters. Returns an iterable if
            the input data parameter was a DataFrame and a DataArray if the inuput was a DataArray.

        """
        if isinstance(data, dict):
            data = Utils.df_from_dict(data)
        elif isinstance(data, pd.DataFrame):
            pass
        elif isinstance(data, xr.DataArray):
            # For the moment just convert DataArrays into DataFrames
            data = data.to_dataframe().reset_index()
        else:
            raise ValueError(f'Variable type of {type(data)} is not supported'
                             ' (only dictionaries, Pandas DataFrames and Xarray DataArrays are).')

        multiprocess = True
        if multiprocess:
            # Using mapply:
            ts = mapply(data, self.__ts_helper, args=(model_type,), axis=1)
            # Using swifter
            # ts = df.swifter.apply(self.__ts_helper, args=(model_type,), axis=1)
        else:  # this uses just one CPU
            ts = data.apply(self.__ts_helper, args=(model_type,), axis=1)

        return ts.to_numpy()

    def __ts_helper(self, *args):
        """Convert function arguments and call calculate_ts()."""
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
        ts : the target strength of the object [dB re 1 m2].

        Notes
        -----
        The model implements the code in Anderson, 1950. Sound scattering from a fluid sphere.
        The Journal of the Acoustical Society of America, 22: 426–431.
        (https://doi.org/10.1121/1.1906621)
        """
        # pylint: disable=too-many-locals

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
                k1 = Utils.k(target_c, f)
                k1a = k1*a
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

    def __fluid_filled_ts_bs(self, medium_c, medium_rho, a, f, target_c, target_rho):
        """Fluid filled sphere model.

        This implementation only calculates the backscatter (theta=90deg).

        This code is directly derived from code written by M. Jech, available elsewhere in the
        echoSMs repository.
        """
        # Fixed model parameters
        # maximum order. Can be changed to improve precision
        order_max = 20

        # sound speed (h) and density (g) contrasts
        g = target_rho/medium_rho
        h = target_c/medium_c

        ###
        # reflectivity coefficient
        # Bessel functions from SciPy
        # spherical Bessel function of the 2nd kind is the Neumann function
        # Anderson uses Neumann function notation
        real = 0.0  # real component
        imag = 0.0  # imaginary component

        ka_sphere = (2*np.pi*f/target_c)*a
        ka_water = (2*np.pi*f/medium_c)*a
        for m in range(order_max):
            sphjkas = m/ka_sphere * spherical_jn(m, ka_sphere) - \
                spherical_jn(m+1, ka_sphere)
            sphjkaw = m/ka_water * spherical_jn(m, ka_water) - \
                spherical_jn(m+1, ka_water)
            sphykaw = m/ka_water * spherical_yn(m, ka_water) - \
                spherical_yn(m+1, ka_water)

            numer = sphjkas/sphjkaw * \
                spherical_yn(m, ka_water) / spherical_jn(m, ka_sphere) - \
                sphykaw/sphjkaw * g*h
            denom = sphjkas/sphjkaw * \
                spherical_jn(m, ka_water) / spherical_jn(m, ka_sphere) - g*h

            cscat = numer/denom
            real += ((-1.)**m) * (2.*m+1) / (1.+cscat**2)
            imag += ((-1.)**m) * (2.*m+1) * cscat/(1.+cscat**2)

        # reflectivity coefficient
        refl = (2/ka_water) * np.sqrt(real**2+imag**2)

        # convert to target strength (TS re 1 m^2 [dB])
        ts = 10*np.log10((refl*a)**2 / 4.)

        return ts


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

    def calculate_ts(self, medium_c, medium_rho, a, b, theta, freqs, model_type,
                     target_c=None, target_rho=None, **kwargs):
        """Manage the calling of the single frequency, single angle version of the PSMS code.

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
        ts : array of float with dimensions of (len(freq), len(angles)
            The scatter from the object [dB re 1 m2].
        freq : array of float
            The frequencies that apply to TS [Hz].
        angles : array of float
            The pitch angles that apply to TS [degrees].

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
        theta_rad = theta[0] * np.pi/180.
        ts_f = []
        for f in freqs:
            ts = self.calculate_ts_one_f(medium_c, medium_rho, a, b, theta_rad, f, model_type,
                                         target_c, target_rho)
            ts_f.append(ts)

        return np.array(ts_f, theta, ndmin=2)

    def calculate_ts_one_f(self, medium_c, medium_rho, a, b, theta, freq, model_type,
                           target_c=None, target_rho=None):
        """Prolate spheroid modal series (PSMS) solution model."""
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
