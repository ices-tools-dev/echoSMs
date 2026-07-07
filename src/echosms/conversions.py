"""Functions that convert between different echoSMs datastore shape representations."""

from pathlib import Path
import numpy as np
import trimesh
from trimesh.path.polygons import projected
from trimesh.creation import triangulate_polygon, Trimesh
import pymeshlab
import numpy.typing as npt
from scipy.spatial.transform import Rotation as R
from shapely import intersection, LineString, Polygon

def mesh_from_surface(shapes: list[dict]) -> list[trimesh.Trimesh]:
    """Create triangulated meshes from echoSMs datastore surface shapes.

    Parameters
    ----------
    shapes :
        The shapes to convert, in the echoSMs datastore `surface` shape data structure.

    Returns
    -------
    :
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
        if 'spound_speed_compressional' in s:
            c = sum(s['sound_speed_compressional'])/len(s['sound_speed_compressional'])
        else:
            c = np.nan

        if 'mass_density' in s:
            rho = sum(s['mass_density'])/len(s['mass_density'])
        else:
            rho = np.nan

        height2 = np.array(s['height'])/2.0
        return KRMshape(s['boundary'], np.array(s['x']), np.array(s['width']),
                        s['z'] + height2, s['z'] - height2, c, rho)

    if len(shapes) == 0:
        return KRMorganism('', '', [], [])

    KRMshapes = [_to_KRMshape(s) for s in shapes]

    # get the index of the first shape with name == 'body' (if any)
    idx = [i for i, s in enumerate(shapes) if s['anatomical_feature'] == 'body']
    if not idx:
        idx = [0]  # No shape with name of body so we use the first shape as the body

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
                     anatomical_feature: str = 'body',
                     boundary: str = 'pressure-release') -> dict:
    """Create an echoSMs surface shape from an .stl file.

    Parameters
    ----------
    stl_file :
        An .stl file
    dim_scale :
        Scaling factor applied to the node positions. Use to convert from one
        length unit to another (e.g., 1e-3 will convert from mm to m).
    anatomical_feature :
        The anatomical feature for this shape, as per the echoSMs datastore schema.
    boundary :
        The boundary type for this shape, as per the echoSMs datastore schema.

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

    # Bundle up into a dict as per the echoSMs schema for a surface
    return {'anatomical_feature': anatomical_feature, 'boundary': boundary,
            'shape_units': 'm',
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
                     anatomical_feature: str = "body",
                     boundary: str = 'pressure-release') -> dict:
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
    anatomical_feature :
        The anatomical feature for this shape, as per the echoSMs datastore schema.
    boundary :
        The boundary type for this shape, as per the echoSMs datastore schema.

    Returns
    -------
     An echoSMs outline shape representation.
    """
    y = np.zeros(len(x))
    height = np.array(height_u) - np.array(height_l)
    z = -(np.array(height_l) + height / 2.0)

    return {'anatomical_feature': anatomical_feature, 'boundary': boundary,
            'shape_units': 'm',
            'x': np.array(x).tolist(),
            'y': y.tolist(),
            'z': z.tolist(),
            'height': height.tolist(),
            'width': np.array(width).tolist()}


def outline_from_dwba(x, z, radius, anatomical_feature: str = "body",
                      boundary: str = 'pressure-release') -> dict:
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
    anatomical_feature :
        The anatomical feature for this shape, as per the echoSMs datastore schema.
    boundary :
        The boundary type for this shape, as per the echoSMs datastore schema.

    Returns
    -------
     An echoSMs outline shape representation.

    """
    return {'anatomical_feature': anatomical_feature,
            'boundary': boundary,
            'shape_units': 'm',
            'x': np.array(x).tolist(),
            'y': np.zeros(len(x)).tolist(),
            'z': (-np.array(z)).tolist(),
            'height': (2*np.array(radius)).tolist(),
            'width': (2*np.array(radius)).tolist()}


