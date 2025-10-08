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
        An iterable of vectors of the 3D positions of the centre of each disc that
        defines the spheroid. Each vector has three values corresponding to
        the _x_, _y_, and _z_ coordinates [m] of the disc centre.
    rv_tan : iterable[np.ndarray]
        An iterable of unit vectors of the tangent to the target body axis at
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
        An iterable of vectors of the 3D positions of the centre of each disc that
        defines the cylinder. Each vector has three values corresponding to
        the _x_, _y_, and _z_ coordinates [m] of the disc centre.
    rv_tan : iterable[np.ndarray]
        An iterable of unit vectors of the tangent to the cylinder body axis at
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


def create_dwba_from_xyza(x, y, z, a, name: str, g: float = 1.0, h: float = 1.0,
                          source: str = '', note: str = ''):
    """Create a DWBAorganism instance from shape data.

    Converts a centreline and radius definiton of the DWBA shape into
    that required by the echoSMs implementation of the DWBA (centreline, tangential, and
    radii vectors).

    Parameters
    ----------
    x : Iterable[float]
        x-coordinates [m] of the centreline of the DWBA shape as per the echoSMs
        [coordinate system](https://ices-tools-dev.github.io/echoSMs/
        conventions/#coordinate-systems).
    y : Iterable[float]
        y-coordinates [m] of the centreline of the DWBA shape as per the echoSMs
        [coordinate system](https://ices-tools-dev.github.io/echoSMs/
        conventions/#coordinate-systems).
    z : Iterable[float]
        z-coordinates [m] of the centreline of the DWBA shape as per the echoSMs
        [coordinate system](https://ices-tools-dev.github.io/echoSMs/
        conventions/#coordinate-systems).
    a : Iterable[float]
        radius [m] of the DWBA shape at each centreline (x,y,z) position.
    name :
        A name for the organism.
    source :
        A link/URL/DOI or description for the source of the data.
    note :
        Notes about the organism or data.
    g :
        A single value of g, the ratio of organism density divided by the
        medium density. This is applied to all parts of the shape.
    h :
        A single value of h, the ratio of organism sound speed divided by
        the medium sound speed. This is applied to all parts of the shape.

    Returns
    -------
        An instance of DWBAorganism.

    Notes
    -----
    Here is an example of how to use this function to read in .sat files
    from the ZooScatR package and convert them into the format required
    by the echoSMs DWBA model.

    ```py
    import pandas as pd
    from echosms import create_dwba_from_xyza

    filepath = 'shape.sat'

    s = pd.read_csv(filepath, delimiter=' ', names=['y', 'x', 'a'])

    # Adjust the data to match the echoSMs units
    s /= 1000  # convert mm to m

    # .sat files don't have a z coordinate but echoSMs requires it
    s['z'] = 0.0

    # An example of flipping left to right to match the echoSMS coordinate system
    s['x'] = max(s['x']) - s['x']

    shape = create_dwba_from_xyza(s['x'], s['y'], s['z'], s['a'], name=filepath, g=1.05, h=1.05)

    ```
    """
    # Estimate rv_tan from a spline through (x,y).
    tck, u = splprep([x, y, z])
    rv_tan = np.vstack(splev(u, tck, der=1))
    # Make sure rv_tan holds only unit vectors
    n = np.linalg.norm(np.vstack(rv_tan), axis=0)
    rv_tan = (rv_tan / n).T

    # Convert the x, y, and z into a 2D array and get one row for each (x,y,z) point.
    rv_pos = np.vstack((x, y, z)).T

    gg = np.full((1, rv_pos.shape[0]), g)
    hh = np.full((1, rv_pos.shape[0]), h)

    return DWBAorganism(rv_pos, a, gg, hh, name, source, note, rv_tan)


@dataclass
class DWBAorganism():
    """DWBA shape and property class to represent an organism.

    Attributes
    ----------
    rv_pos : iterable[np.ndarray]
        An iterable of vectors of the 3D positions of the centre of each disc that
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
        An iterable of unit vectors of the tangent to the body axis at
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
    # items below here are depreciated and will be removed in later revisions
    aphiaid: int = 1
    length: float = 0.0
    vernacular_name: str = ''

    def plot(self):
        """Do a simple plot of the DWBA model data."""
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(2, 1, layout='compressed')
        x = self.rv_pos[:, 0]*1e3
        outline1 = (-self.rv_pos[:, 1] + self.a)*1e3
        outline2 = (-self.rv_pos[:, 1] - self.a)*1e3
        axs[0].plot(x, -self.rv_pos[:, 1]*1e3, '.-', c='C0')
        axs[0].plot(x, outline1, c='C1')
        axs[0].plot(x, outline2, c='C1')
        axs[0].plot([x[0], x[0]], [outline1[0], outline2[0]], c='C1')
        axs[0].plot([x[-1], x[-1]], [outline1[-1], outline2[-1]], c='C1')
        axs[0].set_title('Dorsal', loc='left', fontsize=8)
        axs[0].axis('scaled')
        axs[0].xaxis.set_inverted(True)

        outline1 = (-self.rv_pos[:, 2] + self.a)*1e3
        outline2 = (-self.rv_pos[:, 2] - self.a)*1e3
        axs[1].plot(x, -self.rv_pos[:, 2]*1e3, '.-', c='C0')
        axs[1].plot(x, outline1, c='C1')
        axs[1].plot(x, outline2, c='C1')
        axs[1].plot([x[0], x[0]], [outline1[0], outline2[0]], c='C1')
        axs[1].plot([x[-1], x[-1]], [outline1[-1], outline2[-1]], c='C1')
        axs[1].set_title('Lateral', loc='left', fontsize=8)
        axs[1].axis('scaled')
        axs[1].xaxis.set_inverted(True)

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

        # Put the shapes into a dict of DWBAorganism().
        self.dwba_models = {}
        for s in shapes['shape']:
            mx = max(s['x'])
            s['x'] = np.array(s['x'])-mx  # put head at x=0
            # Estimate rv_tan from a spline through (x,y,z).
            tck, u = splprep([s['x'], s['y'], s['z']])
            rv_tan = np.vstack(splev(u, tck, der=1))
            # Make sure rv_tan holds only unit vectors
            n = np.linalg.norm(np.vstack(rv_tan), axis=0)
            rv_tan = (rv_tan / n).T

            # Convert the x, y, z lists into a 2D array with one row for each (x,y,z) point
            rv_pos = np.vstack((np.array(s['x']), np.array(s['y']), np.array(s['z']))).T

            organism = DWBAorganism(rv_pos, np.array(s['a']), np.array(s['g']), np.array(s['h']),
                                    s['name'], s.get('source', ''), s.get('note', ''), rv_tan,
                                    s['aphiaid'], s['length'], s['vernacular'],)
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
