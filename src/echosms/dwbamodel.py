"""The distorted-wave Born approximation model."""

from .scattermodelbase import ScatterModelBase
from .utils import as_dict, wavenumber
from math import pi, log10
import warnings


class DWBAModel(ScatterModelBase):
    """Distorted-wave Born approximation scattering model.

    Note
    ----
    The DWBA model is not yet functional.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'distorted-wave Born approximation'
        self.short_name = 'dwba'
        self.analytical_type = 'approximate'
        self.boundary_types = ['weakly scattering']
        self.shapes = ['any']
        self.max_ka = 20
        self.g_range = [0.95, 1.05]
        self.h_range = [0.95, 1.05]

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_positive(p, ['medium_rho', 'medium_c', 'target_rho', 'target_c', 'f'])
        g = abs(p['target_rho'] / p['medium_rho'])
        h = abs(p['target_c'] / p['medium_c'])

        if (g < self.g_range[0]) or (g > self.g_range[1]):
            raise warnings.warn('Ratio of medium and target densities are '
                                'outside the DWBA limits.')

        if (h < self.h_range[0]) or (h > self.h_range[1]):
            raise warnings.warn('Ratio of medium and target sound speeds are '
                                'outside the DWBA limits.')

    def calculate_ts_single(self, medium_c, medium_rho, theta, phi, f, target_c, target_rho,
                            validate_parameters=True):
        """Distorted-wave Born approximation scattering model.

        Implements the distorted-wave Born approximation
        model for calculating the acoustic backscatter from weakly scattering bodies.

        Parameters
        ----------
        medium_c : float
           Sound speed in the fluid medium surrounding the target [m/s].
        medium_rho : float
           Density of the fluid medium surrounding the target [kg/m³].
        theta : float
            Pitch angle to calculate the scattering as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].
        f : float
            Frequency to run the model at [Hz]
        target_c : float
            Sound speed in the fluid inside the target [m/s].
        target_rho : float
            Density of the fluid inside the target [kg/m³].
        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) [dB] of the target.

        Notes
        -----
        This class implements the method presented in Stanton et al. (1998).

        The DWBA model density and sound speed values are often specified as ratios of the medium
        and target values (g & h). However, the echoSMs implementation requires actual densities
        and sound speeds to maintain compatibility with other echoSMs model input parameters.

        References
        ----------
        Stanton, T. K., Chu, D., & Wiebe, P. H. (1998). Sound scattering by several zooplankton
        groups. II. Scattering models. The Journal of the Acoustical Society of America, 103(1),
        236–253. <https://doi.org/10.1121/1.421110>
        """
        if validate_parameters:
            p = {'medium_rho': medium_rho, 'medium_c': medium_c, 'theta': theta, 'f': f,
                 'target_rho': f, 'target_c': target_c}
            self.validate_parameters(p)

        k = wavenumber(medium_c, f)
        kappa_1 = 1.0 / (medium_rho * medium_c**2)
        kappa_2 = 1.0 / (target_rho * target_c**2)
        gamma_k = (kappa_2 - kappa_1) / kappa_1
        gamma_rho = (target_rho - medium_rho) / target_rho

        f_bs = k/4.0 * 1.0

        return 10*log10(abs(f_bs)**2)
