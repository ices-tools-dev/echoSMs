"""A class that provides the prolate spheroidal modal series scattering model."""

import numpy as np
from scipy.integrate import quad
from .scattermodelbase import ScatterModelBase
from .utils import pro_rad1, pro_rad2, pro_ang1, wavenumber, Neumann


class PSMSModel(ScatterModelBase):
    """Prolate spheroidal modal series (PSMS) scattering model."""

    def __init__(self):
        super().__init__()
        self.long_name = 'prolate spheroidal modal series'
        self.short_name = 'psms'
        self.analytical_type = 'exact'
        self.boundary_types = ['fixed rigid', 'pressure release', 'fluid filled']
        self.shapes = ['prolate spheroid']
        self.max_ka = 10  # [1]

    def calculate_ts_single(self, medium_c, medium_rho, a, b, theta, f, boundary_type,
                            target_c=None, target_rho=None):
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
            Pitch angle to calculate the scattering at [°]. An angle of 0 is head on,
            90 is dorsal, and 180 is tail on.
        f : float
            Frequency to calculate the scattering at [Hz].
        boundary_type : str
            The model type. Supported model types are given in the `boundary_types` class variable.
        target_c : float, optional
            Sound speed in the fluid inside the target [m/s].
            Only required for `boundary_type` of ``fluid filled``.
        target_rho : float, optional
            Density of the fluid inside the target [kg/m³].
            Only required for `boundary_type` of ``fluid filled``.

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
            model,” Fish. Sci., 60, 261–265.
        """
        match boundary_type:
            case 'pressure release' | 'fluid filled':
                pass
            case 'fixed rigid':
                raise ValueError(f'Model type "{boundary_type}" has not yet been implemented '
                                 f'for the {self.long_name} model.')
            case _:
                raise ValueError(f'The {self.long_name} model does not support '
                                 f'a model type of "{boundary_type}".')

        if boundary_type == 'fluid filled':
            hc = target_c / medium_c
            rh = target_rho / medium_rho

        xiw = (1.0 - (b/a)**2)**(-.5)
        q = a/xiw  # semi-focal length

        kw = wavenumber(medium_c, f)
        hw = kw*q

        # Phi, the port/starboard angle is fixed for this code
        phi_inc = np.pi  # incident direction
        phi_sca = np.pi + phi_inc  # scattered direction

        theta_inc = np.deg2rad(theta)  # incident direction
        theta_sca = np.pi - theta_inc  # scattered direction

        # Approximate limits on the summations
        m_max = int(np.ceil(2*kw*b))
        n_max = int(m_max + np.ceil(hw/2))

        f_sc = 0.0
        for m in range(m_max+1):
            epsilon_m = Neumann(m)
            for n in range(m, n_max+1):
                Smn_inc, _ = pro_ang1(m, n, hw, np.cos(theta_inc))
                Smn_sca, _ = pro_ang1(m, n, hw, np.cos(theta_sca))
                match boundary_type:
                    case 'fluid filled':
                        r_type1A, dr_type1A = pro_rad1(m, n, hw, xiw)
                        r_type2A, dr_type2A = pro_rad2(m, n, hw, xiw)
                        r_type1B, dr_type1B = pro_rad1(m, n, hw/hc, xiw)

                        eeA = r_type1A - rh*r_type1B/dr_type1B*dr_type1A
                        eeB = eeA + 1j*(r_type2A - rh*r_type1B/dr_type1B*dr_type2A)
                        Amn = -eeA/eeB  # Furusawa (1988) Eq. 5 p 15
                    case 'pressure release':
                        r_type1, _ = pro_rad1(m, n, hw, xiw)
                        r_type2, _ = pro_rad2(m, n, hw, xiw)
                        Amn = -r_type1/(r_type1 + 1j*r_type2)
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
                n_mn = quad(PSMSModel.aswfa2, -1, 1, args=(m, n, hw), epsrel=1e-5)

                f_sc += epsilon_m / n_mn[0]\
                    * Smn_inc * Amn * Smn_sca * np.cos(m*(phi_sca - phi_inc))

        return 20*np.log10(-2j / kw * f_sc)

    @staticmethod
    def aswfa2(eta, m, n, h0):
        """Need eta argument to be first for use in quad()."""
        # Calculates the square of S_mn for the given values of eta.
        return pro_ang1(m, n, h0, eta)[0]**2
