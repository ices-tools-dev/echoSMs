"""A class that provides the prolate spheroidal modal series scattering model."""

import numpy as np
from .scattermodelbase import ScatterModelBase
import scipy.integrate as integrate
from .utils import pro_rad1, pro_rad2, pro_ang1, wavenumber, Neumann, as_dict, boundary_type as bt


class PSMSModel(ScatterModelBase):
    """Prolate spheroidal modal series (PSMS) scattering model.

    Note
    ----
    The fluid filled boundary type implementation is under development and is of limited use
    at the moment.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'prolate spheroidal modal series'
        self.short_name = 'psms'
        self.analytical_type = 'exact'
        self.boundary_types = [bt.fixed_rigid, bt.pressure_release, bt.fluid_filled]
        self.shapes = ['prolate spheroid']
        self.max_ka = 10  # [1]

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_in(p, ['boundary_type'], self.boundary_types)
        super()._present_and_positive(p, ['medium_c', 'medium_rho', 'a', 'b', 'f'])

        types = np.unique(np.atleast_1d(p['boundary_type']))
        for t in types:
            if t == bt.fluid_filled:
                super()._present_and_positive(p, ['target_c', 'target_rho'],
                                              mask=p['boundary_type'] == t)

    def calculate_ts_single(self, medium_c, medium_rho, a, b, theta, f, boundary_type: bt,
                            target_c=None, target_rho=None, validate_parameters=True):
        """Prolate spheroid modal series (PSMS) solution model.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho : float
            Density of the fluid medium surrounding the target [kg/m³].
        a : float
            Prolate spheroid major axis radius [m].
        b : float
            Prolate spheroid minor axis radius [m].
        theta : float
            Pitch angle to calculate the scattering as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].
        f : float
            Frequency to calculate the scattering at [Hz].
        boundary_type :
            The model type. Supported model types are given in the `boundary_types` class variable.
        target_c : float
            Sound speed in the fluid inside the target [m/s].
            Only required for `boundary_type` of ``fluid_filled``.
        target_rho : float
            Density of the fluid inside the target [kg/m³].
            Only required for `boundary_type` of ``fluid_filled``.
        validate_parameters : bool
            Whether to validate the input parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) of the target [dB].

        Notes
        -----
        The backscattered target strength of a pressure release or fluid-filled prolate spheroid
        is calculated using the PSMS method of Furusawa (1988) and corrections in
        Furusawa et al. (1994).

        References
        ----------
        Furusawa, M. (1988). "Prolate spheroidal models for predicting general
            trends of fish target strength," J. Acoust. Soc. Jpn. 9, 13-24.
        Furusawa, M., Miyanohana, Y., Ariji, M., and Sawada, Y. (1994).
            “Prediction of krill target strength by liquid prolate spheroid
            model,” Fish. Sci., 60, 261-265.
        """
        if validate_parameters:
            self.validate_parameters(locals())

        if boundary_type not in self.boundary_types:
            raise ValueError(f'The {self.long_name} model does not support '
                             f'a model type of "{boundary_type}".')

        xim = (1.0 - (b/a)**2)**(-0.5)
        q = a/xim  # semi-focal length

        km = wavenumber(medium_c, f)
        hm = km*q

        if boundary_type == bt.fluid_filled:
            g = target_rho / medium_rho
            ht = wavenumber(target_c, f)*q
            simplified = False
            # Note: we can implement simpler equations if sound speeds are
            # similar between the medium and the target. The simplified
            # equations are quicker, so it is worth to do.
            # But, it appears that target_c ≈ medium_c is not the only requirement for
            # the simplification to work well - see section 4.1.1 in:
            #
            # Gonzalez, J. D., Lavia, E. F., Blanc, S., & Prario, I. (2016).
            # Acoustic scattering by prolate and oblate liquid spheroids.
            # Proceedings of the 22nd International Congress on Acoustics.
            # Acoustics for the 21st Century, Buenos Aires.
            #
            # So, for the moment, the simplification is turned off.

            # if abs(1.0-target_c/medium_c) <= 0.01:
            #    simplified = True

        # Phi, the roll angle is fixed for this implementation
        phi_inc = np.pi  # incident direction
        phi_sca = np.pi + phi_inc  # scattered direction

        theta_inc = np.deg2rad(theta)  # incident direction
        theta_sca = np.pi - theta_inc  # scattered direction

        # Approximate limits on the summations. These come from Furusawa (1988), but other
        # implementations of this code use more complex functions to calculate the maximum orders
        # of spheroidal wave functions to calculate. It is also feasible to work to a defined
        # convergence level. This is a potenital future improvement.
        m_max = int(np.ceil(2*km*b))  # +1
        n_max = int(m_max + np.ceil(hm/2))  # +3

        f_sca = 0.0
        for m in range(m_max+1):
            epsilon_m = Neumann(m)
            cos_term = np.cos(m*(phi_sca - phi_inc))

            if boundary_type == bt.fluid_filled and not simplified:
                Am = PSMSModel._fluidfilled(m, n_max, hm, ht, xim, g, theta_inc)

            for n_i, n in enumerate(range(m, n_max+1)):
                # Use the normalisation offered by spheroidalwavefunctions.pro_ang1() because
                # it removes the need to calculate a normalisation factor (N_mn in Furusawa, 1998).
                # This is because the pro_ang1(norm=True) norm is unity.
                Smn_inc, _ = pro_ang1(m, n, hm, np.cos(theta_inc), norm=True)
                Smn_sca, _ = pro_ang1(m, n, hm, np.cos(theta_sca), norm=True)

                # FYI, the code used to use the Meixner-Schäfke normalisation scheme for the
                # angular function of the first kind (eqn 21.7.11 in Abramowitz, M., and Stegun,
                # I. A. (1964). Handbook of Mathematical Functions with Formulas, Graphs, and
                # Mathematical Tables # (Dover, New York), 10th ed.
                # N_mn = 2/(2*n+1) * factorial(n+m) / factorial(n-m)

                R1m, dR1m = pro_rad1(m, n, hm, xim)
                R2m, dR2m = pro_rad2(m, n, hm, xim)

                match boundary_type:
                    case bt.fluid_filled:
                        if simplified:
                            E1, E3 = PSMSModel._fluidfilled_Emn(m, n, n, hm, ht, xim, g)
                            Amn = -E1/E3
                        else:
                            Amn = Am[n_i][0]
                    case bt.pressure_release:
                        Amn = -R1m/(R1m + 1j*R2m)
                    case bt.fixed_rigid:
                        Amn = -dR1m/(dR1m + 1j*dR2m)

                f_sca += epsilon_m * Smn_inc * Amn * Smn_sca * cos_term

        return 20*np.log10(np.abs(-2j / km * f_sca))

    @staticmethod
    def _fluidfilled_Emn(m, n, ell, hm, ht, xim, g):
        """Calculate Emn_i values where i = 1 and 3."""
        R1mn_w, dR1mn_w = pro_rad1(m, n, hm, xim)
        R2mn_w, dR2mn_w = pro_rad2(m, n, hm, xim)
        R1ml_t, dR1ml_t = pro_rad1(m, ell, ht, xim)

        R3mn_w = R1mn_w + 1j*R2mn_w
        dR3mn_w = dR1mn_w + 1j*dR2mn_w

        E1 = R1mn_w - g * R1ml_t / dR1ml_t * dR1mn_w
        E3 = R3mn_w - g * R1ml_t / dR1ml_t * dR3mn_w

        return E1, E3

    @staticmethod
    def _fluidfilled(m, n_max, hm, ht, xim, g, theta_inc):
        """Calculate Amn for fluid filled prolate spheroids."""
        # Rather than implement eqn (4) in Furusawa (1988), use an alternative form that
        # I found easier to understand. This is eqns 5, 6, 7, and 8 in:
        #
        # Gonzalez, J. D., Lavia, E. F., Blanc, S., & Prario, I. (2016).
        # Acoustic scattering by prolate and oblate liquid spheroids.
        # Proceedings of the 22nd International Congress on Acoustics.
        # Acoustics for the 21st Century, Buenos Aires.

        Q = np.full((n_max+1-m, n_max+1-m), 0+0j)
        f = np.full((n_max+1-m, 1), 0+0j)

        for ell in range(m, n_max+1):
            for n in range(m, n_max+1):
                Smn_w_inc, _ = pro_ang1(m, n, hm, np.cos(theta_inc), norm=True)

                if not Smn_w_inc == 0.0:  # reduces CPU effort as this happens often
                    E1, E3 = PSMSModel._fluidfilled_Emn(m, n, ell, hm, ht, xim, g)

                    alpha_nl = integrate.quad(PSMSModel._alpha_int, -1, 1, (m, n, ell, hm, ht))[0]
                    # By using norm=True when calculating Smn_w_inc, dividing
                    # by a norm is not necessary, so the equations below differ from
                    # those in Gonzalez et al - they don't have the Nmn division.
                    Q[ell-m, n-m] = 1j**n * alpha_nl * Smn_w_inc * -E3
                    f[ell-m] += 1j**n * alpha_nl * Smn_w_inc * E1

        # Solve for Amn
        return np.linalg.lstsq(Q, f, rcond=None)[0]

    @staticmethod
    def _alpha_int(eta, m, n, ell, hm, ht):
        """Eqn (8) in Gonzalez et al (2016) ready for integration with respect to eta.

        The denominator in eqn (8) is not necessary because of the norm=True
        option in the pro_ang1 calls.
        """
        return pro_ang1(m, n, hm, eta, norm=True)[0] * pro_ang1(m, ell, ht, eta, norm=True)[0]
