"""A class that provides the Kirchhoff ray mode scattering model."""

from math import log10, pi, sqrt, cos, sin, radians
import numpy as np
from .utils import wavenumber, as_dict
from .scattermodelbase import ScatterModelBase


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
        self.no_expand_parameters = ['body', 'swimbladder']

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_positive(p, ['medium_c', 'f'])

        # p['theta'] >= 65 and p['theta'] <= 115

        # k = wavenumber(medium_c, f)
        # a = np.array((swimbladder.w[0:-1] + swimbladder.w[1:])/4)  # Eqn (12)
        # if np.any(ka_s <= 0.15):
        #     warnings.warn('Some ka_s is below the limit.')

    def calculate_ts_single(self, medium_c, medium_rho, target_c, target_rho,
                            swimbladder_c, swimbladder_rho,
                            theta, f, body, swimbladder,
                            validate_parameters=True, **kwargs) -> float:
        """
        Calculate the scatter using the krm model for one set of parameters.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho : float
            Density in the fluid medium surrounding the target [kg/m³]
        target_c : float
            Sound speed in the target body [m/s].
        target_rho : float
            Density in the target body [kg/m³]
        swimbladder_c : float
            Sound speed in the swimbladder [m/s].
        swimbladder_rho : float
            Density in the swimbladder [kg/m³].
        theta : float
            Pitch angle to calculate the scattering as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].
        f : float
            Frequency to calculate the scattering at [Hz].
        body : namedtuple(KRMshape)
            The target body. This parameter must provide numpy.ndarray attributes with names of:

            - `x`
            - `w`
            - 'z_U`
            - `z_L`

        swimbladder : namedtuple(KRMshape)
            The target internal body (e.g., fish swimbladder). This parameter must provide
            numpy.ndarray attributes with names of:

            - `x`
            - `w`
            - 'z_U`
            - `z_L`

        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) of the target [dB].

        Notes
        -----
        The class implements the code in Clay & Horne (1994). Backscatter when ka < 0.15 are
        as per Clay (1992).

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
        a_e = sqrt(self._volume(swimbladder)
                   / (pi * (np.max(swimbladder.x) - np.min(swimbladder.x))))
        a_e = 10

        # Choose which modelling approach to use
        if k*a_e < 0.15:
            # Do the mode solution for the swimbladder (and ignore the body?)
            mode_sl = self._mode_solution(swimbladder)
            return 20*log10(abs(mode_sl))
        else:
            # Do the Kirchhoff-ray approximation for the swimbladder and body
            soft_sl = self._soft_KA(swimbladder, k, k_b, R_bc, TwbTbw, theta)
            fluid_sl = self._fluid_KA(body, k, k_b, R_wb, TwbTbw, theta)
            return 20*log10(abs(soft_sl + fluid_sl))

    def _volume(self, shape):
        """Volume of the object."""
        return 1.0

    def _mode_solution(self, swimbladder):
        """Backscatter from a soft swimbladder at low ka."""
        return -1.

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
