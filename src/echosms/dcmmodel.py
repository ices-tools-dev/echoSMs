"""A class that provides the model series deformed cylinder scattering model."""

from math import sin, cos, nan, pi, log10
from scipy.special import jv, hankel1, jvp, h1vp, yv, yvp
import numpy as np
from .utils import Neumann, wavenumber, as_dict, boundary_type as bt
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
        self.boundary_types = [bt.fixed_rigid, bt.pressure_release, bt.fluid_filled]
        self.shapes = ['finite cylinder']
        self.max_ka = 20  # [1]

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_in(p, ['boundary_type'], self.boundary_types)
        super()._present_and_positive(p, ['medium_rho', 'medium_c', 'a', 'b', 'f'])

        types = np.unique(np.atleast_1d(p['boundary_type']))
        for t in types:
            if t == bt.fluid_filled:
                super()._present_and_positive(p, ['target_c', 'target_rho'],
                                              mask=p['boundary_type'] == t)

    def calculate_ts_single(self, medium_c, medium_rho, a, b, theta, f, boundary_type: bt,
                            target_c=None, target_rho=None, validate_parameters=True,
                            **kwargs):
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
            Pitch angle to calculate the scattering as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].
        f : float
            Frequency to calculate the scattering at [Hz].
        boundary_type :
            The model type. Supported model types are given in the `boundary_types` class attribute.
        target_c : float, optional
            Sound speed in the fluid inside the sphere [m/s].
            Only required for `boundary_type` of ``fluid_filled``.
        target_rho : float, optional
            Density of the fluid inside the sphere [kg/m³].
            Only required for `boundary_type` of ``fluid_filled``.
        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) of the target [dB].

        Notes
        -----
        The class implements the code in Section B.1 of Jech et al. (2015).

        References
        ----------
        Jech, J.M., Horne, J.K., Chu, D., Demer, D.A., Francis, D.T.I., Gorska, N., Jones, B.,
        Lavery, A.C., Stanton, T.K., Macaulay, G.J., Reeder, D.B., Sawada, K., 2015.
        Comparisons among ten models of acoustic backscattering used in aquatic ecosystem
        research. Journal of the Acoustical Society of America 138, 3742–3764.
        <https://doi.org/10.1121/1.4937607>
        """
        if validate_parameters:
            self.validate_parameters(locals())

        if theta == 0.0:
            return nan

        theta_rad = theta*pi/180.
        kL = wavenumber(medium_c, f)*b
        K = wavenumber(medium_c, f) * sin(theta_rad)
        Ka = K*a

        m = range(30)  # TODO this needs to vary with f

        match boundary_type:
            case bt.fixed_rigid:
                series = map(lambda m: (-1)**m * Neumann(m)*(jvp(m, Ka) / h1vp(m, Ka)), m)
            case bt.pressure_release:
                series = map(lambda m: (-1)**m * Neumann(m)*(jv(m, Ka) / hankel1(m, Ka)), m)
            case bt.fluid_filled:
                g = target_rho/medium_rho
                h = target_c/medium_c
                gh = g*h
                Kda = K/h*a

                def Cm(m):
                    numer = (jvp(m, Kda)*yv(m, Ka)) / (jv(m, Kda)*jvp(m, Ka))\
                        - gh*(yvp(m, Ka)/jvp(m, Ka))
                    denom = (jvp(m, Kda)*jv(m, Ka)) / (jv(m, Kda)*jvp(m, Ka)) - gh
                    return numer/denom

                series = map(lambda m: 1j**(2*m) * Neumann(m) / (1 + 1j*Cm(m)), m)
            case _:
                raise ValueError(f'The {self.long_name} model does not support '
                                 f'a model type of "{boundary_type}".')

        fbs = 1j*b/pi * (sin(kL*cos(theta_rad)) / (kL*cos(theta_rad))) * sum(series)
        return 20*log10(abs(fbs))  # ts
