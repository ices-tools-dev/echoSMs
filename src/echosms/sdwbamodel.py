"""The stochastic distorted-wave Born approximation model."""

from .scattermodelbase import ScatterModelBase


class SDWBAModel(ScatterModelBase):
    """Stochastic distorted-wave Born approximation scattering model.

    Note
    ----
    The SDWBA model is not yet functional.
    """

    def __init__(self):
        super().__init__()
        self.long_name = "stochastic distorted-wave Born approximation"
        self.short_name = "sdwba"
        self.analytical_type = "approximate"
        self.boundary_types = "weakly scattering"
        self.shapes = ["any"]
        self.max_ka = 20

    def calculate_ts_single(self, theta, phi, f, target_rho, target_c):
        """Stochastic distorted-wave Born approximation scattering model.

        Implements the stochastic distorted-wave Born approximation
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
        This class implements the method presented in Demer & Conti (2003), Demer & Conti (2004),
        and Conti & Demer (2006).

        References
        ----------
        Demer, D. A., & Conti, S. G. (2003). Reconciling theoretical versus empirical target
        strengths of krill: Effects of phase variability on the distorted-wave Born approximation.
        ICES Journal of Marine Science, 60, 429-434.
        <https://doi.org/10.1016/S1054-3139(03)00002-X>

        Demer, D. A., & Conti, S. G. (2004). Reconciling theoretical versus empirical
        target strengths of krill: Effects of phase variability on the distorted-wave Born
        approximation. ICES Journal of Marine Science, 61(1), 157-158.
        <https://doi.org/10.1016/j.icesjms.2003.12.003>

        Conti, S. G., & Demer, D. A. (2006). Improved parameterization of the SDWBA for estimating
        krill target strength. ICES Journal of Marine Science, 63(5), 928-935.
        <https://doi.org/10.1016/j.icesjms.2006.02.007>
        """
        return None