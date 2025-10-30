"""A class that provides a high-pass fluid sphere scattering model."""

from math import log10, pi, sin, cos, exp, radians
from .utils import wavenumber, as_dict, boundary_type as bt
from .scattermodelbase import ScatterModelBase


class HPModel(ScatterModelBase):
    """High-pass (HP) scattering model."""

    def __init__(self):
        super().__init__()
        self.long_name = 'high pass'
        self.short_name = 'hp'
        self.analytical_type = 'approximate'
        self.boundary_types = [bt.fluid_filled, bt.elastic, bt.fixed_rigid]
        self.shapes = ['sphere', 'prolate spheroid', 'cylinder', 'bent cylinder']
        self.max_ka = 20  # [1]

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_positive(p, ['medium_c', 'a', 'f'])

        if not p['shape'].isin(self.shapes).all():
            raise ValueError('The shape parameter must be one of: ' + ', '.join(self.shapes))

        if not p['boundary_type'].isin(self.boundary_types).all():
            raise ValueError('The boundary_type parameter must be one of: ' +
                             ', '.join(self.boundary_types))

    def calculate_ts_single(self, shape, medium_c, a, f, boundary_type: bt, medium_rho=None,
                            target_c=None, target_rho=None,
                            theta=None,
                            L=None, rho_c=None,
                            irregular=False,
                            validate_parameters=True, **kwargs) -> float:
        """
        Calculate the backscatter using the high pass model for one set of parameters.

        Parameters
        ----------
        shape : str
            The shape to model. Must be one of the shapes given in the `shapes` variable.
        medium_c : float
            Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho : float
            Density of the fluid medium surrounding the target [kg/m³]. Not required when
            `boundary_type` is `fixed_rigid`.
        target_c : float
            Longitudinal sound speed in the material inside the target [m/s]. Not required when
            `boundary_type` is `fixed_rigid`.
        target_rho : float
            Density of the material inside the target [kg/m³]. Not required when
            `boundary_type` is `fixed_rigid`.
        a : float
            Radius of the sphere, length of semi-minor axis of the prolate spheriod, or cylindrical
            radius of the straight or bent cylinder [m].
        f : float
            Frequency to calculate the scattering at [Hz].
        boundary_type :
            The boundary type for the model.
        theta : float
            Pitch angle to calculate the scattering as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°]. Only required for the straight cylinder shape.
        L : float
            Total length of the prolate spheroid and straight cylinder, or arc length of
            the bent cylinder [m]. Only required for prolate spheroid, cylinder, and bent cylinder
            shapes.
        rho_c : float
            Radius of curvature of the axis of the bent cylinder [m]. Only required for the
            bent cylinder shape.
        irregular :
            Set to `True` if the modelled object is not exactly a sphere, prolate spheroid,
            straight or uniformly beny cylinder.
        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) of the sphere [dB].

        Notes
        -----
        The class implements the high-pass model in Stanton (1989) for spheres, prolate spheroids,
        cylinders, and bent cylinders with fluid filled, elastic, and rigid fixed boundary
        conditions. There are several restrictions on valid input parameters, so a careful
        reading of Stanton (1989) is recommended.

        The theta angle convention used in Stanton (1989) is the same as the echoSMs
        [coordinate system convention](https://ices-tools-dev.github.io/echoSMs/
        conventions/#coordinate-systems).

        Stanton (1989) also provides parameters for gas-filled shapes, but more
        prior knowledge is required about the gas for useful results (e.g., damping
        characteristics of the gas and medium) and these have not been implemented here. There
        are many other models available that accurately model gas-filled shapes such that the
        lack of the high-pass gas-filled model should not be missed.

        References
        ----------
        Stanton, T. K. (1989). Simple approximate formulas for backscattering of sound
        by spherical and elongated objects. The Journal of the Acoustical Society of
        America, 86(4), 1499-1510.
        <https://doi.org/10.1121/1.398711>
        """
        if validate_parameters:
            self.validate_parameters(locals())

        if boundary_type == bt.fixed_rigid:
            # just need something large
            g = 1e20
            h = 1e20
        else:
            g = target_rho/medium_rho
            h = target_c/medium_c

        k = wavenumber(medium_c, f)

        G = 1.0
        F = 1.0

        def alpha_pic(g, h):
            return (1-g*h*h)/(2*g*h*h) + (1-g)/(1+g)

        match shape:
            case 'sphere':
                alpha_pis = (1-g*h*h)/(3*g*h*h) + (1-g)/(1+2*g)
                R = (g*h-1)/(g*h+1)
                if irregular:
                    match boundary_type:
                        case bt.fluid_filled:
                            F = 40 * (k*a)**(-0.4)
                            G = 1-0.8*exp(-2.5*(k*a-2.25)**2)
                        case bt.elastic:
                            F = 15 * (k*a)**(-1.9)
                        case bt.fixed_rigid:
                            F = 15 * (k*a)**(-1.9)

                sigma_bs = a*a * (k*a)**4 * alpha_pis**2 * G\
                    / (1 + 4*(k*a)**4 * alpha_pis**2/(R**2 * F))
            case 'prolate spheroid':
                a_pic = alpha_pic(g, h)
                if irregular:
                    match boundary_type:
                        case bt.fluid_filled:
                            F = 2.5 * (k*a)**(1.65)
                            G = 1-0.8*exp(-2.5*(k*a-2.3)**2)
                        case bt.elastic:
                            F = 1.8 * (k*a)**(-0.4)
                        case bt.fixed_rigid:
                            F = 1.8 * (k*a)**(-0.4)

                sigma_bs = 1/9 * L*L * (k*a)**4 * a_pic**2 * G\
                    / (1 + 16/9*(k*a)**4 * a_pic**2/(R**2 * F))
            case 'cylinder':
                theta = radians(theta)
                a_pic = alpha_pic(g, h)
                s = sin(k*L*cos(theta)) / (k*L*cos(theta))
                Ka = k*sin(theta)*a
                if irregular:
                    match boundary_type:
                        case bt.fluid_filled:
                            F = 3 * (k*a)**(0.65)
                            G = 1-0.8*exp(-2.5*(k*a-2.0)**2)
                        case bt.elastic:
                            F = 3.5 * (k*a)**(-1.0)
                        case bt.fixed_rigid:
                            F = 3.5 * (k*a)**(-1.0)

                sigma_bs = 0.25 * L*L * (Ka)**4 * a_pic**2 * s*s * G\
                    / (1 + pi*(Ka)**4 * a_pic**2/(R**2 * F))
            case 'bent cylinder':
                a_pic = alpha_pic(g, h)
                H = 1.
                if irregular:
                    match boundary_type:
                        case bt.fluid_filled:
                            F = 3.0 * (k*a)**(0.65)
                            G = 1-0.8*exp(-2.5*(k*a-2.0)**2)
                        case bt.elastic:
                            F = 2.5 * (k*a)**(-1.0)
                        case bt.fixed_rigid:
                            F = 2.5 * (k*a)**(-1.0)

                sigma_bs = 0.25 * L*L * (k*a)**4 * a_pic**2 * H*H*G\
                    / (1 + L*L*(k*a)**4 * a_pic**2 * H*H/(rho_c*a*R**2 * F))

        return 10*log10(sigma_bs)
