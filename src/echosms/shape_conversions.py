"""Functions that convert between different echoSMs datastore shape representations."""

import numpy as np
import trimesh
from trimesh.path.polygons import projected
from trimesh.creation import triangulate_polygon, Trimesh

from shapely import intersection, LineString, Polygon

def outline_to_surface(outline: dict, num_pts:int = 20) -> dict:
    """Convert an outline shape to a surface shape.

    Parameters
    ----------
    outline :
        An echoSMs outline shape.
    num_pts :
        The number of points to place on each cross-sectional ellipse.

    Returns
    -------
    :
        An echoSMs surface shape with shape metadata as per the input shape.

    Notes
    -----
    Each outline cross-sectional ellipse is represented by a polygon with num_pts
    vertices. Triangles are created that join the vertices on adjacent polygons.
    The two ends are meshed using an ear slicing algorithm (using the `mapbox_earcut` package, a
    Python binding to a [C++ implementation](https://github.com/mapbox/earcut.hpp) of the
    algorithm).
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
    # Same vectorisation comment here as above
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
    # TODO - ensure this works for end surfaces that are a point (e.g. width or height = 0)
    pts2d = [[p[1], p[2]] for p in pts]  # shapely.Polygon wants a 2D polygon, so remove the x coord

    _, endcap1_faces = triangulate_polygon(Polygon(pts2d[:num_pts]), engine='earcut')
    # the order of the nodes is inverted for endcap2 to have the normals point outwards
    _, endcap2_faces = triangulate_polygon(Polygon(pts2d[:-(num_pts+1):-1]), engine='earcut')
    # Get the right facet indices for endcap2
    endcap2_faces = [f - 1 + num_pts * (num_discs-1) for f in endcap2_faces]

    faces.extend(endcap1_faces)
    faces.extend(endcap2_faces)

    # Put into trimesh to get the face normals
    mesh = Trimesh(vertices=pts, faces=faces)

    if not mesh.is_volume:
        raise ValueError('Mesh is not watertight, not wound consistently, '
                         'or normals are not facing outwards')

    # TODO - consider resampling the mesh to give triangles all of a similar size

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
