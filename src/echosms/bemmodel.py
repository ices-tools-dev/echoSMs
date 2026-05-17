"""A class that provides an implementation of the classical boundary element method for pressure release targets."""

from typing import Any
from .scattermodelbase import ScatterModelBase
from .utils import as_dict, boundary_type as bt

from numpy import pi, sqrt, exp, sin, cos, array, zeros, log10
from scipy.linalg import solve
from numpy import errstate, fill_diagonal
from scipy.spatial.distance import pdist, squareform

class BEMModel(ScatterModelBase):
    """Boundary element method (BEM) scattering model.
    
    This class calculates acoustic scatter arbitrary surfaces.
    """

    def __init__(self):
        super().__init__()
        self.long_name = 'Boundary Element Method'
        self.short_name = 'bem'
        self.analytical_type = 'numerical'
        self.boundary_types = [bt.pressure_release]
        self.shapes = ['closed surfaces']
        self.max_ka = 50
        self.no_expand_parameters = ['mesh']

    def validate_parameters(self, params):
        """Validate the model parameters.

        See [here][echosms.ScatterModelBase.validate_parameters] for calling details.
        """
        p = as_dict(params)
        super()._present_and_in()
        super()._present_and_positive()
    
    def calculate_ts_single(self, medium_c: float, theta: float, phi: float,
                            f: float, mesh: Any, boundary_type: bt,
                            validate_parameters: bool=True, **kwargs) -> float:
        """
        Calculate the scatter using the boundary element method for one set of parameters.

        Parameters
        ----------
        medium_c :
            Sound speed in the fluid medium surrounding the target [m/s].
        theta :
            Pitch angle to calculate the scattering as per the echoSMs
            [coordinate system](conventions.md#coordinate-systems) [°].
        phi :
            Roll angle to calculate the scattering as per the echoSMs
            [coordinate system](conventions.md#coordinate-systems) [°].
        f :
            Frequency to calculate the scattering at [Hz].
        mesh :
            The triangular mesh that defines the scattering surface. This parameter must provide
            attributes with names of:

            - `vertices` (coordinates of the mesh vertices)
            - `faces` (indices into `vertices` that define the triangular mesh surface)

            A suitable library for creating and manipulating triangular meshes
            is [trimesh](https://trimesh.org).
        boundary_type :
            The boundary type. Supported types are given in the `boundary_types` class variable.
        validate_parameters :
            Whether to validate the model parameters.        

        Returns
        -------
        :
            The target strength (re 1 m²) of the target [dB].

        Notes
        -----
        This models implements the classical BEM for pressure release targets
        using scipy.linalg.solve with k/4 diagonal regularization, kindly provided by
        Marek Marek Moszyński.
    
        References
        ----------

        """

        # Note: th, ph - incident wave direction angles in radians

        (f0, c0, th, ph) = (f, medium_c, -theta*pi/180, phi*pi/180 )
        k = 2*pi*f0/c0
        
        # waves directions
        Rz = array([[cos(ph),-sin(ph),0], [sin(ph),cos(ph),0], [0,0,1]])
        di = Rz @ [cos(th),    0, sin(th)]        # incident direction
        r1 = Rz @ [cos(th+pi), 0, sin(th+pi)]     # backscatter direction

        # target surface centers
        (v, e) = (mesh.vertices, mesh.faces )
        (n, m) = (len(v), len(e) )
        # TODO - use trimesh's triangles_center rather than calculate it here ourselves
        x = [sum([array(v[e[i][j]])/3 for j in range(3)]) for i in range(m)]

        # negative incident field on target surface
        npinc = [-exp(1j*k * xi@di) for xi in x]

        # Helmholtz single layer boundary operator        
        
        # S = zeros((m,m),dtype=complex);
        # for i in range(m):
        #     for j in range(i+1):
        #         r = sqrt(sum((x[i]-x[j])**2))
        #         S[i][j] = S[j][i] = exp(1j*k*r)/(4*pi*r) if r!=0 else k/4 + 1j*k/(4*pi)
        # # surface solution
        # u = solve(S, npinc)
        
        r = squareform(pdist(x))
        with errstate(divide='ignore', invalid='ignore'):
            S = exp(1j*k*r)/(4*pi*r)
        fill_diagonal(S, k/4 + 1j*k/(4*pi))
        u = solve(S, npinc, assume_a='sym')
        
        # far field solution at |r1| = 1
        S = [exp(-1j*k * xi@r1)/(4*pi) for xi in x]
        psc = S @ u;
        return 20*log10(abs(psc))
