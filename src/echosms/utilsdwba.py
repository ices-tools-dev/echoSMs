"""Miscellaneous functions for the DWBA models."""
import numpy as np


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
