"""A class that provides the modal series solution scattering model."""

import numpy as np
from math import log10
# from mapply.mapply import mapply
# import swifter
from scipy.special import spherical_jn, spherical_yn
from .utils import h1, k
from .scattermodelbase import ScatterModelBase


class ESModel(ScatterModelBase):
    """Elastic sphere (ES) scattering model.

    This class calculates acoustic scatter from elastic spheres.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'elastic sphere'
        self.short_name = 'es'
        self.analytical_type = 'exact'
        self.boundary_types = ['elastic sphere']
        self.shapes = ['sphere']
        self.max_ka = 20  # [1]

    def calculate_ts_single(self, medium_c, medium_rho, diameter, theta, f,
                            target_longitudal_c, target_transverse_c, target_rho,
                            **kwargs) -> float:
        """
        Calculate the scatter from an elastic sphere for one set of parameters.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the sphere [m/s].
        medium_rho : float
            Density of the fluid medium surrounding the sphere [kg/m³].
        diameter : float
            Diameter of the sphere [m].
        theta : float
            Pitch angle(s) to calculate the scattering at [°]. An angle of 0 is head on,
            90 is dorsal, and 180 is tail on.
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
        k0 = k(medium_c, f)
        ka = k0*diameter

        return -1.0
