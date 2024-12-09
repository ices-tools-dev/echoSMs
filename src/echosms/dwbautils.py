"""Miscellaneous functions for the DWBA models."""
import numpy as np
from pathlib import Path
import sys
from dataclasses import dataclass
from scipy.interpolate import splprep, splev
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
class DWBAorganism():
    """DWBA shape and property class to represent an organism.

    Attributes
    ----------
    rv_pos : iterable[np.ndarray]
        An interable of vectors of the 3D positions of the centre of each disc that
        defines the target shape. Each vector should have three values corresponding to
        the _x_, _y_, and _z_ coordinates [m] of the disc centre, as per the echoSMs
        [coordinate system](https://ices-tools-dev.github.io/echoSMs/
        conventions/#coordinate-systems).
    a :
        The radii [m] of each disc.
    g :
        The density contrast between medium and organism (organism divied by medium).
    h :
        The sound speed contrast betwwen medium and organism (organism divied by medium).
    source :
        A link to the source of the data.
    note :
        Information about the data.
    rv_tan :
        An interable of unit vectors of the tangent to the body axis at
        the points given by (_x_, _y_, _z_). Each vector has three values corresponding to
        the _x_, _y_, and _z_ components of the tangent vector [m]. If not given, unit
        vectors pointing along the positive _x_-axis are used.
    """

    rv_pos: np.ndarray
    a: np.ndarray
    g: np.ndarray
    h: np.ndarray
    name: str
    source: str = ''
    note: str = ''
    rv_tan: np.ndarray = None

    def plot(self):
        """Do a simple plot of the DWBA model data."""
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(2, 1)
        x = self.rv_pos[:, 0]*1e3
        axs[0].plot(x, -self.rv_pos[:, 1]*1e3, '.-', c='C0')
        axs[0].plot(x, (-self.rv_pos[:, 1]+self.a/2)*1e3, c='C1')
        axs[0].plot(x, (-self.rv_pos[:, 1]-self.a/2)*1e3, c='C1')
        axs[0].set_title('Dorsal', loc='left', fontsize=8)
        axs[0].set_aspect('equal')

        axs[1].plot(x, -self.rv_pos[:, 2]*1e3, '.-', c='C0')
        axs[1].plot(x, (-self.rv_pos[:, 2]+self.a/2)*1e3, c='C1')
        axs[1].plot(x, (-self.rv_pos[:, 2]-self.a/2)*1e3, c='C1')
        axs[1].set_title('Lateral', loc='left', fontsize=8)
        axs[1].set_aspect('equal')

        plt.suptitle(self.name)
        plt.show()


class DWBAdata():
    """Example datasets for the SDWBA and DWBA models."""

    def __init__(self):
        # Load in the shapes data
        self.file = Path(__file__).parent/Path('resources')/Path('DWBA_shapes.toml')
        with open(self.file, 'rb') as f:
            try:
                shapes = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise SyntaxError(f'Error while parsing file "{self.defs_filename.name}"') from e

        # Put the shapes into a dict of SDWBAorganism().
        self.dwba_models = {}
        for s in shapes['shape']:
            # Estimate rv_tan from a spline through (x,y,z).
            tck, u = splprep([s['x'], s['y'], s['z']])
            rv_tan = np.vstack(splev(u, tck, der=1))
            # Make sure rv_tan holds only unit vectors
            n = np.linalg.norm(np.vstack(rv_tan), axis=0)
            rv_tan = (rv_tan / n).T

            # Convert the x, y, z lists into a 2D array with one row for each (x,y,z) point
            rv_pos = np.vstack((np.array(s['x']), np.array(s['y']), np.array(s['z']))).T

            organism = DWBAorganism(rv_pos, np.array(s['a']), np.array(s['g']), np.array(s['h']),
                                    s['name'], s.get('source', ''), s.get('note', ''), rv_tan)
            self.dwba_models[s['name']] = organism

    def names(self):
        """Available DWBA model names."""
        return [*self.dwba_models]

    def as_dict(self) -> dict:
        """DWBA model shapes as a dict.

        Returns
        -------
        :
            All the DWBA model shapes. The dataset name is the dict key and the value is an
            instance of `DWBAorganism`.

        """
        return self.dwba_models

    def model(self, name: str) -> DWBAorganism:
        """DWBA model shape with requested name.

        Parameters
        ----------
        name :
            The name of a DWBA model shape.

        Returns
        -------
        :
            An instance of `DWBAorganism` or None if there is no model with `name`.

        """
        try:
            return self.dwba_models[name]
        except KeyError:
            return None
