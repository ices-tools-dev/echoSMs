"""A class that implements the Kirchhoff ray mode scattering model."""

from math import cos, pi, radians, sin, sqrt

import numpy as np
from scipy.special import j0, jvp, y0, yvp

from .krmdata import KRMorganism, KRMshape
from .scattermodelbase import ScatterModelBase
from .utils import as_dict, wavenumber
from .utils import boundary_type as bt


def _u(x: float, z: float, theta: float) -> float:
    """KRM coordinate transform from x to u."""  # ruff: ignore[docstring-missing-returns]
    return np.array(x*sin(theta) - z*cos(theta))  # Eqn (4)


def _v(x: float, z: float, theta: float) -> float:
    """KRM coordinate transform from x to v."""  # ruff: ignore[docstring-missing-returns]
    return np.array(x*cos(theta) + z*sin(theta))  # Eqn (5)


def _deltau(x: float, theta: float) -> float:
    """KRM projection of delta x onto u."""  # ruff: ignore[docstring-missing-returns]
    return np.diff(x)*sin(theta)  # Eqn (6)


class KRMModel(ScatterModelBase):
    """Kirchhoff ray mode (KRM) scattering model."""

    def __init__(self) -> None:
        super().__init__()
        self.long_name = 'Kirchhoff ray mode'
        self.short_name = 'krm'
        self.analytical_type = 'approximate'
        self.boundary_types = [bt.fluid_filled]
        self.shapes = ['closed surfaces']
        self.max_ka = 20  # [1]
        self.no_expand_parameters = ['bodies']
        self.theta_min = 65  # [deg]
        self.theta_max = 115  # [deg]

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.scattermodelbase.ScatterModelBase.validate_parameters] for
        calling details.

        Raises
        ------
        KeyError
            If the incidence angles are outside the valid bounds.
        """
        p = as_dict(params)
        super()._present_and_positive(p, ['medium_c', 'medium_rho', 'f'])

        if np.any(np.atleast_1d(p['theta']) < self.theta_min) or\
             np.any(np.atleast_1d(p['theta']) > self.theta_max):
            raise KeyError('Incidence angle(s) (theta) are outside 65 to 115°')

    def calculate_ts_single(self, medium_c: float, medium_rho: float, theta: float,
                            f: float, organism: KRMorganism, high_ka_medium: str = 'body',
                            low_ka_medium: str = 'body',
                            validate_parameters: bool = True, **kwargs: dict) -> float:
        """Calculate the scatter using the Kirchhoff ray mode model for one set of parameters.

        Parameters
        ----------
        medium_c :
            Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho :
            Density in the fluid medium surrounding the target [kg/m³]
        theta :
            Pitch angle to calculate the scattering at, as per the echoSMs
            [coordinate system](conventions.md#coordinate-systems) [°].
        f :
            Frequency to calculate the scattering at [Hz].
        organism :
            The shapes that make up the model. This is typically a shape for the body and zero or
            more enclosed shapes that represent internal parts of the organism.
            Surface coordinates must be relative to the fish reference axis in Clay & Horne
            (1994), Fig. 3. The empirical body correction uses these coordinates directly.
        high_ka_medium :
            If set to `body`, use the body wavenumber for inclusions. If set to anything else
            (e.g., `water`), use the water wavenumber. The body/inclusion reflection coefficient
            remains that of Eqn (9).
            This parameter applies to the Kirchhoff approximation part of
            the model (i.e., high _ka_) and corresponds to the use (or not) of the
            approximation given in Clay & Horne (1994) on the line immediately below Eqn (13):
            _k_b ≈ k at low contrast_.
        low_ka_medium :
            If set to `body` the sound speed and density of the organism body is used for
            the fluid surrounding any inclusions. If set to anything else (e.g., `water`)
            the sound speed and density given by `medium_c` and `medium_rho` are used.
            This parameter applies to the mode solution part of the model (i.e., low _ka_)
            and corresponds to the use (or not) of the approximation given in Clay & Horne (1994)
            on the line immediately below Eqn (13): _k_b ≈ k at low contrast_.
        validate_parameters :
            Whether to validate the model parameters.
        kwargs :
            Additional names arguments are ignored.

        Returns
        -------
        :
            The target strength (re 1 m²) of the target [dB].

        Raises
        ------
        ValueError
            On invalid input parameters.

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
        America, 92(4), 2173-2180.
        <https://doi.org/10.1121/1.405211>

        Clay, C. S., & Horne, J. K. (1994). Acoustic models of fish: The Atlantic cod
        (_Gadus morhua_). The Journal of the Acoustical Society of America, 96(3), 1661-1668.
        <https://doi.org/10.1121/1.410245>

        Horne, J. K., & J. M. Jech. (1999). Multi-frequency estimates of fish abundance:
        constraints of rather high frequencies. ICES Journal of Marine Science, 56 (2), 184-199.
        <https://doi.org/10.1006/jmsc.1998.0432>

        """  # ruff: ignore[docstring-extraneous-exception]
        if validate_parameters:
            self.validate_parameters(locals())

        sl = self._scattering_length(medium_c, medium_rho, theta, f, organism,
                                     high_ka_medium, low_ka_medium)
        return 20*np.log10(abs(sl)) if sl != 0 else -np.inf

    def _scattering_length(self, medium_c, medium_rho, theta, f, organism,
                           high_ka_medium='body', low_ka_medium='body'):
        """Calculate the complex scattering length.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid surrounding the organism [m/s].
        medium_rho : float
            Density of the fluid surrounding the organism [kg/m³].
        theta : float
            Pitch angle in the echoSMs coordinate system [°].
        f : float
            Frequency [Hz].
        organism : KRMorganism
            The body and its inclusions.
        high_ka_medium : str
            Use the body wavenumber for inclusions if set to `body`; otherwise use the
            external fluid wavenumber. The reflection coefficient is for the body/inclusion
            interface.
        low_ka_medium : str
            Use the body as the surrounding medium for the modal calculation if set to
            `body`; otherwise use the external fluid.

        Returns
        -------
        complex
            The sum of the body and inclusion scattering lengths [m].

        Raises
        ------
        ValueError
            If an inclusion has an unsupported boundary condition.
        """
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
            if incl.boundary not in [bt.pressure_release, bt.fluid_filled]:
                raise ValueError(f'Unsupported boundary of "{incl.boundary}" for KRM inclusion')
            # Reflection coefficient between body and inclusion
            # The paper gives R_bc in terms of g & h, but it can also be done in the
            # same manner as R_wb above.
            gp = incl.rho / body.rho  # p is 'prime' to fit with paper notation
            hp = incl.c / body.c

            R_bc = (gp*hp-1) / (gp*hp+1)  # Eqn (9)

            # Equivalent radius of inclusion (as per Part A of paper)
            a_e = sqrt(incl.volume() / (pi * incl.length()))
            if a_e == 0:
                continue

            # Choose which modelling approach to use
            kk = k_b if low_ka_medium == 'body' else k
            if kk*a_e < 0.15:  # Do the mode solution for the inclusion
                if low_ka_medium != 'body':
                    gp = incl.rho / medium_rho
                    hp = incl.c / medium_c
                sl.append(self._mode_solution(gp, hp, kk, a_e, incl.length(), theta))
            elif incl.boundary == bt.pressure_release:
                kk = k_b if high_ka_medium == 'body' else k
                sl.append(self._soft_KA(incl, k, kk, R_bc, TwbTbw, theta))
            elif incl.boundary == bt.fluid_filled:
                kk = k_b if high_ka_medium == 'body' else k
                sl.append(self._fluid_KA(incl, k, kk, R_bc, TwbTbw, theta))

        # Do the Kirchhoff-ray approximation for the body. This is always done as a fluid.
        body_sl = self._fluid_KA(body, k, k_b, R_wb, TwbTbw, theta)

        return body_sl + sum(sl)

    def _mode_solution(self, g: float, h: float, k: float, a: float, L_e: float,
                       theta: float) -> complex:
        """Backscatter from a centred equivalent gas cylinder at low ka.

        Parameters
        ----------
        g :
            Ratio of shape density over surrounding medium density.
        h :
            Ratio of shape sound speed over surrounding medium sound speed.
        k :
            The wavenumber in the medium surrounding the shape.
        a :
            Equivalent radius of shape [m].
        L_e :
            Equivalent length of shape [m].
        theta :
            Pitch angle to calculate the scattering at, as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [rad].

        Returns
        -------
        :
            The scattering length [m].

        """  # ruff: ignore[docstring-missing-exception]
        # Note: equation references in this function are to Clay (1992)
        if h == 0.0:
            raise ValueError('Ratio of sound speeds (h) cannot be zero for low ka solution.')

        ka = k*a
        kca = ka/h

        # Avoid division by zero in C_0 for acoustically matched materials.
        N = jvp(0, kca)*y0(ka) - g*h*yvp(0, ka)*j0(kca)
        D = jvp(0, kca)*j0(ka) - g*h*jvp(0, ka)*j0(kca)
        b_0 = -D / (D+1j*N)  # Eqn (A1), m=0

        delta = k*L_e*cos(theta)  # Eqn (4)

        return -1j*L_e/pi * np.sinc(delta/pi) * b_0  # Eqn (15), chi = -pi/4

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
        return -1j*R_bc*TwbTbw/(2*sqrt(pi))\
            * np.sum(A_sb * (np.sqrt((k_b*a+1)*sin(theta))
                             * np.exp(-1j*(2*k_b*v+psi_p))*deltau))

    def _fluid_KA(self, shape: KRMshape, k: float, k_b: float, R_wb: float,
                  TwbTbw: float, theta: float) -> float:
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

        # Upper-surface coordinate relative to the fish reference axis, Eqn (15).
        z_U = (shape.z_U[0:-1] + shape.z_U[1:])/2

        psi_b = -pi*k_b*z_U / (2*(k_b*z_U + 0.4))  # Eqn (15)

        v_bU = _v(shape.x, shape.z_U, theta)
        v_bL = _v(shape.x, shape.z_L, theta)
        v_U = (v_bU[0:-1] + v_bU[1:])/2
        v_L = (v_bL[0:-1] + v_bL[1:])/2

        # Eqn (16)
        return -1j*R_wb/(2*sqrt(pi))\
            * np.sum(np.sqrt(k*a) * _deltau(shape.x, theta)
                     * (np.exp(-2j*k*v_U) - TwbTbw*np.exp(-2j*k*v_U + 2j*k_b*(v_U-v_L) + 1j*psi_b)))
