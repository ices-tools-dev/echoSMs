"""The phase-tracking distorted-wave Born approximation model."""

import numpy as np
from scipy import ndimage
from scipy.spatial.transform import Rotation as R
from .scattermodelbase import ScatterModelBase
from .utils import as_dict, boundary_type as bt


class PTDWBAModel(ScatterModelBase):
    """Phase-tracking distorted-wave Born approximation scattering model."""

    def __init__(self):
        super().__init__()
        self.long_name = 'phase-tracking distorted-wave Born approximation'
        self.short_name = 'pt-dwba'
        self.analytical_type = 'approximate'
        self.boundary_types = [bt.fluid_filled]
        self.shapes = ['unrestricted voxel-based']
        self.max_ka = 20
        self.no_expand_parameters = ['volume', 'voxel_size', 'rho', 'c']

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)

    def calculate_ts_single(self, volume, theta, phi, f, voxel_size, rho, c,
                            validate_parameters=True, **kwargs):
        """Phase-tracking distorted-wave Born approximation scattering model.

        Implements the phase-tracking distorted-wave Born approximation
        model for calculating the acoustic backscatter from weakly scattering bodies.

        Parameters
        ----------
        volume : Numpy ndarray[int]
            The object to be modelled as a 3D volume of voxels. Array contents should be 0
            for the surrounding medium, then increasing by 1 for each additional material
            type (i.e., 1, 2, 3, etc). `volume` should be arranged as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems), where

            - axis 0 (rows) is the _x_-axis
            - axis 1 (columns) is the _y_-axis
            - axis 2: (slices) is the _z_-axis

            Increasing axes indices correspond to increasing _x_, _y_, and _z_ values.

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

        voxel_size : iterable[float]
            The size of the voxels in `volume` [m], ordered (_x_, _y_, _z_).
            This code assumes that the voxels are cubes so _y_ and _z_ are currently irrelevant.

        rho : iterable[float]
            Densities of each material. Must have at least the same number of entries as unique
            integers in `volume` [kg/m³].

        c : iterable[float]
            Sound speed of each material. Must have at least the same number of entries as unique
            integers in `volume` [m/s].
        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) [dB] of the target.

        Notes
        -----
        This class implements the method presented in Jones et. al. (2009). The code is
        based closely on the Matlab code in Jones (2006).

        References
        ----------
        Jones, B. A. (2006). Acoustic scattering of broadband echolocation signals
        from prey of Blainville's beaked whales: Modeling and analysis. Master of Science,
        Massachusetts Institute of Technology. <https://doi.org/10.1575/1912/1283>

        Jones, B. A., Lavery, A. C., & Stanton, T. K. (2009). Use of the distorted
        wave Born approximation to predict scattering by inhomogeneous objects:
        Application to squid. The Journal of the Acoustical Society of America,
        125(1), 73-88. <https://doi.org/10.1121/1.3021298>
        """
        if validate_parameters:
            self.validate_parameters(locals())

        # Make sure things are numpy arrays
        rho = np.atleast_1d(rho)
        c = np.atleast_1d(c)
        voxel_size = np.array(voxel_size)

        # volume of the voxels [m^3]
        dv = voxel_size.prod()

        # input parameter checks
        if not len(volume.shape) == 3:
            raise TypeError('The volume input variable must be 3-dimensional.')

        if not voxel_size.shape[0] == 3:
            raise TypeError('The voxel_size input variable must contain 3 items.')

        if not np.any(voxel_size > 0):
            raise ValueError('All voxel_size values must be positive.')

        if f < 0.0:
            raise ValueError('The f input variable must contain only positive values.')

        if (theta < -0.0) or (theta > 180.0):
            raise ValueError('The theta (pitch) angle must be between -180.0 and +180.0')

        if (phi < -180.0) or (phi > 180.0):
            raise ValueError('The phi (roll) angle must be between -180.0 and +180.0')

        if volume.min() != 0:
            raise ValueError('The volume input variable must contain zeros.')

        categories = np.unique(volume)
        if not len(categories == (volume.max() + 1)):
            raise ValueError('The integers in volume must include all values in the series '
                             '(0, 1, 2, ..., n), where n is the largest integer in volume.')

        if not len(rho) >= len(categories):
            raise ValueError('The target_rho variable must contain at least as many values as '
                             'unique integers in the volume variable.')

        if not len(c) >= len(categories):
            raise ValueError('The target_c variable must contain at least as many values '
                             'as unique integers in the volume variable.')

        # density and sound speed ratios for all object materials
        g = rho[1:] / rho[0]
        h = c[1:] / c[0]

        # Do the pitch and roll rotations

        # Convert echoSMs rotation angles (which are intrinsic) into extrinsic as
        # that is what ndimage.rotate() below uses.
        if phi == 0.0:  # short circuit the coordinate transformation if we can
            pitch = theta-90
            roll = 0.0
        else:
            rot = R.from_euler('ZYX', (0, theta-90, -phi), degrees=True)
            # for backscatter we don't care about yaw
            _, pitch, roll = rot.as_euler('zyz', degrees=True)

        v = ndimage.rotate(volume, pitch, axes=(0, 2), order=0)
        v = ndimage.rotate(v, roll, axes=(1, 2), order=0)

        categories = np.unique(v)  # or just take the max?

        # wavenumbers in the various media
        k = 2.0*np.pi * f / c

        # DWBA coefficients
        # amplitudes in media 1,2,...,n
        Cb = 1.0/(g * h**2) + 1.0/g - 2.0  # gamma_kappa - gamma_rho
        Ca = k[0]**2 * Cb / (4.0*np.pi)  # summation coefficient

        # Differential phase for each voxel.
        dph = np.zeros(v.shape)
        masks = []
        for i, category in enumerate(categories):
            masks.append(np.isin(v, category))
            dph[masks[i]] = k[i] * voxel_size[0]
        masks.pop(0)  # don't need to keep the category[0] mask

        # cumulative summation of phase along the z-direction
        phase = dph.cumsum(axis=2) - dph/2.0
        dA = np.zeros(phase.shape, dtype=np.complex128)

        # differential phases for each voxel
        for i, m in enumerate(masks):
            dA[m] = Ca[i] * np.exp(2.0*1j*phase[m]) * dv

        # Convert to TS
        return 20.0 * np.log10(np.abs(dA.sum()))
