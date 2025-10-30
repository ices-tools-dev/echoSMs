"""Classes to help store KRM model data."""

import sys
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd
from dataclasses import dataclass
from .utils import boundary_type as bt
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class KRMshape():
    """KRM shape and property class.

    Attributes
    ----------
    boundary : bt
        The shape bounday condition - either `pressure_release` or `fluid_filled`.
    x :
        The _x_-axis coordinates [m].
    w :
        Width of the shape [m].
    z_U :
        Distance from the axis to the upper surface of the shape [m].
    z_L :
        Distance from the axis to the lower surface of the shape [m].
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

    def volume(self) -> float:
        """Volume of the shape.

        Returns
        -------
        :
            The volume of the shape [m³].
        """
        thickness = np.diff(self.x)
        thickness = np.append(thickness, thickness[1])
        return np.sum(np.pi * (self.z_U - self.z_L) * self.w * thickness)

    def length(self) -> float:
        """Length of the shape.

        Returns
        -------
        :
            The length of the shape [m].
        """
        return self.x[-1] - self.x[0]


@dataclass
class KRMorganism():
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
    inclusions: List[KRMshape]
    aphiaid: int = 1
    length: float = 0.0
    vernacular_name: str = ''

    def plot(self):
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
        plt.show()


class KRMdata():
    """Example datasets for the KRM model."""

    def __init__(self):
        # Load in the NOAA KRM shapes data
        self.file = Path(__file__).parent/Path('resources')/Path('KRM_shapes.toml')
        with open(self.file, 'rb') as f:
            try:
                shapes = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise SyntaxError(f'Error while parsing file "{self.defs_filename.name}"') from e

        # Put the shapes into a dict of KRMorganism(). Use some default values for sound speed and
        # density
        self.krm_models = {}
        for s in shapes['shape']:
            # These KRM data have the head pointing in the -ve x direction,
            # opposite to the echoSMs coordinate convetion, so fix the
            # x-coordinates here when ingesting the data. And set the posterior end
            # of the organism to have x=0
            m = max(s['x_b'])
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
        """Available KRM model names."""
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
    def ts(name: str) -> np.ndarray:
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
