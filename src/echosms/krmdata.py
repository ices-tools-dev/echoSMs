"""Classes to help store KRM model data."""

import sys
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd
from dataclasses import dataclass
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class KRMshape():
    """KRM shape and property storage.

    Attributes
    ----------
    shape_type :
        The shape bounday condition - either `soft` or `fluid`.
    x :
        The _x_-axis coordinates [m].
    w :
        Width of the shape [m].
    z_U :
        Distance from the fish axis to the upper surface of the shape [m].
    z_L :
        Distance from the fish axis to the lower surface of the shape [m].
    c :
        Sound speed in the shape [m/s].
    rho :
        Density in the shape [kg/m³].
    """

    boundary: str  # 'soft' (aka swimbladder) or 'fluid' (aka body)
    x: np.ndarray
    w: np.ndarray
    z_U: np.ndarray
    z_L: np.ndarray
    c: float = None
    rho: float = None


@dataclass
class KRMfish():
    """KRM fish and swimbladder model shapes.

    Attributes
    ----------
    name :
        A name for the fish.
    source :
        A link to or description of the source of the fish data.
    shapes :
        The shapes that make up the fish.
    """

    name: str
    source: str
    shapes: List[KRMshape]


class KRMdata():
    """Provides example fish datasets for the KRM model."""

    def __init__(self):
        # Load in the NOAA KRM shapes data
        self.file = Path(__file__).parent/Path('resources')/Path('NOAA_KRM_shapes.toml')
        with open(self.file, 'rb') as f:
            try:
                shapes = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise SyntaxError(f'Error while parsing file "{self.defs_filename.name}"') from e

        # Put the shapes into a dict of KRMfish(). Use some default values for sound speed and
        # density
        self.krm_models = {}
        for s in shapes['shape']:
            body = KRMshape('fluid', np.array(s['x_b']), np.array(s['w_b']),
                            np.array(s['z_bU']), np.array(s['z_bL']), 1570, 1070)
            swimbladder = KRMshape('soft', np.array(s['x_sb']), np.array(s['w_sb']),
                                   np.array(s['z_sbU']), np.array(s['z_sbL']), 345, 1.24)
            self.krm_models[s['name']] = KRMfish(s['name'], s['source'], [body, swimbladder])

    def names(self):
        """Available KRM model names."""
        return [*self.krm_models]

    def as_dict(self) -> dict:
        """KRM model shapes as a dict.

        Returns
        -------
        :
            All the KRM model shapes. The dataset name is the dict key and the value is an instance
            of `KRMfish`.

        """
        return self.krm_models

    def model(self, name: str) -> KRMfish:
        """KRM model shape with requested name.

        Parameters
        ----------
        name :
            The name of a KRM model shape.

        Returns
        -------
        :
            An instance of `KRMfish` or None if there is no model with `name`.

        """
        try:
            return self.krm_models[name]
        except KeyError:
            return None

    @staticmethod
    def ts(name: str) -> np.ndarray:
        """KRM model ts with requested name.

        Parameters
        ----------
        name :
            The name of a KRM model shape.

        Returns
        -------
        :
            The TS (re 1 m²) for some default model parameters [dB] or None of no TS data exist.

        """
        # Sometimes there will be TS results for the model (available for testing of the
        # model), so load them in if present.
        tsfile = Path(__file__).parent/Path('resources')/Path('NOAA_KRM_ts_' + name + '.csv')

        if tsfile.exists():
            return pd.read_csv(tsfile)

        return None
