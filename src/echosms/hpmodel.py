"""A class that provides a high-pass fluid sphere scattering model."""

from math import log10, sin, atan, fsum
from cmath import exp
from warnings import warn
from scipy.special import spherical_jn, spherical_yn
from .utils import wavenumber, spherical_jnpp, as_dict
from .scattermodelbase import ScatterModelBase


class HPModel(ScatterModelBase):
    """High-pass fluid sphere (HP) scattering model.

    This class calculates backscatter from elastic shelled spheres.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'elastic sphere'
        self.short_name = 'hp'
        self.analytical_type = 'approximate'
        self.boundary_types = ['elastic shelled sphere']
        self.shapes = ['sphere']
        self.max_ka = 20  # [1]

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_in(p, ['boundary_type'], self.boundary_types)
        super()._present_and_positive(p, ['medium_rho', 'medium_c', 'a', 'f',
                                          'target_longitudinal_c',
                                          'target_transverse_c', 'target_rho'])

    def calculate_ts_single(self, medium_c, medium_rho, a, f,
                            target_longitudinal_c, target_transverse_c, target_rho,
                            validate_parameters=True,
                            **kwargs) -> float:
        """
        Calculate the backscatter from an elastic shelled sphere for one set of parameters.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the sphere [m/s].
        medium_rho : float
            Density of the fluid medium surrounding the sphere [kg/m³].
        a : float
            Radius of the sphere [m].
        f : float
            Frequency to calculate the scattering at [Hz].
        target_longitudinal_c : float
            Longitudinal sound speed in the material inside the sphere [m/s].
        target_transverse_c : float
            Transverse sound speed in the material inside the sphere [m/s].
        target_rho : float
            Density of the material inside the sphere [kg/m³].
        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) of the sphere [dB].

        Notes
        -----
        The class implements the high-pass fluid sphere model in Lavery et al. (2007)
        and Stanton (1989)

        References
        ----------
        Lavery, A. C., Wiebe, P. H., Stanton, T. K., Lawson, G. L., Benfield, M. C., &
        Copley, N. (2007). Determining dominant scatterers of sound in mixed zooplankton
        populations. The Journal of the Acoustical Society of America, 122(6), 3304–3326.
        <https://doi.org/10.1121/1.2793613>
        
        Stanton, T. K. (1989). Simple approximate formulas for backscattering of sound
        by spherical and elongated objects. The Journal of the Acoustical Society of
        America, 86(4), 1499–1510.
        <https://doi.org/10.1121/1.398711>
        """
        if validate_parameters:
            p = {'medium_c': medium_c, 'medium_rho': medium_rho, 'a': a, 'f': f,
                 'target_longitudinal_c': target_longitudinal_c,
                 'target_transverse_c': target_transverse_c,
                 'target_rho': target_rho}
            self.validate_parameters(p)

        q = wavenumber(medium_c, f)*a
        q1 = q*medium_c/target_longitudinal_c
        q2 = q*medium_c/target_transverse_c
        alpha = 2. * (target_rho/medium_rho) * (target_transverse_c/medium_c)**2
        beta = (target_rho/medium_rho) * (target_longitudinal_c/medium_c)**2 - alpha

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

        # Estimate the number of terms to use in the summation
        n_max = round(q+10)
        tol = 1e-10  # somewhat arbitrary
        while abs(S(n_max)) > tol:
            n_max += 10

        if n_max > 200:
            warn('TS results may be inaccurate because the modal series required a large '
                 f'number ({n_max}) of terms to converge.')

        n = range(n_max)

        f_inf = -2.0/q * sum(map(S, n))

        return 10*log10(a**2 * abs(f_inf)**2 / 4.0)
