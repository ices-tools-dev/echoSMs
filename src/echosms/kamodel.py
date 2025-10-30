"""A class that provides the Kirchhoff approximation scattering model."""

from math import log10
import numpy as np
from scipy.spatial.transform import Rotation as R
from .utils import wavenumber, wavelength, as_dict, boundary_type as bt
from .scattermodelbase import ScatterModelBase


class KAModel(ScatterModelBase):
    """Kirchhoff approximation (KA) scattering model.

    This class calculates acoustic scatter from arbitrary surfaces.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'Kirchhoff approximation'
        self.short_name = 'ka'
        self.analytical_type = 'approximate'
        self.boundary_types = [bt.pressure_release]
        self.shapes = ['closed surfaces']
        self.max_ka = 20  # [1]
        self.no_expand_parameters = ['mesh']

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_in(p, ['boundary_type'], self.boundary_types)
        super()._present_and_positive(p, ['medium_c', 'f'])

    def calculate_ts_single(self, medium_c, theta, phi, f, mesh,
                            boundary_type: bt, validate_parameters=True, **kwargs) -> float:
        """
        Calculate the scatter using the ka model for one set of parameters.

        Parameters
        ----------
        medium_c : float
            Sound speed in the fluid medium surrounding the target [m/s].
        theta : float
            Pitch angle to calculate the scattering as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].
        phi : float
            Roll angle to calculate the scattering as per the echoSMs
            [coordinate system](https://ices-tools-dev.github.io/echoSMs/
            conventions/#coordinate-systems) [°].
        f : float
            Frequency to calculate the scattering at [Hz].
        mesh : Any
            The triangular mesh that defines the scattering surface. This parameter must provide
            attributes with names of:

            - `triangles_center` (the position of the centre of each triangular face [m]),
            - `face_normals` (the outward-pointing unit normals for each triangular face),
            - `area_faces` (the area of each triangular face [m²]).

            A suitable library for creating and manipulating triangular meshes
            is [trimesh](https://trimesh.org). Trimesh will accept the usual nodes/facets
            definition of a mesh and calculate the above attributes automatically.
        boundary_type :
            The boundary type. Supported types are given in the `boundary_types` class variable.
        validate_parameters : bool
            Whether to validate the model parameters.

        Returns
        -------
        : float
            The target strength (re 1 m²) of the target [dB].

        Notes
        -----
        The class implements the code in Foote (1985).

        References
        ----------
        Foote, K. G. (1985). Rather-high-frequency sound scattering of swimbladdered fish.
        The Journal of the Acoustical Society of America, 78(2), 688–700.
        <https://doi.org/10.1121/1.392438>

        """
        if validate_parameters:
            self.validate_parameters(locals())

        if boundary_type not in self.boundary_types:
            raise ValueError(f'The {self.long_name} model does not support '
                             f'a model type of "{boundary_type}".')

        # This model keeps the organism fixed and varies the incident wave vector. So need
        # to convert the theta and phi echoSMs coordinate sytem Tait-Bryan angles
        # into an (x,y,z) vector.

        # Acoustic wave incident vector and its' norm
        rot = R.from_euler('ZYX', (0, theta-90, -phi), degrees=True)
        k_norm = rot.as_matrix() @ np.array([[0, 0, 1]]).T
        k = k_norm * wavenumber(medium_c, f)

        r = mesh.triangles_center  # position vector of each surface element
        dS = mesh.area_faces.reshape((-1, 1))  # [m^2]

        kn_nn = mesh.face_normals @ k_norm

        fbs = 1./wavelength(medium_c, f)\
            * np.sum(np.exp(2j*r @ k) * np.heaviside(kn_nn, 0.5) * kn_nn * dS)

        return 10*log10(abs(fbs)**2)  # ts
