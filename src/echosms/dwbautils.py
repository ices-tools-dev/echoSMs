"""Miscellaneous functions for the DWBA models."""
import numpy as np
from pathlib import Path
import sys
from dataclasses import dataclass
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def create_dwba_spheroid(major_radius: float, minor_radius: float, spacing: float = 0.0001):
    """Create shape description variables for the DWBA model for spheres and prolate spheroids.

    The shape descriptions are essentially a set of discs and their orientation.

    Notes
    -----
    Currently only supports prolate spheroids and spheres (set `major_radius` and `minor_radius`
    to the same value to get a sphere).

    Parameters
    ----------
    major_radius :
        The major radius [m] of the spheroid.
    minor_radius :
        The minor radius [m] of the spheroid.
    spacing :
        The spacing [m] between successive discs.

    Returns
    -------
    rv_pos : iterable[np.ndarray]
        An interable of vectors of the 3D positions of the centre of each disc that
        defines the spheroid. Each vector has three values corresponding to
        the _x_, _y_, and _z_ coordinates [m] of the disc centre.
    rv_tan : iterable[np.ndarray]
        An interable of unit vectors of the tangent to the target body axis at
        the points given in `rv_pos`. Each vector has three values corresponding to
        the _x_, _y_, and _z_ components of the tangent vector.
    a : iterable
        The radii [m] of the discs that define the spheroid.
    """
    v = np.linspace(0, np.pi, int(round(2*major_radius/spacing)))
    a = minor_radius*np.sin(v)  # radius at points along the spheroid
    x = major_radius-major_radius*np.cos(v)  # shift so that origin is at one end

    # List of disc position vectors
    rv_pos = [np.array([i, 0, 0]) for i in x]

    # List of tangent vectors to sphere axis (all the same for spheroids)
    rv_tan = [np.array([1, 0, 0])] * len(x)

    return rv_pos, rv_tan, a


def create_dwba_cylinder(radius: float, length: float, spacing: float = 0.0001):
    """Create shape description variables for the DWBA model for cylinders.

    The shape descriptions are essentially a set of discs and their orientation.

    Parameters
    ----------
    radius :
        The radius [m] of the cylinder.
    length :
        The length [m] of the cylinder.
    spacing :
        The spacing [m] between successive discs.

    Returns
    -------
    rv_pos : iterable[np.ndarray]
        An interable of vectors of the 3D positions of the centre of each disc that
        defines the cylinder. Each vector has three values corresponding to
        the _x_, _y_, and _z_ coordinates [m] of the disc centre.
    rv_tan : iterable[np.ndarray]
        An interable of unit vectors of the tangent to the cylinder body axis at
        the points given in `rv_pos`. Each vector has three values corresponding to
        the _x_, _y_, and _z_ components of the tangent vector.
    a : iterable
        The radii [m] of the discs that define the spheroid.
    """
    pos = np.linspace(0, length, int(round(length/spacing)))
    rv_pos = [np.array([x, 0, 0]) for x in pos]
    rv_tan = [np.array([1, 0, 0])] * len(pos)
    a = [radius] * len(pos)

    return rv_pos, rv_tan, a


@dataclass
class SDWBAorganism():
    """SDWBA shape and property class to represent an organism.

    Attributes
    ----------
    x :
        The _x_-axis coordinates [m].
    y :
        XXX.
    z :
        XXX
    a :
        XXX
    g :
        XXXX
    h :
        XXXX

    """

    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    a: np.ndarray
    g: np.ndarray
    h: np.ndarray


class SDWBAdata():
    """Example datasets for the SDWBA and DWBA models."""

    def __init__(self):
        # Load in the shapes data
        self.file = Path(__file__).parent/Path('resources')/Path('SDWBA_shapes.toml')
        with open(self.file, 'rb') as f:
            try:
                shapes = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise SyntaxError(f'Error while parsing file "{self.defs_filename.name}"') from e

        # Put the shapes into a dict of SDWBAorganism().
        self.sdwba_models = {}
        for s in shapes['shape']:
            organism = SDWBAorganism(np.array(s['x']), np.array(s['y']), np.array(s['z']),
                                     np.array(s['a']), np.array(s['g']), np.array(s['h']))
            self.sdwba_models[s['name']] = organism

    def names(self):
        """Available SDWBA model names."""
        return [*self.sdwba_models]

    def as_dict(self) -> dict:
        """SDWBA model shapes as a dict.

        Returns
        -------
        :
            All the SDWBA model shapes. The dataset name is the dict key and the value is an
            instance of `SDWBAorganism`.

        """
        return self.sdwba_models

    def model(self, name: str) -> SDWBAorganism:
        """SDWBA model shape with requested name.

        Parameters
        ----------
        name :
            The name of a SDWBA model shape.

        Returns
        -------
        :
            An instance of `SDWBAorganism` or None if there is no model with `name`.

        """
        try:
            return self.sdwba_models[name]
        except KeyError:
            return None
