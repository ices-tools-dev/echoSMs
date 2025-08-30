"""Utilities for working with the echoSMs anatomical datastore."""
import trimesh
import numpy as np


def mesh_from_datastore(shapes: list[dict]) -> list[trimesh]:
    """Create trimesh instances from an echoSMs datastore surface shape.

    Parameters
    ----------
    shape :
        The shapes to convert, in the echoSMs datastore `surface` shape data structure.

    Returns
    -------
        The shapes in trimesh form, in the same order as the input.

    """

    def _to_trimesh(s: dict) -> trimesh.Trimesh:
        """Put echoSMs datstore shape into a trimesh instance."""
        faces = [f for f in zip(s['facets_0'], s['facets_1'], s['facets_2'])]
        vertices = [v for v in zip(s['x'], s['y'], s['z'])]

        return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)

    return [_to_trimesh(s) for s in shapes]


def dwbaorganism_from_datastore(shape: dict):
    """Create a DWBAorganism instance from an echoSMs datastore shape.

    Converts the centreline and width/height definition of a shape into that
    required by the echoSMs implementation of the DWBA (centreline, tangential, and
    radii vectors).

    Parameters
    ----------
    shape :
        The shape to convert, in the echoSMs datastore `outline` shape data structure.

    Returns
    -------
        An instance of DWBAorganism

    Notes
    -----
    The DWBA simulates a circular shape but the echoSMs datastore shape can store non-
    circular shapes (via the height and width). This function uses the height information
    and ignores the width information.

    If `mass_density_ratio` and `sound_speed_ratio` are present into the shape dict,
    these are used. If not, default values are used by DWBorganism().
    """
    from echosms import create_dwba_from_xyza  # here to avoid a circular import
    a = np.array(shape['height']) * 0.5
    if 'mass_density_ratio' in shape and 'sound_speed_ratio' in shape:
        return create_dwba_from_xyza(shape['x'], shape['y'], shape['z'], a,
                                     shape['name'], shape['mass_density_ratio'],
                                     shape['sound_speed_ratio'])

    return create_dwba_from_xyza(shape['x'], shape['y'], shape['z'], a, shape['name'])


def krmorganism_from_datastore(shapes: list[dict]) -> list:
    """Create a KRMorganism instance from an echoSMs datastore shape.

    Converts the centreline and width/height definition of a shape into that
    required by the echoSMs implementation of the KRM (straight centreline, width, upper and
    lower heights from the centreline).

    Parameters
    ----------
    shapes :
        The shapes to convert, in the echoSMs datastore `outline` shape data structure.

    Returns
    -------
        Instances of KRMorganism

    Notes
    -----
    The shape with name `body` becomes the main organism body and all other shapes become
    inclusions. If there is no shape with name of `body`, the first shape is used for the body.

    The KRM uses just one sound speed and density per shape, but datastore shapes can have values
    per _x_-axis value. The mean of the sound speed and density values are used if so.

    Datastore shapes can have non-zero _y_-axis values but these are ignored when creating
    a KRMorganism instance.

    """
    from echosms import KRMorganism, KRMshape  # here to avoid a circular import

    def _to_KRMshape(s: dict):
        """Convert echoSMs datstore shape into a KRMshape."""
        # Take mean of sound speed and density in case there is more than one value.
        c = sum(s['sound_speed_compressional'])/len(s['sound_speed_compressional'])
        rho = sum(s['mass_density'])/len(s['mass_density'])

        height2 = np.array(s['height'])/2.0
        return KRMshape(s['boundary'], np.array(s['x']), np.array(s['width']),
                        s['z'] + height2, s['z'] - height2, c, rho)

    if len(shapes) == 0:
        return KRMorganism('', '', [], [])

    KRMshapes = [_to_KRMshape(s) for s in shapes]

    # get the index of the first shape with name == 'body' (if any)
    idx = [i for i, s in enumerate(shapes) if s['name'] == 'body']
    if not idx:
        idx = 0  # No shape with name of body so we use the first shape as the body

    body = KRMshapes.pop(idx[0])
    inclusions = KRMshapes

    return KRMorganism('', '', body, inclusions)


def volume_from_datastore(voxels: list):
    """Create a 3D numpy array from nested lists.

    Parameters
    ----------
    voxels :
        The datastore 3D voxel structure (list of list of list)

    Returns
    -------
        A numpy 3D array.
    """
    return np.array(voxels)  # TODO - check ordering is correct!
