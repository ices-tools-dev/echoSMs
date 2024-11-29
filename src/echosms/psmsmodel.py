"""A class that provides the prolate spheroidal modal series scattering model."""

import numpy as np
from math import factorial
from .scattermodelbase import ScatterModelBase
from .utils import pro_rad1, pro_rad2, pro_ang1, wavenumber, Neumann, as_dict


class PSMSModel(ScatterModelBase):
    """Prolate spheroidal modal series (PSMS) scattering model.

    Note
    -------
    The fluid filled boundary type implementation is currently only accurate
    for weakly scattering interiors. Support for strongly scattering
    (e.g., gas-filled) will come later.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'prolate spheroidal modal series'
        self.short_name = 'psms'
        self.analytical_type = 'exact'
        self.boundary_types = ['fixed rigid', 'pressure release', 'fluid filled']
        self.shapes = ['prolate spheroid']
        self.max_ka = 10  # [1]

    def validate_parameters(self, params):
        """Validate the model parameters.
        
        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_in(p, ['boundary_type'], self.boundary_types)
        super()._present_and_positive(p, ['medium_c', 'medium_rho', 'a', 'b', 'f'])

        for bt in np.atleast_1d(p['boundary_type']):
            match bt:
                case 'fluid filled':
                    super()._present_and_positive(p, ['target_c', 'target_rho'])

    def calculate_ts_single(self, medium_c, medium_rho, a, b, theta, f, boundary_type,
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
        boundary_type : str
            The model type. Supported model types are given in the `boundary_types` class variable.
        target_c : float
            Sound speed in the fluid inside the target [m/s].
            Only required for `boundary_type` of ``fluid filled``.
        target_rho : float
            Density of the fluid inside the target [kg/m³].
            Only required for `boundary_type` of ``fluid filled``.
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

        xim = (1.0 - (b/a)**2)**(-.5)
        q = a/xim  # semi-focal length

        km = wavenumber(medium_c, f)
        hm = km*q

        if boundary_type == 'fluid filled':
            g = target_rho / medium_rho
            ht = wavenumber(target_c, f)*q

        # Phi, the port/starboard angle is fixed for this code
        phi_inc = np.pi  # incident direction
        phi_sca = np.pi + phi_inc  # scattered direction

        theta_inc = np.deg2rad(theta)  # incident direction
        theta_sca = np.pi - theta_inc  # scattered direction

        # Approximate limits on the summations
        m_max = int(np.ceil(2*km*b))
        n_max = int(m_max + np.ceil(hm/2))

        f_sca = 0.0
        for m in range(m_max+1):
            epsilon_m = Neumann(m)
            cos_term = np.cos(m*(phi_sca - phi_inc))
            for n in range(m, n_max+1):
                Smn_inc, _ = pro_ang1(m, n, hm, np.cos(theta_inc))
                Smn_sca, _ = pro_ang1(m, n, hm, np.cos(theta_sca))
                # The Meixner-Schäfke normalisation scheme for the angular function of the first
                # kind. Refer to eqn 21.7.11 in Abramowitz, M., and Stegun, I. A. (1964).
                # Handbook of Mathematical Functions with Formulas, Graphs, and Mathematical Tables
                # (Dover, New York), 10th ed.
                N_mn = 2/(2*n+1) * factorial(n+m) / factorial(n-m)

                R1m, dR1m = pro_rad1(m, n, hm, xim)
                R2m, dR2m = pro_rad2(m, n, hm, xim)

                match boundary_type:
                    case 'fluid filled':
                        # Note: we can implement the simpler equations if impedances are
                        # similar between the medium and the target. The gas-filled
                        # condition does not meet that, so we have two paths here. The simplified
                        # equations are quicker, so it is worth to do.
                        if (abs(1.0-target_c/medium_c) <= 0.01) and (abs(1.0-g) <= 0.01):
                            Amn = PSMSModel._fluidfilled_approx(m, n, hm, ht, xim, g)
                        else:
                            Amn = PSMSModel._fluidfilled_exact(m, n, hm, ht, xim, g, theta_inc)
                    case 'pressure release':
                        Amn = -R1m/(R1m + 1j*R2m)
                    case 'fixed rigid':
                        Amn = -dR1m/(dR1m + 1j*dR2m)

                f_sca += epsilon_m * (Smn_inc / N_mn) * Smn_sca * Amn * cos_term

        return 20*np.log10(np.abs(-2j / km * f_sca))

    @staticmethod
    def _fluidfilled_approx(m, n, hm, ht, xim, g):

        R1m, dR1m = pro_rad1(m, n, hm, xim)
        R2m, dR2m = pro_rad2(m, n, hm, xim)

        R1t, dR1t = pro_rad1(m, n, ht, xim)
        R3m = R1m + 1j*R2m
        dR3m = dR1m + 1j*dR2m

        E1 = R1m - g * R1t / dR1t * dR1m
        E3 = R3m - g * R1t / dR1t * dR3m
        return -E1/E3

    @staticmethod
    def _fluidfilled_exact(m, n, hm, ht, xim, g, theta_inc):
        """Calculate Amn for fluid filled prolate spheroids."""
        # This is conplicated!

        # Setup the system of simultaneous equations to solve for Amn.

        # Solve for Amn
        Amn = 1.0

        return Amn
