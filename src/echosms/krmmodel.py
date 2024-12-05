"""A class that provides the Kirchhoff ray mode scattering model."""

from math import log10, pi, sqrt, cos, sin, radians
from cmath import exp
import numpy as np
from scipy.special import j0, y0, jvp, yvp
from .utils import wavenumber, as_dict
from .scattermodelbase import ScatterModelBase
from .krmdata import KRMshape


def _u(x, z, theta):
    """KRM coordinate transform from x to u."""
    return np.array(x*sin(theta) - z*cos(theta))  # Eqn (4)


def _v(x, z, theta):
    """KRM coordinate transform from x to v."""
    return np.array(x*cos(theta) + z*sin(theta))  # Eqn (5)


def _deltau(x, theta):
    """KRM projection of delta x onto u."""
    return np.diff(x)*sin(theta)  # Eqn (6)


class KRMModel(ScatterModelBase):
    """Kirchhoff ray mode (KRM) scattering model."""

    def __init__(self):
        super().__init__()
        self.long_name = 'Kirchhoff ray mode'
        self.short_name = 'krm'
        self.analytical_type = 'approximate'
        self.boundary_types = ['fluid filled']
        self.shapes = ['closed surfaces']
        self.max_ka = 20  # [1]
        self.no_expand_parameters = ['bodies']

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_positive(p, ['medium_c', 'f'])

        if np.any(np.atleast_1d(p['theta']) < 65) or np.any(np.atleast_1d(p['theta']) > 115):
            raise KeyError('Incidence angle(s) (theta) are outside 65 to 115°')

        # k = wavenumber(p['medium_c'], p['f'])
        # a = np.array((swimbladder.w[0:-1] + swimbladder.w[1:])/4)  # Eqn (12)
        # if np.any(ka_s <= 0.15):
        #     warnings.warn('Some ka_s is below the limit.')

    def calculate_ts_single(self, medium_c, medium_rho, theta, f, bodies,
                            validate_parameters=True, **kwargs) -> float:
        """
        Calculate the scatter using the Kirchhoff ray mode model for one set of parameters.

        Warning
        --------
        The low _ka_ part of this model has not yet been verified to give correct results.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho : float
            Density in the fluid medium surrounding the target [kg/m³]
        theta : float
            Pitch angle to calculate the scattering at, as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].
        f : float
            Frequency to calculate the scattering at [Hz].
        bodies: KRMorganism
            The body shapes that make up the model. Currently, `bodies` should contain only two
            shapes, one of which should have a boundary of `fluid` (aka, the fish body) and the
            other a boundary of `soft` (aka, the swimbladder). KRMorganism.shapes[0] should be the
            fish body and KRMorganism.shapes[1] the swimbladder.
        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) of the target [dB].

        Notes
        -----
        The class implements the code in Clay & Horne (1994) and when ka < 0.15 uses Clay (1992).

        References
        ----------
        Clay, C. S., & Horne, J. K. (1994). Acoustic models of fish: The Atlantic cod
        (_Gadus morhua_). The Journal of the Acoustical Society of America, 96(3), 1661–1668.
        <https://doi.org/10.1121/1.410245>

        Clay, C. S. (1992). Composite ray-mode approximations for backscattered sound from
        gas-filled cylinders and swimbladders. The Journal of the Acoustical Society of
        America, 92(4), 2173–2180.
        <https://doi.org/10.1121/1.405211>
        """
        if validate_parameters:
            self.validate_parameters(locals())

        theta = radians(theta)

        # Interim setup - eventual plan is to accept multiple shapes, but need to sort out
        # correct reflection coefficient calculations to do that.
        body = bodies.shapes[0]
        target_rho = body.rho
        target_c = body.c
        swimbladder = bodies.shapes[1]
        swimbladder_rho = swimbladder.rho
        swimbladder_c = swimbladder.c

        k = wavenumber(medium_c, f)
        k_b = wavenumber(target_c, f)

        # Reflection coefficient between water and body
        R_wb = (target_rho*target_c - medium_rho*medium_c)\
            / (target_rho*target_c + medium_rho*medium_c)
        TwbTbw = 1-R_wb**2  # Eqn (15)

        # Reflection coefficient: between body and swimbladder
        # The paper gives R_bc in terms of g & h, but it can also be done in the
        # same manner as R_wb above.
        gp = swimbladder_rho / target_rho  # p is 'prime' to fit with paper notation
        hp = swimbladder_c / target_c
        R_bc = (gp*hp-1) / (gp*hp+1)  # Eqn (9)

        # Equivalent radius of swimbladder (as per Part A of paper)
        a_e = sqrt(swimbladder.volume() / (pi * swimbladder.length()))

        # Choose which modelling approach to use
        if k*a_e < 0.15:
            # Do the mode solution for the swimbladder (and ignore the body?)
            # TODO: need to check if it should be target or medium for the numerators
            g = target_rho / swimbladder_rho
            h = target_c / target_c
            mode_sl = self._mode_solution(swimbladder, g, h, k, a_e, swimbladder.length(), theta)
            return 20*log10(abs(mode_sl))

        # Do the Kirchhoff-ray approximation for the swimbladder and body
        soft_sl = self._soft_KA(swimbladder, k, k_b, R_bc, TwbTbw, theta)
        fluid_sl = self._fluid_KA(body, k, k_b, R_wb, TwbTbw, theta)

        return 20*log10(abs(soft_sl + fluid_sl))

    def _mode_solution(self, swimbladder: KRMshape, g: float, h: float,
                       k: float, a: float, L_e: float, theta: float) -> float:
        """Backscatter from a soft swimbladder at low ka.

        Parameters
        ----------
        swimbladder :
            The shape.
        g :
            Ratio of medium density over swimbladder density.
        h :
            Ratio of medium sound speed over swimbladder sound speed.
        k :
            The wavenumber in the medium surrounding the swimbladder.
        a :
            Equivalent radius of swimbladder [m].
        L_e :
            Equivalent length of swimbladder [m].
        theta :
            Pitch angle to calculate the scattering at, as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].

        Returns
        -------
        :
            The scattering length [m].
        """
        # Note: equation references in this function are to Clay (1992)
        if h == 0.0:
            raise ValueError('Ratio of sound speeds (h) cannot be zero for low ka solution.')

        # Chi is approximately this. More accurate equations are in Appendix B of Clay (1992)
        chi = -pi/4  # Eqn (B10) and paragraph below that equation

        ka = k*a
        kca = ka/h

        C_0 = (jvp(0, kca)*y0(ka) - g*h*yvp(0, ka)*j0(kca))\
            / (jvp(0, kca)*j0(ka) - g*h*jvp(0, ka)*j0(kca))  # Eqn (A1) with m=0
        b_0 = -1 / (1+1j*C_0)  # Also Eqn (A1)

        delta = k*L_e*cos(theta)  # Eqn (4)

        S_M = (exp(1j*(chi - pi/4)) * L_e)/pi * sin(delta)/delta * b_0  # Eqn (15)

        return S_M

    def _soft_KA(self, swimbladder, k, k_b, R_bc, TwbTbw, theta):
        """Backscatter from a soft object using the Kirchhoff approximation."""
        # Not low-ka model
        # Reflection coefficient: between water and body

        # The paper's notation gets confusing here - eqn (10) uses a_s and Eqn (11) uses a,
        # but they are the same quantity (radius of swimbladder for each short cylinder)
        a = np.array((swimbladder.w[0:-1] + swimbladder.w[1:])/4)  # Eqn (12)
        ka_s = k * a
        A_sb = ka_s / (ka_s + 0.083)  # Eqn (10)
        psi_p = ka_s / (40 + ka_s) - 1.05  # Eqn (10)

        v_sU = _v(swimbladder.x, swimbladder.z_U, theta)
        v = (v_sU[0:-1] + v_sU[1:])/2  # Eqn (13)

        deltau = _deltau(swimbladder.x, theta)

        # Swimbladder backscatter
        # Note - the paper has k_b rather than k in this formula, but in the text after Eqn (13)
        # states that "k_b ≈ k at low contrast". Two other implementations of the KRM use k
        # here instead of k_b, so we follow that in this code too.
        # But, if k_b is used instead of k with the fish properties in the paper, the final TS
        # can be a dB or so different.

        # This is Eqn (11)
        soft_sl = -1j*R_bc*TwbTbw/(2*sqrt(pi))\
            * np.sum(A_sb * (np.sqrt((k*a+1)*sin(theta))
                             * np.exp(-1j*(2*k*v+psi_p))*deltau))

        return soft_sl

    def _fluid_KA(self, body, k, k_b, R_wb, TwbTbw, theta):
        """Backscatter from a fluid object using the Kirchhoff approximation."""
        # Body backscatter
        a = (body.w[0:-1] + body.w[1:])/4  # Eqn (12) but for the body, not swimbladder

        # This isn't stated in the paper but seems approrpiate - is in the NOAA KRM code
        z_U = (body.z_U[0:-1] + body.z_U[1:])/2

        psi_b = -pi*k_b*z_U / (2*(k_b*z_U + 0.4))

        v_bU = _v(body.x, body.z_U, theta)
        v_bL = _v(body.x, body.z_L, theta)
        v_U = (v_bU[0:-1] + v_bU[1:])/2
        v_L = (v_bL[0:-1] + v_bL[1:])/2

        fluid_sl = -1j*R_wb/(2*sqrt(pi))\
            * np.sum(np.sqrt(k*a) * _deltau(body.x, theta)
                     * (np.exp(-2j*k*v_U)
                        - TwbTbw*np.exp(-2j*k*v_U + 2j*k_b*(v_U-v_L) + 1j*psi_b)))

        return fluid_sl
