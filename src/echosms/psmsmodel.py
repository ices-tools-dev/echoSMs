"""A class that provides the prolate spheroidal modal series scattering model."""

import numpy as np
from math import factorial
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
        if boundary_type not in self.boundary_types:
            raise ValueError(f'The {self.long_name} model does not support '
                             f'a model type of "{boundary_type}".')

        xiw = (1.0 - (b/a)**2)**(-.5)
        q = a/xiw  # semi-focal length

        kw = wavenumber(medium_c, f)
        hw = kw*q

        if boundary_type == 'fluid filled':
            g = target_rho / medium_rho
            ht = wavenumber(target_c, f)*q

        # Phi, the port/starboard angle is fixed for this code
        phi_inc = np.pi  # incident direction
        phi_sca = np.pi + phi_inc  # scattered direction

        theta_inc = np.deg2rad(theta)  # incident direction
        theta_sca = np.pi - theta_inc  # scattered direction

        # Approximate limits on the summations
        m_max = int(np.ceil(2*kw*b))
        n_max = int(m_max + np.ceil(hw/2))

        f_sca = 0.0
        for m in range(m_max+1):
            epsilon_m = Neumann(m)
            for n in range(m, n_max+1):
                Smn_inc, _ = pro_ang1(m, n, hw, np.cos(theta_inc))
                Smn_sca, _ = pro_ang1(m, n, hw, np.cos(theta_sca))
                # The Meixner-Schäfke normalisation scheme for the angular function of the first
                # kind. Refer to eqn 21.7.11 in Abramowitz, M., and Stegun, I. A. (1964).
                # Handbook of Mathematical Functions with Formulas, Graphs, and Mathematical Tables
                # (Dover, New York), 10th ed.
                N_mn = 2/(2*n+1) * factorial(n+m) / factorial(n-m)
                # since N_mn and the angular functions can be very large for large m,
                # structure things to reduce roundoff errors.
                ss = (Smn_inc / N_mn) * Smn_sca

                match boundary_type:
                    case 'fluid filled':
                        # Note: we can implement the simplier equations if hw is similar to ht,
                        # but that only applies to weakly scattering conditions. The gas-filled
                        # condition does not meet that, so we have two paths here. The simplified
                        # equations are quicker, so it is worth to do.
                        R1w, dR1w = pro_rad1(m, n, hw, xiw)
                        R1t, dR1t = pro_rad1(m, n, ht, xiw)
                        R2w, dR2w = pro_rad2(m, n, hw, xiw)

                        R3w = R1w + 1j*R2w
                        dR3w = dR1w + 1j*dR2w
                        if abs((hw - ht)/ht) <= 0.1:  # weakly scattering simplification
                            E1 = R1w - g * R1t / dR1t * dR1w
                            E3 = R3w - g * R1t / dR1t * dR3w
                            Amn = -E1/E3
                        else:
                            Amn = PSMSModel._fluidfilled(m, n, hw, ht, xiw, theta_inc)
                    case 'pressure release':
                        R1w, _ = pro_rad1(m, n, hw, xiw)
                        R2w, _ = pro_rad2(m, n, hw, xiw)
                        Amn = -R1w/(R1w + 1j*R2w)
                    case 'fixed rigid':
                        _, dR1w = pro_rad1(m, n, hw, xiw)
                        _, dR2w = pro_rad2(m, n, hw, xiw)
                        Amn = -dR1w/(dR1w + 1j*dR2w)

                f_sca += epsilon_m * ss * Amn * np.cos(m*(phi_sca - phi_inc))

        return 20*np.log10(np.abs(-2j / kw * f_sca))

    @staticmethod
    def _fluidfilled(m, n, hw, ht, xiw, theta_inc):
        """Calculate Amn for fluid filled prolate spheroids."""
        # This is conplicated!

        # Setup the system of simultaneous equations to solve for Amn.

        # Solve for Amn
        Amn = 1.0

        return Amn
