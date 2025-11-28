"""Functions that convert between different echoSMs datastore shape representations."""

import numpy as np
import trimesh
from trimesh.path.polygons import projected
from shapely import intersection, LineString

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

    # Get a centreline on the x-axis that extends the full length of the organism
    bounds = mesh.bounding_box
    xmin = bounds.vertices[0, 0]
    xmax = bounds.vertices[7, 0]
    centreline_x = np.arange(xmin, xmax, slice_thickness)

    # calculate the shape heights, widths, and y and z coordinates of the centreline
    widths = []
    heights = []
    centreline_y = []
    centreline_z = []

    for x in centreline_x:
        # Get the points where a line perpendicular to the x-axis intersects
        # the dorsal and lateral shapes

        # A line perpendicular to the x-axis that extends off a long way (1000 m)
        line = LineString([[x, -1000], [x, 1000]])
        # and the intersection of that line with the dorsal shape
        intersect = intersection(dorsal, line)

        # The length of that line is the width of the shape at this x position
        widths.append(intersect.length)
        # and the centre point of that line is the y coordinate of the centreline
        centre = intersect.interpolate(0.5, normalized=True)
        # No intersection means the y coordinate of the centreline is 0.0
        centreline_y.append(-centre.y if centre else 0.0)

        # Do similar for the lateral outline
        line = LineString([[-1000, x], [1000, x]])
        intersect = intersection(lateral, line)
        heights.append(intersect.length)
        centre = intersect.interpolate(0.5, normalized=True)
        centreline_z.append(centre.x if centre else 0.0)

    # Create an echoSMs shape dict using the metadata from the input surface shape
    to_remove = ['x', 'y', 'z', 'facets_0', 'facets_1', 'facets_2',
                 'normals_x', 'normals_y', 'normals_z']
    outline_shape = {k: v for k, v in shape.items() if k not in to_remove}

    # Add the outline shape data
    outline_shape['x'] = centreline_x.tolist()
    outline_shape['y'] = centreline_y
    outline_shape['z'] = centreline_z
    outline_shape['height'] = heights
    outline_shape['width'] = widths
    
    return outline_shape