def outline_to_surface(outline: dict, num_pts:int = 20, mesh_len:float = 2.0) -> dict:
    """Convert an outline shape to a surface shape.

    Parameters
    ----------
    outline :
        An echoSMs outline shape.
    num_pts :
        The number of points to place on each cross-sectional ellipse.
    mesh_len :
        The desired typical mesh length as a percentage of overall object size

    Returns
    -------
    : dict[str, list]
        An echoSMs surface shape with shape metadata as per the input shape.

    Notes
    -----
    Each outline cross-sectional ellipse is represented by a polygon with num_pts
    vertices. Triangles are created that join the vertices on adjacent polygons.
    The two ends are meshed using an ear slicing algorithm (using the `mapbox_earcut` package, a
    Python binding to a [C++ implementation](https://github.com/mapbox/earcut.hpp) of the
    algorithm).

    The mesh is then remeshed using the pymeshlab isotropic remeshing algorithm.
    """
    num_discs = len(outline['x'])

    # Create points around each ellipse cross-section of the outline shape
    t = np.linspace(0, 2*np.pi, num=num_pts, endpoint=False)
    pts = []
    # Could vectorise this, but then the code is harder to understand and the number of
    # discs that this will iterate over is fairly small so speed isn't a concern
    for i in range(num_discs):
        pts_y = outline['y'][i] + outline['width'][i]/2 * np.cos(t)
        pts_z = outline['z'][i] + outline['height'][i]/2 * np.sin(t)
        pts_x = np.full(pts_y.shape, outline['x'][i])
        pts.extend(np.c_[pts_x, pts_y, pts_z].tolist())

    # Create triangles connecting respective points on each ellipse
    # Same vectorisation/speed comment here as above
    faces = []
    for disc in range(num_discs-1):
        for pt_i in range(num_pts):
            face = [disc*num_pts + pt_i,
                    (disc+1)*num_pts + pt_i,
                    disc*num_pts + (pt_i+1) % num_pts]
            faces.append(face)

            face = [disc*num_pts + (pt_i+1) % num_pts,
                    (disc+1)*num_pts + pt_i,
                    (disc+1)*num_pts + (pt_i+1) % num_pts]
            faces.append(face)

    # Create triangles for the two end surfaces
    pts2d = [[p[1], p[2]] for p in pts]  # shapely.Polygon wants a 2D polygon, so remove the x coord

    _, endcap1_faces = triangulate_polygon(Polygon(pts2d[:num_pts]), engine='earcut')
    # the order of the nodes is inverted for endcap2 to have the normals point outwards
    _, endcap2_faces = triangulate_polygon(Polygon(pts2d[:-(num_pts+1):-1]), engine='earcut')
    # Get the right facet indices for endcap2
    endcap2_faces = [f - 1 + num_pts * (num_discs-1) for f in endcap2_faces]

    faces.extend(endcap1_faces)
    faces.extend(endcap2_faces)

    # Tidy the mesh using pymeshlab
    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(pts, faces))
    # ms.save_current_mesh('test_before.stl')
    #ms.meshing_merge_close_vertices()
    #ms.meshing_remove_t_vertices()
    #ms.meshing_close_holes()
    #ms.meshing_repair_non_manifold_edges()
    #ms.meshing_re_orient_faces_coherently()
    #ms.meshing_isotropic_explicit_remeshing(targetlen=pymeshlab.PercentageValue(mesh_len),
    #                                        adaptive=True)
    # ms.save_current_mesh('test_after.stl')
    m = ms.current_mesh()

    # Put into trimesh to get the face normals and do some checks
    mesh = Trimesh(vertices=m.vertex_matrix(), faces=m.face_matrix())

    errors = []
    if not mesh.is_watertight:
        errors.append('Mesh is not watertight')
    if not mesh.is_winding_consistent:
        errors.append('Mesh winding is not consistent')
    if errors:
        raise ValueError(', '.join(errors))

    # structure as an echoSMs surface dict
    surface = {'x': mesh.vertices[:, 0].tolist(),
               'y': mesh.vertices[:, 1].tolist(),
               'z': mesh.vertices[:, 2].tolist(),
               'facets_0': mesh.faces[:, 0].tolist(),
               'facets_1': mesh.faces[:, 1].tolist(),
               'facets_2': mesh.faces[:, 2].tolist(),
               'normals_x': mesh.face_normals[:, 0].tolist(),
               'normals_y': mesh.face_normals[:, 1].tolist(),
               'normals_z': mesh.face_normals[:, 2].tolist(),
               }

    # Copy across other attributes from the outline shape
    attrs = {k:v for k, v in outline.items() if k not in ['x', 'y', 'z', 'height', 'width']}

    return attrs | surface


