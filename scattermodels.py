"""Classes that provide acoustic scattering models."""

import numpy as np
from scipy.special import spherical_jn, spherical_yn

# pylint: disable=too-many-arguments


class ScatterModel:
    """Base class for a class that provides a scattering model."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.long_name = ''  # the name in words
        self.short_name = ''  # an abbreviation
        self.analytical_type = ''  # 'exact', 'approximate'
        self.boundary_types = []  # 'fixed rigid', 'pressure release', 'fluid filled'
        self.max_frequency = np.NaN  # [Hz]
        self.min_frequency = np.NaN  # [Hz]
        self.backscatter = False
        self.scatter = False

    def calculate_ts(self, water_c, water_rho, a, angles, freqs, boundary):
        """Calculate the scatter from an object.

        Parameters
        ----------
        water_c : float
            Sound speed in the water surrounding the object [m/s].
        water_rho: float
            Density of the water surrounding the object [kg/m3].
        a : float
            Radius of the object [m].
        angle: float or array of float
            Angle(s) to calculate the scattering at [rad].
        freq: float or array of float
            Frequencies to calculate the scattering at [Hz].
        boundary: str
            The boundary condition on the sphere surface.

        Returns
        -------
        sigma : array of float with dimensions of (len(freq), len(angle))
            The scatter from the object [m2].
        freq : array of float
            The frequencies that apply to sigma [Hz].
        angle : array of float
            The angles that apply to sigma [rad].
        """
        pass


class MSSModel(ScatterModel):
    """Modal series solution (MSS) scattering model.

    This class contains methods to calculate acoustic scatter from spheres and shells with various
    boundary conditions.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'modal series solution'
        self.short_name = 'mss'
        self.analytical_type = 'exact'
        self.boundary_types = ['fixed rigid', 'pressure release', 'fluid filled']
        self.max_frequency = 200.0e3  # [Hz]
        self.min_frequency = 1.0  # [Hz]
        self.backscatter = True

    def calculate_ts(self, water_c, water_rho, sphere_c, sphere_rho, a, angles, freqs, boundary):
        """Calculate the scatter using the mss model.

        Parameters
        ----------
        water_c : float
            Sound speed in the water surrounding the object [m/s].
        water_rho: float
            Density of the water surrounding the object [kg/m3].
        a : float
            Radius of the object [m].
        angle: float or array of float
            Angle(s) to calculate the scattering at [rad].
        freq: float or array of float
            Frequencies to calculate the scattering at [Hz].
        boundary: str
            The boundary condition on the sphere surface.

        Returns
        -------
        sigma : array of float with dimensions of (len(freq), len(angle))
            The scatter from the object [m2].
        freq : array of float
            The frequencies that apply to sigma [Hz].
        angle : array of float
            The angles that apply to sigma [rad].

        Notes
        -----
        The model implements the code in Anderson, 1950. Sound scattering from a fluid sphere.
        The Journal of the Acoustical Society of America, 22: 426–431.
        (https://doi.org/10.1121/1.1906621)


        """

        # pylint: disable=too-many-locals

        match boundary:
            case 'fixed rigid' | 'pressure release':
                raise ValueError(f'Boundary type "{boundary}" has not yet been implemented '
                                 f'for the {self.long_name} model.')
            case 'fluid filled':
                # Fixed model parameters
                # maximum order. Can be changed to improve precision
                order_max = 20

                ###
                # set up output variables
                # reflectivity coefficient
                refl = []
                # ka
                ka = []

                # sound speed (h) and density (g) contrasts
                g = sphere_rho/water_rho  # df
                h = sphere_c/water_c

                # real component
                real = 0.0
                # imaginary component
                imag = 0.0
                ###
                # reflectivity coefficient
                # Bessel functions from SciPy
                # spherical Bessel function of the 2nd kind is the Neumann function
                # Anderson uses Neumann function notation
                for f in freqs:
                    ka_sphere = (2*np.pi*f/sphere_c)*a
                    ka_water = (2*np.pi*f/water_c)*a
                    ka.append(ka_water)
                    for m in range(order_max):
                        sphjkas = (m/ka_sphere)*spherical_jn(m, ka_sphere) - \
                            spherical_jn(m+1, ka_sphere)
                        sphjkaw = (m/ka_water)*spherical_jn(m, ka_water)-spherical_jn(m+1, ka_water)
                        sphykas = (m/ka_sphere)*spherical_yn(m, ka_sphere) - \
                            spherical_yn(m+1, ka_sphere)
                        sphykaw = (m/ka_water)*spherical_yn(m, ka_water)-spherical_yn(m+1, ka_water)
                        alphaw = (2.*m+1.)*sphjkaw
                        alphas = (2.*m+1.)*sphjkas
                        beta = (2.*m+1)*sphykaw
                        numer = (alphas/alphaw)*(spherical_yn(m, ka_water) /
                                                 spherical_jn(m, ka_sphere)) - \
                                ((beta/alphaw)*(g*h))
                        denom = (alphas/alphaw)*(spherical_jn(m, ka_water) /
                                                 spherical_jn(m, ka_sphere))-(g*h)
                        cscat = numer/denom
                        real = real+((-1.)**m)*(2.*m+1)/(1.+cscat**2)
                        imag = imag+((-1.)**m)*(2.*m+1)*cscat/(1.+cscat**2)

                    refl.append((2/ka_water)*np.sqrt(real**2+imag**2))
                    imag = 0.0
                    real = 0.0

                # convert to numpy arrays
                refl = np.array(refl, dtype=float)
                ka = np.array(ka, dtype=float)

                # convert to target strength (TS dB re m^2)
                # s is the cross-sectional area of the sphere
                s = np.pi*a**2
                # 4pi is for backscatter
                ts = 10*np.log10(refl**2 * s)-10*np.log10(4 * np.pi)
            case _:
                raise ValueError(f'The {self.long_name} model does not support '
                                 f'a boundary type of "{boundary}".')
        return (freqs, 0.0, ts)


class PSMSModel(ScatterModel):
    """Prolate spheroidal modal series (PSMS) scattering model.

    This class contains methods to calculate acoustic scatter from prolate spheroids with various
    boundary conditions.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'prolate spheroidal modal series'
        self.short_name = 'psms'
        self.analytical_type = 'exact'
        self.boundary_types = ['fixed rigid', 'pressure release', 'fluid filled']
        self.max_frequency = 200.0e3  # [Hz]
        self.min_frequency = 1.0  # [Hz]
        self.backscatter = True

    def calculate_ts(self, water_c, water_rho, a, angles, freqs, boundary):
        """Prolate spheroid modal series (PSMS) solution model.

        This method calculates acoustic scatter from spheres and shells with various
        boundary conditions.

        Parameters
        ----------
        water_c : float
        water_rho: float

        Returns
        -------
        sigma_bs : array of float
        freq : array of float
        """
        match boundary:
            case 'fixed rigid' | 'pressure release' | 'fluid filled':
                raise ValueError(f'Boundary type "{boundary}" has not yet been implemented '
                                 f'for the {self.long_name} model.')
            case _:
                raise ValueError(f'The {self.long_name} model does not support '
                                 f'a boundary type of "{boundary}".')
