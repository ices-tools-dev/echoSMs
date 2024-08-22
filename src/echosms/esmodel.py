"""A class that provides the elastic scattering model."""

import numpy as np
from math import log10, sin, atan
from cmath import exp
from scipy.special import spherical_jn, spherical_yn
from .utils import k, spherical_jnpp
from .scattermodelbase import ScatterModelBase


class ESModel(ScatterModelBase):
    """Elastic sphere (ES) scattering model.

    This class calculates acoustic backscatter from elastic spheres.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'elastic sphere'
        self.short_name = 'es'
        self.analytical_type = 'exact'
        self.boundary_types = ['elastic sphere']
        self.shapes = ['sphere']
        self.max_ka = 20  # [1]

    def calculate_ts_single(self, medium_c, medium_rho, a, f,
                            target_longitudal_c, target_transverse_c, target_rho,
                            **kwargs) -> float:
        """
        Calculate the backscatter from an elastic sphere for one set of parameters.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the sphere [m/s].
        medium_rho : float
            Density of the fluid medium surrounding the sphere [kg/m³].
        a : float
            Radius of the sphere [m].
        f : float
            Frequencies to calculate the scattering at [Hz].
        target_longitudal_c : float
            Longitudal sound speed in the material inside the sphere [m/s].
        target_transverse_c : float
            Transverse sound speed in the material inside the sphere [m/s].
        target_rho : float
            Density of the material inside the sphere [kg/m³].

        Returns
        -------
        : float
            The target strength (re 1 m²) of the sphere [dB].

        Notes
        -----
        The class implements the code in [1].

        References
        ----------
        MacLennan, D. N. (1981). The Theory of Solid Spheres as Sonar Calibration Targets
        Scottish Fisheries Research Report Number 22. Department of Agriculture and Fisheries
        for Scotland.
        """
        q = k(medium_c, f)*a
        q1 = q*medium_c/target_longitudal_c
        q2 = q*medium_c/target_transverse_c
        alpha = 2. * (target_rho/medium_rho) * (target_transverse_c/medium_c)**2
        beta = (target_rho/medium_rho) * (target_longitudal_c/medium_c)**2 - alpha

        n = range(20)

        # Use n instead of l (ell) because l looks like 1.
        def S(n):
            A2 = (n**2 + n-2) * spherical_jn(n, q2) + q2**2 * spherical_jnpp(n, q2)
            A1 = 2*n*(n+1) * (q1*spherical_jn(n, q1, True) - spherical_jn(n, q1))
            B2 = A2*q1**2 * (beta*spherical_jn(n, q1) - alpha*spherical_jnpp(n, q1))\
                - A1*alpha * (spherical_jn(n, q2) - q2*spherical_jn(n, q2, True))
            B1 = q * (A2*q1*spherical_jn(n, q1, True) - A1*spherical_jn(n, q2))
            eta_n = atan(-(B2*spherical_jn(n, q, True) - B1*spherical_jn(n, q))
                         / (B2*spherical_yn(n, q, True) - B1*spherical_yn(n, q)))

            return (-1)**n * (2*n+1) * sin(eta_n) * exp(1j*eta_n)

        f_inf = -2.0/q * np.sum(list(map(S, n)))

        return 10*log10(a**2 * abs(f_inf)**2 / 4.0)
