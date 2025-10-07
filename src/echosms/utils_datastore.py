"""Utilities for working with the echoSMs anatomical datastore."""
import trimesh
import numpy as np
from pathlib import Path
import numpy.typing as npt

def mesh_from_datastore(shapes: list[dict]) -> list[trimesh]:
    """Create trimesh instances from an echoSMs datastore surface shape.

    Parameters
    ----------
    shapes :
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


def surface_from_stl(stl_file: str | Path, 
                     dim_scale: float = 1.0,
                     name: str = 'body',
                     boundary: str = 'soft') -> dict:
    """Create an echoSMs surface shape from an .stl file.

    Parameters
    ----------
    stl_file :
        An .stl file
    dim_scale :
        Scaling factor applied to the node positions. Use to convert from one 
        length unit to another (e.g., 1e-3 will convert from mm to m).
    name : 
        The name for this shape.
    boundary :
        The boundary type for this shape.

    Returns
    -------
    :
        An echoSMs surface shape representation.

    Notes
    -----
    This function uses a call to `load_mesh()` from the `trimesh` library to read the
    .stl file. If there are problems with loading your .stl file, please refer to the 
    `trimesh` documentation.
    """
    mesh = trimesh.load_mesh(stl_file)

    # Boundle up into a dict as per the echoSMs schema for a surface
    return {'name': name, 'boundary': boundary,
            'x': (mesh.vertices[:, 0]*dim_scale).tolist(),
            'y': (mesh.vertices[:, 1]*dim_scale).tolist(),
            'z': (mesh.vertices[:, 2]*dim_scale).tolist(),
            'facets_0': mesh.faces[:, 0].tolist(),
            'facets_1': mesh.faces[:, 1].tolist(),
            'facets_2': mesh.faces[:, 2].tolist(),
            'normals_x': mesh.face_normals[:, 0].tolist(),
            'normals_y': mesh.face_normals[:, 1].tolist(),
            'normals_z': mesh.face_normals[:, 2].tolist()}


def outline_from_krm(x: npt.ArrayLike, height_u: npt.ArrayLike, height_l: npt.ArrayLike,
                     width: npt.ArrayLike,
                     name: str = "body", boundary: str = 'soft') -> dict:
    """
    Convert KRM shape representation to the echoSMs outline shape representation.

    Parameters
    ----------
    x :
        The _x_ values of the centreline
    height_u :
        The distance from _z_ = 0 to the upper part of the shape at each _x_ coordinate.
        Positive values are towards the dorsal surface and negative values towards the ventral
        surface.
    height_l :
        The distance from _z_ = 0 to the lower part of the shape at each _x_ coordinate.
        Positive values are towards the dorsal surface and negative values towards the ventral
        surface.
    width :
        The width of the shape at each _x_ coordinate
    name : 
        The name for this shape.
    boundary :
        The boundary type for this shape.

    Returns
    -------
     An echoSMs outline shape representation.
    """

    y = np.zeros(len(x))
    height = np.array(height_u) - np.array(height_l)
    z = -(np.array(height_l) + height / 2.0)

    return {'name': name, 'boundary': boundary,
            'x': np.array(x).tolist(),
            'y': y.tolist(),
            'z': z.tolist(),
            'height': height.tolist(),
            'width': width.tolist()}


def outline_from_dwba(x, z, radius, name: str = "body", boundary: str = 'soft') -> dict:
    """
    Convert DWBA shape to the echoSMs outline shape representation.
    
    Parameters
    ----------
    x :
        The _x_ values of the centreline
    z :
        The distance of the centreline from _z_ = 0. Positive values are towards
        the dorsal surface and negative values towards the ventral surface.
    radius :
        The radius of the shape at each _x_ coordinate
    name : 
        The name for this shape.
    boundary :
        The boundary type for this shape.

    Returns
    -------
     An echoSMs outline shape representation.
    
    """

    return {'name': name, 'boundary': boundary,
            'x': np.array(x).tolist(),
            'y': np.zeros(len(x)).tolist(),
            'z': (-np.array(z)).tolist(),
            'height': 2*np.array(radius).tolist(),
            'width': 2*np.array(radius).tolist()}
