"""The distorted-wave Born approximation model."""

from .scattermodelbase import ScatterModelBase


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
        self.boundary_types = 'weakly scattering'
        self.shapes = ['any']
        self.max_ka = 20

    def calculate_ts_single(self, theta, phi, f, target_rho, target_c):
        """Distorted-wave Born approximation scattering model.

        Implements the distorted-wave Born approximation
        model for calculating the acoustic backscatter from weakly scattering bodies.

        Parameters
        ----------
        theta : float
            Incident wave pitch angle [°].

        phi : float
            Incident wave roll angle [°].

        f : float
            Frequency to run the model at [Hz]

        target_rho : iterable[float]
            Densities of each material. Must have at least the same number of entries as unique
            integers in `volume` [kg/m³].

        target_c : iterable[float]
            Sound speed of each material. Must have at least the same number of entries as unique
            integers in `volume` [m/s].

        Returns
        -------
        : float
            The target strength (re 1 m²) [dB] of the target.

        Notes
        -----
        This class implements the method presented in Chu et al. (1993).

        References
        ----------
        Chu, D., Foote, K. G., & Stanton, T. K. (1993). Further analysis of target strength
        measurements of Antarctic krill at 38 and 120 kHz: Comparison with deformed cylinder
        model and inference or orientation distribution. The Journal of the Acoustical Society
        of America, 93(5), 2985–2988. <https://doi.org/10.1121/1.405818>

        """
        return None
