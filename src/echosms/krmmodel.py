"""A class that implements the Kirchhoff ray mode scattering model."""

from math import log10, pi, sqrt, cos, sin, radians
from cmath import exp
import numpy as np
from scipy.special import j0, y0, jvp, yvp
from .utils import wavenumber, as_dict, boundary_type as bt
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
        self.boundary_types = [bt.fluid_filled]
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

    def calculate_ts_single(self, medium_c, medium_rho, theta, f, organism,
                            high_ka_medium='body', low_ka_medium='body',
                            validate_parameters=True, **kwargs) -> float:
        """
        Calculate the scatter using the Kirchhoff ray mode model for one set of parameters.

        Warning
        --------
        The mode solution (low _ka_) part of this model has not yet been verified to give
        correct results.

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
        organism: KRMorganism
            The shapes that make up the model. This is typically a shape for the body and zero or
            more enclosed shapes that repesent internal parts of the organism.
        high_ka_medium:
            If set to `body` the sound speed and density of the organism body is used for
            the fluid surrounding any inclusions. If set to anything else (e.g., `water`)
            the sound speed and density given by `medium_c` and `medium_rho` are used.
            This parameter applies to the Kirchhoff approximation part of
            the model (i.e., high _ka_) and corresponds to the use (or not) of the
            approximation given in Clay & Horne (1994) on the line immediately below Eqn (13):
            _k_b ≈ k at low contrast_.
        low_ka_medium:
            If set to `body` the sound speed and density of the organism body is used for
            the fluid surrounding any inclusions. If set to anything else (e.g., `water`)
            the sound speed and density given by `medium_c` and `medium_rho` are used.
            This parameter applies to the mode solution part of the model (i.e., low _ka_)
            and corresponds to the use (or not) of the approximation given in Clay & Horne (1994)
            on the line immediately below Eqn (13): _k_b ≈ k at low contrast_.
        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) of the target [dB].

        Notes
        -----
        The class implements the code in Clay & Horne (1994) and when _ka_ < 0.15 uses Clay (1992).

        The `high_ka_medium` and `low_ka_medium` parameters allow the user to select which
        medium surrounds the inclusions (e.g., the swimbladder) - the fish body or
        the water surrounding the fish body. The equations in Clay & Horne (1994) used the body
        but included a sentence saying that the water could be used at low contrast
        (between the water and the body). A later paper
        (Horne & Jech, 1999) used water for low _ka_ (the mode solution) and the body for
        higher _ka_ (the Kirchhoff approximation). Some open-source KRM model codes always
        use the water.

        References
        ----------
        Clay, C. S. (1992). Composite ray-mode approximations for backscattered sound from
        gas-filled cylinders and swimbladders. The Journal of the Acoustical Society of
        America, 92(4), 2173–2180.
        <https://doi.org/10.1121/1.405211>

        Clay, C. S., & Horne, J. K. (1994). Acoustic models of fish: The Atlantic cod
        (_Gadus morhua_). The Journal of the Acoustical Society of America, 96(3), 1661–1668.
        <https://doi.org/10.1121/1.410245>

        Horne, J. K., & J. M. Jech. (1999). Multi–frequency estimates of fish abundance:
        constraints of rather high frequencies. ICES Journal of Marine Science, 56 (2), 184–199.
        <https://doi.org/10.1006/jmsc.1998.0432>
        """
        if validate_parameters:
            self.validate_parameters(locals())

        theta = radians(theta)

        body = organism.body

        k = wavenumber(medium_c, f)
        k_b = wavenumber(body.c, f)

        # Reflection coefficient between water and body
        R_wb = (body.rho*body.c - medium_rho*medium_c)\
            / (body.rho*body.c + medium_rho*medium_c)
        TwbTbw = 1-R_wb**2  # Eqn (15)

        sl = []  # scattering lengths for inclusions
        for incl in organism.inclusions:
            # Reflection coefficient between body and inclusion
            # The paper gives R_bc in terms of g & h, but it can also be done in the
            # same manner as R_wb above.
            gp = incl.rho / body.rho  # p is 'prime' to fit with paper notation
            hp = incl.c / body.c

            R_bc = (gp*hp-1) / (gp*hp+1)  # Eqn (9)

            # Equivalent radius of inclusion (as per Part A of paper)
            a_e = sqrt(incl.volume() / (pi * incl.length()))

            # Choose which modelling approach to use
            if k*a_e < 0.15:  # Do the mode solution for the inclusion
                if low_ka_medium != 'body':
                    gp = incl.rho / medium_rho
                    hp = incl.c / medium_c
                sl.append(self._mode_solution(1/gp, 1/hp, k, a_e, incl.length(), theta))
            elif incl.boundary == bt.pressure_release:
                kk = k_b if high_ka_medium == 'body' else k
                sl.append(self._soft_KA(incl, k, kk, R_bc, TwbTbw, theta))
            elif incl.boundary == bt.fluid_filled:
                kk = k_b if high_ka_medium == 'body' else k
                sl.append(self._fluid_KA(incl, k, kk, R_bc, TwbTbw, theta))
            else:
                raise ValueError(f'Unsupported boundary of "{incl.boundary}" for KRM inclusion')

        # Do the Kirchhoff-ray approximation for the body. This is always done as a fluid.
        body_sl = self._fluid_KA(body, k, k_b, R_wb, TwbTbw, theta)

        return 20*log10(abs(body_sl + sum(sl)))

    def _mode_solution(self, g: float, h: float, k: float, a: float, L_e: float,
                       theta: float) -> float:
        """Backscatter from a soft shape at low ka.

        Parameters
        ----------
        g :
            Ratio of medium density over shape density.
        h :
            Ratio of medium sound speed over shape sound speed.
        k :
            The wavenumber in the medium surrounding the shape.
        a :
            Equivalent radius of shape [m].
        L_e :
            Equivalent length of shape [m].
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

    def _soft_KA(self, shape: KRMshape, k: float, k_b: float, R_bc: float,
                 TwbTbw: float, theta: float) -> float:
        """Backscatter from a soft object using the Kirchhoff approximation.

        Parameters
        ----------
        shape :
            The shape.
        k :
            Wavenumber in the fluid surrounding the organism body.
        k_b :
            Wavenumber to use for the fluid surrounding the object.
        R_bc :
            Reflection coefficient between the object and the surrounding fluid.
        TwbTbw :
            Transmission coefficient between external media (e.g., water) and the body.
        theta :
            Pitch angle to calculate the scattering at, as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].

        Returns
        -------
        :
            The scattering length [m].
        """
        # Not low-ka model
        # Reflection coefficient: between water and body

        # The paper's notation gets confusing here - eqn (10) uses a_s and Eqn (11) uses a,
        # but they are the same quantity (radius of swimbladder for each short cylinder)
        a = np.array((shape.w[0:-1] + shape.w[1:])/4)  # Eqn (12)
        ka_s = k * a
        A_sb = ka_s / (ka_s + 0.083)  # Eqn (10)
        psi_p = ka_s / (40 + ka_s) - 1.05  # Eqn (10)

        v_sU = _v(shape.x, shape.z_U, theta)
        v = (v_sU[0:-1] + v_sU[1:])/2  # Eqn (13)

        deltau = _deltau(shape.x, theta)

        # This is Eqn (11)
        soft_sl = -1j*R_bc*TwbTbw/(2*sqrt(pi))\
            * np.sum(A_sb * (np.sqrt((k_b*a+1)*sin(theta))
                             * np.exp(-1j*(2*k_b*v+psi_p))*deltau))

        return soft_sl

    def _fluid_KA(self, shape, k, k_b, R_wb, TwbTbw, theta):
        """Backscatter from a fluid object using the Kirchhoff approximation.

        Parameters
        ----------
        shape :
            The shape.

        k :
            Wavenumber in the fluid surrounding the organism body.
        k_b :
            Wavenumber to use for the fluid surrounding the object.
        R_wb :
            Reflection coefficient between the object and the surrounding fluid.
        TwbTbw :
            Transmission coefficient between external media (e.g., water) and the surrounding fluid.
        theta :
            Pitch angle to calculate the scattering at, as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].

        Returns
        -------
        :
            The scattering length [m].
        """
        a = (shape.w[0:-1] + shape.w[1:])/4  # Eqn (12)

        # This isn't stated in the paper but seems approrpiate - is in the NOAA KRM code
        z_U = (shape.z_U[0:-1] + shape.z_U[1:])/2

        psi_b = -pi*k_b*z_U / (2*(k_b*z_U + 0.4))  # Eqn (15)

        v_bU = _v(shape.x, shape.z_U, theta)
        v_bL = _v(shape.x, shape.z_L, theta)
        v_U = (v_bU[0:-1] + v_bU[1:])/2
        v_L = (v_bL[0:-1] + v_bL[1:])/2

        # Eqn (16)
        fluid_sl = -1j*R_wb/(2*sqrt(pi))\
            * np.sum(np.sqrt(k*a) * _deltau(shape.x, theta)
                     * (np.exp(-2j*k*v_U) - TwbTbw*np.exp(-2j*k*v_U + 2j*k_b*(v_U-v_L) + 1j*psi_b)))

        return fluid_sl