def surface_to_outline(shape: dict, slice_thickness: float=5e-3) -> dict:
    """Convert a surface shape to an outline shape.

    Parameters
    ----------
    shape :
        An echoSMs surface shape.
    slice_thickness :
        The slice thickness [m] used when generating the outline.

    Returns
    -------
    :
        An echoSMs outline shape with shape metadata as per the input shape.

    Notes
    -----
    The conversion projects the surface shape to get dorsal and lateral outlines and then
    slices along the _x_-axis at a configurable resolution to produce the outline shape.
    """
    # Put the shape into a trimesh mesh
    v = np.array([shape['x'], shape['y'], shape['z']]).T
    f = np.array([shape['facets_0'], shape['facets_1'], shape['facets_2']]).T
    mesh = trimesh.Trimesh(vertices=v, faces=f)

    # Project the surface mesh onto dorsal and lateral planes
    dorsal = projected(mesh, normal=[0, 0, 1], ignore_sign=True)
    lateral = projected(mesh, normal=[0, -1, 0], ignore_sign=True)

    # Get bounds for a centreline on the x-axis that extends the full length of the organism
    bounds = mesh.bounding_box
    xmin = bounds.vertices[0, 0]
    xmax = bounds.vertices[7, 0]

    # calculate the shape heights, widths, and y and z coordinates of the centreline
    widths = []
    heights = []
    centreline_x = []
    centreline_y = []
    centreline_z = []

    for x in np.arange(xmin, xmax, slice_thickness):
        # Get the points where a line perpendicular to the x-axis intersects
        # the dorsal and lateral shapes

        # A line perpendicular to the x-axis that extends off a long way (1000 m)
        line = LineString([[x, -1000], [x, 1000]])
        # and the intersection of that line with the dorsal shape
        intersect = intersection(dorsal, line)

        # If there is no intersection, go to the next x-point. This can happen
        # at the start or end of the bounding box
        if not intersect:
            continue

        # The length of that line is the width of the shape at this x position
        w = intersect.length
        # and the centre point of that line is the y coordinate of the centreline
        centre = intersect.interpolate(0.5, normalized=True)
        y = -centre.y

        # Do similar for the lateral outline
        line = LineString([[-1000, x], [1000, x]])
        intersect = intersection(lateral, line)
        if not intersect:
            continue

        heights.append(intersect.length)
        centre = intersect.interpolate(0.5, normalized=True)

        widths.append(w)
        centreline_x.append(x)
        centreline_y.append(y)
        centreline_z.append(centre.x)

    # Create an echoSMs shape dict using the metadata from the input surface shape
    to_remove = ['x', 'y', 'z', 'facets_0', 'facets_1', 'facets_2',
                 'normals_x', 'normals_y', 'normals_z']
    outline_shape = {k: v for k, v in shape.items() if k not in to_remove}

    # Add the outline shape data
    outline_shape['x'] = centreline_x
    outline_shape['y'] = centreline_y
    outline_shape['z'] = centreline_z
    outline_shape['height'] = heights
    outline_shape['width'] = widths

    return outline_shape

def mesh_from_geometric(shapes: list[dict]) -> trimesh.Trimesh:
    """Create a triangulated mesh from a datastore geometric shape.
    
    Parameters
    ----------
    shapes :
        Geometric shapes defined as per the echoSMs datastore schema.
    
    Returns
    -------
    :
        The mesh resulting from the merging of the input shapes.
    """
    meshes = []

    for s in shapes:
        match s['geometric_form']:
            case 'spheroid':
                meshes.append(_spheroid_mesh(**s))
            case 'cylinder':
                meshes.append(_cylinder_mesh(**s))
            case _:
                raise ValueError('geometric_form of {} is not yet supported'.format(s['geometric_form']))

    return trimesh.boolean.union(meshes, check_volume=False)


def _spheroid_mesh(equatorial_radius: float, polar_radius: float,
                   origin_location: tuple[float]|None=None,
                   pitch: float=0.0, roll: float=0.0, yaw:float=0.0, **kwargs):
    """Create a spheroid triangulated mesh as per the size and orientation."""

    if origin_location is None:
        origin_location = (0.0, 0.0, 0.0)

    mesh = trimesh.creation.icosphere(subdivisons=3)
    scale = np.diag([equatorial_radius, equatorial_radius, polar_radius, 1.0])
    return mesh.apply_transform(_transform(pitch, roll, yaw, origin_location) @ scale)


def _cylinder_mesh(radius: float, length: float, origin_location: tuple[float]|None=None,
                  pitch: float=0.0, roll: float=0.0, yaw: float=0.0, **kwargs):
    """Create a cylinder triangulated mesh as per the size and orientation."""

    if origin_location is None:
        origin_location = (0.0, 0.0, 0.0)

    mesh = trimesh.creation.cylinder(radius=radius, height=length, sections=32)
    return mesh.apply_transform(_transform(pitch, roll, yaw, origin_location))


def _transform(pitch: float, roll: float, yaw: float, o: tuple[float]):
    """Calculate a rotation and origin shift matrix."""

    rotation = R.from_euler('ZYX', (yaw, pitch-90, -roll), degrees=True)
    transform = np.eye(4)
    transform[:3, :3] = rotation.as_matrix()
    transform[:3, 3] = o

    return transform
