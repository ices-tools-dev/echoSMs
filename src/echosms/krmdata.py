"""Classes to help store KRM model data."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .utils import boundary_type as bt


@dataclass
class KRMshape:
    """KRM shape and property class.

    Attributes
    ----------
    boundary : bt
        The shape boundary condition - either `pressure_release` or `fluid_filled`.
    x :
        The _x_-axis coordinates of the cross-sections [m]. Cross-sections may be supplied
        in any order, with all geometry arrays are sorted together by increasing x.
    w :
        Width of the shape [m].
    z_U :
        The upper surface coordinates relative to the fish reference axis [m].
    z_L :
        The lower surface coordinates relative to the fish reference axis [m].
    c :
        Sound speed in the shape [m/s].
    rho :
        Density of the shape material [kg/m³].

    """

    boundary: bt
    x: np.ndarray
    w: np.ndarray
    z_U: np.ndarray
    z_L: np.ndarray
    c: float
    rho: float

    def __post_init__(self):
        """Check geometry and store cross-sections in increasing x order.

        Raises
        ------
        ValueError
            If the cross-section arrays are invalid or x contains duplicate coordinates.
        """
        names = ['x', 'w', 'z_U', 'z_L']
        arrays = [np.asarray(getattr(self, name), dtype=float) for name in names]
        if any(a.ndim != 1 or a.size < 2 or not np.all(np.isfinite(a)) for a in arrays)\
                or any(a.shape != arrays[0].shape for a in arrays):
            raise ValueError('KRM geometry requires matching finite arrays of at least two sections.')
        x, w, z_U, z_L = arrays
        if np.any(w < 0) or np.any(z_U < z_L):
            raise ValueError('KRM widths and heights must be non-negative.')
        order = np.argsort(x)
        if np.any(np.diff(x[order]) == 0):
            raise ValueError('KRM x coordinates must be unique.')
        for name, a in zip(names, arrays):
            setattr(self, name, a[order])

    def volume(self) -> float:
        """Volume of the shape.

        Returns
        -------
        :
            The volume of the shape [m³].

        """
        height = self.z_U - self.z_L
        width = self.w
        # Integrate pi*width*height/4 with both dimensions linear between cross-sections.
        return np.sum(np.pi/24 * np.diff(self.x)
                      * (2*width[:-1]*height[:-1] + width[:-1]*height[1:]
                         + width[1:]*height[:-1] + 2*width[1:]*height[1:]))

    def length(self) -> float:
        """Length of the shape.

        Returns
        -------
        :
            The length of the shape [m].

        """
        return self.x[-1] - self.x[0]


@dataclass
class KRMorganism:
    """KRM body and inclusion shape(s).

    Attributes
    ----------
    name :
        A name for the organism.
    source :
        A link to or description of the source of the organism data.
    body :
        The shape that represents the organism's body.
    inclusions :
        The shapes that are internal to the organism (e.g., swimbladder, backbone, etc)
    aphiaid :
        The aphiaID of the organism
    length :
        The length of the organism (m)
    vernacular_name :
        A vernacular name of the organism

    """

    name: str
    source: str
    body: KRMshape
    inclusions: list[KRMshape]
    aphiaid: int = 1
    length: float = 0.0
    vernacular_name: str = ''

    def plot(self, block=True):
        """Plot of organism shape."""
        import matplotlib.pyplot as plt

        plt.plot(self.body.x*1e3, self.body.z_U*1e3, self.body.x*1e3, self.body.z_L*1e3, c='black')
        for i in [0, -1]:  # close the ends of the shape
            plt.plot([self.body.x[i]*1e3]*2, [self.body.z_U[i]*1e3, self.body.z_L[i]*1e3],
                     c='black')

        for s in self.inclusions:
            c = 'C0' if s.boundary == bt.fluid_filled else 'C1'
            plt.plot(s.x*1e3, s.z_U*1e3, s.x*1e3, s.z_L*1e3, c=c)
            for i in [0, -1]:  # close the ends of the shape
                plt.plot([s.x[i]*1e3]*2, [s.z_U[i]*1e3, s.z_L[i]*1e3], c=c)

        plt.gca().set_aspect('equal')
        plt.gca().xaxis.set_inverted(True)
        plt.title(self.name)
        plt.show(block=block)


class KRMdata:
    """Example datasets for the KRM model."""

    def __init__(self, file='KRM_shapes.toml') -> None:
        """Create the NOAA KRM shapes dataset.

        Parameters
        ----------
        file :
            The name of the TOML file containing the KRM shapes.

        Raises
        ------
        SyntaxError
            If the TOML file is invalid.
        """
        self.file = Path(__file__).parent/'resources'/file
        with Path.open(self.file, 'rb') as f:
            try:
                shapes = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise SyntaxError(f'Error while parsing file "{self.defs_filename.name}"') from e

        # Put the shapes into a dict of KRMorganism(). Use some default values for sound speed and
        # density
        self.krm_models = {}
        for s in shapes['shape']:
            # These KRM data have the head pointing in the -ve x direction,
            # opposite to the echoSMs coordinate convention, so fix the
            # x-coordinates here when ingesting the data. And set the posterior end
            # of the organism to have x=0

            body = KRMshape(bt.fluid_filled, -np.array(s['x_b']), np.array(s['w_b']),
                            np.array(s['z_bU']), np.array(s['z_bL']),
                            s['body_c'], s['body_rho'])
            swimbladder = KRMshape(bt.pressure_release, -np.array(s['x_sb']), np.array(s['w_sb']),
                                   np.array(s['z_sbU']), np.array(s['z_sbL']),
                                   s['swimbladder_c'], s['swimbladder_rho'])
            self.krm_models[s['name']] = KRMorganism(s['name'], s['source'],
                                                     body, [swimbladder],
                                                     s['aphiaid'], s['length'],
                                                     s['vernacular'])

    def names(self):
        """Available KRM model names.

        Returns
        -------
        :
            The KRM model names.
        """
        return [*self.krm_models]

    def as_dict(self) -> dict:
        """KRM model shapes as a dict.

        Returns
        -------
        :
            All the KRM model shapes. The dataset name is the dict key and the value is an instance
            of `KRMorganism`.

        """
        return self.krm_models

    def model(self, name: str) -> KRMorganism:
        """KRM model shape with requested name.

        Parameters
        ----------
        name :
            The name of a KRM model shape.

        Returns
        -------
        :
            An instance of `KRMorganism` or None if there is no model with `name`.

        """
        try:
            return self.krm_models[name]
        except KeyError:
            return None

    @staticmethod
    def ts(name: str) -> pd.DataFrame:
        """KRM model TS from model `name`.

        Parameters
        ----------
        name :
            The name of a KRM model shape.

        Returns
        -------
        :
            The TS (re 1 m²) for some default model parameters [dB] or None if no TS data
            are available.

        """
        # Sometimes there will be TS results for the model (available for testing of the
        # model), so load them in if present.
        tsfile = Path(__file__).parent/Path('resources')/Path('NOAA_KRM_ts_' + name + '.csv')

        if tsfile.exists():
            return pd.read_csv(tsfile)

        return None
