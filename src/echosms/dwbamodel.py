"""The distorted-wave Born approximation model."""

from .scattermodelbase import ScatterModelBase
from .utils import wavenumber, as_dict, boundary_type as bt
from math import log10, cos, acos, pi, isclose, radians
from cmath import exp
from scipy.spatial.transform import Rotation as R
import numpy as np
from scipy.special import j1
import warnings


class DWBAModel(ScatterModelBase):
    """Distorted-wave Born approximation (DWBA) scattering models.

    This class calculates acoustic scatter from piecewise cylindical shapes with weakly
    scattering material contrasts. It can also add a stochastic component to provide the
    stochastic DWBA (SDWBA) model.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'distorted-wave Born approximation'
        self.short_name = 'dwba'
        self.analytical_type = 'approximate'
        self.boundary_types = [bt.fluid_filled]
        self.shapes = ['piecewise cylindical']
        self.max_ka = 20
        # The distorted wave Born approximation is increasingly inaccurate outside these limits:
        self.g_range = [0.95, 1.05]
        self.h_range = [0.95, 1.05]
        self.no_expand_parameters = ['a', 'rv_pos', 'rv_tan']
        self.rng = np.random.default_rng()  # for SDWBA

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_positive(p, ['medium_rho', 'medium_c', 'target_rho', 'target_c', 'f'])

        g = p['target_rho'] / p['medium_rho']
        h = p['target_c'] / p['medium_c']

        if (np.any(g < self.g_range[0])) or np.any((g > self.g_range[1])):
            warnings.warn('Ratio of target and medium densities (g) is outside the DWBA limits.')

        if (np.any(h < self.h_range[0])) or np.any((h > self.h_range[1])):
            warnings.warn('Ratio of target and medium sound speeds (h) are '
                          'outside the DWBA limits.')

        if not np.all([isclose(1.0, np.linalg.norm(v)) for v in p['rv_tan']]):
            raise ValueError('All vectors in rv_tan must be of unit length.')

    def calculate_ts_single(self, medium_c, medium_rho, theta, phi, f, target_c, target_rho,
                            a, rv_pos, rv_tan, phase_sd=0, num_runs=1, validate_parameters=True,
                            **kwargs) -> float:
        """Distorted-wave Born approximation scattering model.

        Implements the distorted-wave Born approximation and stochastic DWBA
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
        phi : float
            Roll angle to calculate the scattering as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].
        f : float
            Frequency to run the model at [Hz]
        target_c : float
            Sound speed in the fluid inside the target [m/s].
        target_rho : float
            Density of the fluid inside the target [kg/m³].
        a : iterable
            The radii of the discs that define the target shape [m].
        rv_pos : iterable[np.ndarray]
            An interable of vectors of the 3D positions of the centre of each disc that
            defines the target shape. Each vector should have three values corresponding to
            the _x_, _y_, and _z_ coordinates [m] of the disc centre.
        rv_tan : iterable[np.ndarray]
            An interable of unit vectors of the tangent to the target body axis at
            the points given in `rv_pos`. Each vector should have three values corresponding to
            the _x_, _y_, and _z_ components of the tangent vector.
        phase_sd : float
            If non-zero, this model becomes the SDWBA (stochastic DWBA). A random phase is
            applied to each term in the DWBA integral, obtained from a Gaussian distribution
            centered on 0 with standard deviation of `phase_sd` [°].
        num_runs : int
            The number of times to run the SDWBA model. The mean TS (calculated in the
            linear domain) is returned. Intended to be used in conjunction with `phase_sd`.
        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) [dB] of the target.

        Notes
        -----
        This class implements the method presented in Eqn (5) of Stanton et al. (1998). This
        caters to objects that are discretised into a set of adjacent discs with potentially
        offset centres.

        The DWBA model density and sound speed values are often specified as ratios of the medium
        and target values (g & h). However, to maintain compatibility with other echoSMs models
        this implementation requires actual densities and sound speeds.

        The SDWBA component is as per Demer & Conti (2003).

        References
        ----------
        Demer, D. A., & Conti, S. G. (2003). Reconciling theoretical versus empirical target
        strengths of krill: Effects of phase variability on the distorted-wave Born approximation.
        ICES Journal of Marine Science, 60, 429-434.
        <https://doi.org/10.1016/S1054-3139(03)00002-X>

        Stanton, T. K., Chu, D., & Wiebe, P. H. (1998). Sound scattering by several zooplankton
        groups. II. Scattering models. The Journal of the Acoustical Society of America, 103(1),
        236-253. <https://doi.org/10.1121/1.421110>
        """
        if validate_parameters:
            self.validate_parameters(locals())

        do_sdwba = False if phase_sd == 0.0 else True

        # The structure of this code follows closely the formulae in Stanton et al (1998). Where
        # relevant, the equation numbers from that paper are given.

        k1 = wavenumber(medium_c, f)
        k2 = wavenumber(target_c, f)
        kappa_1 = 1.0 / (medium_rho * medium_c**2)  # Eqn (4) for medium
        kappa_2 = 1.0 / (target_rho * target_c**2)  # Eqn (4) for target
        gamma_k = (kappa_2 - kappa_1) / kappa_1  # Eqn (2)
        gamma_rho = (target_rho - medium_rho) / target_rho  # Eqn (3)
        # Note: the (gamma_k - gamma_rho) term in Eqn (5) can be simplified using g & h to:
        # 1/gh^2 + 1/g - 2.

        # Calculate the distance between each disc using the disc position vectors. The Euclidean
        # distance is the L2 norm so use np.norm(). Could also use
        # scipy.spatial.distance.euclidean(), but that is apparently a lot slower.
        dist = np.array([np.linalg.norm(r1-r0) for r0, r1 in zip(rv_pos[0:-1], rv_pos[1:])])  # [m]

        # Thickness of each disc based on the distance between discs. The first and last
        # discs are treated differently.
        d_rv_pos = np.hstack((dist[0], dist[0:-1]/2 + dist[1:]/2, dist[-1]))  # [m]

        # Calculate direction of incident wave given theta and phi. The echoSMs convention
        # has the target rotating and the incident vector always being (0,0,1), but for the DWBA
        # we keep the body stationary and change the incident vector.
        rot = R.from_euler('ZYX', (0, theta-90, -phi), degrees=True)
        k_hat_i = rot.apply([0, 0, 1])  # needs to be a unit vector
        k_i2 = k_hat_i * k2  # incident vector with magnitude equal to wavenumber inside the target

        # This code is a little complex because it does both the DWBA and SDWBA
        phase_factors = np.ones(len(a))  # for DWBA
        runs = []

        for run in range(int(num_runs)):  # is only ever 1 run for the DWBA
            if do_sdwba:
                phase_factors = np.exp(1j*self.rng.normal(scale=radians(phase_sd), size=len(a)))

            integral = 0.0
            for a_, r_pos, d_r_pos, r_tan, p in zip(a, rv_pos, d_rv_pos, rv_tan, phase_factors):
                # The round() is here because sometimes the dot product gets values slightly outside
                # the [-1, 1] range (due to floating point inaccuracies) and cos will complain.
                cbeta_tilt = cos(pi/2 - acos(round(k_hat_i @ r_tan, 8)))

                # This is the integral part of Eqn (5) with addition of
                # Eqn (4) from Demer & Conti (2003) for the SDWBA part
                integral += (gamma_k-gamma_rho) * exp(2j*(k_i2@r_pos))\
                    * a_*j1(2*k2*a_*cbeta_tilt) / cbeta_tilt * abs(d_r_pos) * p
            runs.append(integral)

        return 20*log10(np.mean(abs(k1/4.0*np.array(runs))))
