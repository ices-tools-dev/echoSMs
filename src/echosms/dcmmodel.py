"""A class that provides the model series deformed cylinder scattering model."""

from scipy.special import jv, hankel1, jvp, h1vp, yv, yvp
from math import sin, cos, nan, pi, log10
# from mapply.mapply import mapply
# import swifter
from .utils import eta, k
from .scattermodelbase import ScatterModelBase


class DCMModel(ScatterModelBase):
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
        self.shapes = ['finite cylinder']
        self.max_ka = 20  # [1]

    def calculate_ts_single(self, medium_c, medium_rho, a, b, theta, f, model_type,
                            target_c=None, target_rho=None, **kwargs):
        """
        Calculate the scatter from a finite cylinder using the modal series deformed cylinder model.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho : float
            Density of the fluid medium surrounding the target [kg/m³].
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
            Density of the fluid inside the sphere [kg/m³].
            Only required for `model_type` of ``fluid filled``

        Returns
        -------
        : float
            The target strength (re 1 m²) of the target [dB].

        Notes
        -----
        The class implements the code in Section B.1 of [1].

        References
        ----------
        [1] Jech, J.M., Horne, J.K., Chu, D., Demer, D.A., Francis, D.T.I., Gorska, N., Jones, B.,
        Lavery, A.C., Stanton, T.K., Macaulay, G.J., Reeder, D.B., Sawada, K., 2015.
        Comparisons among ten models of acoustic backscattering used in aquatic ecosystem
        research. Journal of the Acoustical Society of America 138, 3742–3764.
        <https://doi.org/10.1121/1.4937607>
        """
        if theta == 0.0:
            return nan

        theta_rad = theta*pi/180.
        kL = k(medium_c, f)*b
        K = k(medium_c, f) * sin(theta_rad)
        Ka = K*a

        m = range(30)  # this needs to vary with f

        # Some code varies with model type.
        match model_type:
            case 'fixed rigid':
                series = list(map(lambda m: (-1)**m * eta(m)*(jvp(m, Ka) / h1vp(m, Ka)), m))
            case 'pressure release':
                series = list(map(lambda m: (-1)**m * eta(m)*(jv(m, Ka) / hankel1(m, Ka)), m))
            case 'fluid filled':
                g = target_rho/medium_rho
                h = target_c/medium_c
                gh = g*h
                Kda = K/h*a

                def Cm(m):
                    numer = (jvp(m, Kda)*yv(m, Ka)) / (jv(m, Kda)*jvp(m, Ka))\
                        - gh*(yvp(m, Ka)/jvp(m, Ka))
                    denom = (jvp(m, Kda)*jv(m, Ka)) / (jv(m, Kda)*jvp(m, Ka)) - gh
                    return numer/denom

                series = list(map(lambda m: 1j**(2*m) * eta(m) / (1 + 1j*Cm(m)), m))
            case _:
                raise ValueError(f'The {self.long_name} model does not support '
                                 f'a model type of "{model_type}".')

        fbs = 1j*b/pi * (sin(kL*cos(theta_rad)) / (kL*cos(theta_rad))) * sum(series)
        return 20*log10(abs(fbs))  # ts
