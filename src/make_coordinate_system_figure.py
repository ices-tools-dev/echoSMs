# %%
"""Create the coordinate system figure for the documentation."""
import pyvista as pv
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET

# These two functions came from https://github.com/pyvista/pyvista/discussions/5023 and are
# used to create arced arrows.


def rotate_to(a, b):
    """Return a rotation matrix taking the vector A to B."""
    # Naive approach is unstable if a and b are near parallel
    theta = np.arccos(np.dot(a, b))
    eps = 1e-3
    if np.absolute(theta) < eps:
        return np.eye(4)
    elif np.absolute(np.pi - theta) < eps:  # Close to 180 degrees
        # Choose the coordinate axis most orthogonal to A
        x = np.zeros(3)
        x[np.argmin(np.absolute(a))] = 1.0
        axis = np.cross(a, x)
        axis /= np.linalg.norm(axis)
        return pv.utilities.transformations.axis_angle_rotation(axis, theta, deg=False)
    else:
        axis = np.cross(a, b)
        return pv.utilities.transformations.axis_angle_rotation(axis, theta, deg=False)


def semi_circular_arrow(
        start_angle=0,
        circ_frac=0.75,
        body_axial_res=100,
        body_radial_res=50,
        head_radial_res=100,
        circ_radius=10,
        body_radius=1,
        head_length=3,
        head_radius_frac=1.5,
        normal=None,
        center=None):
    """Create a semi circular arrow."""
    t = np.linspace(0, circ_frac * 2 * np.pi, body_axial_res) + start_angle
    x = circ_radius * np.cos(t)
    y = circ_radius * np.sin(t)
    z = np.zeros(body_axial_res)
    body_pts = np.column_stack([x, y, z])
    body = pv.MultipleLines(body_pts).tube(body_radius, n_sides=body_radial_res)

    # Direction the head points
    dhead = body_pts[-1] - body_pts[-2]
    dhead /= np.linalg.norm(dhead)

    head = pv.Cone(
        center=body_pts[-1] + dhead * (head_length / 2),
        direction=dhead,
        height=head_length,
        radius=head_radius_frac * body_radius,
        resolution=head_radial_res,
    )

    arrow = body.merge(head, merge_points=False)

    if normal is not None:
        arrow = arrow.transform(rotate_to((0, 0, 1), normal), inplace=False)

    if center is not None:
        arrow = arrow.translate(center, inplace=False)

    return arrow

# %%
# This code generates the figure


resourcesDir = Path(r'../resources')
al = 10.0  # axes length
sr = 0.01  # shaft radius for axes and arrows

# Axes arrows
arrow_x = pv.Arrow(start=(0, 0, 0), direction=(al, 0, 0), shaft_radius=sr, tip_radius=0.02,
                   tip_length=0.1, scale='auto')
arrow_y = pv.Arrow(start=(0, 0, 0), direction=(0, al, 0), shaft_radius=sr, tip_radius=0.02,
                   tip_length=0.1, scale='auto')
arrow_z = pv.Arrow(start=(0, 0, 0), direction=(0, 0, al), shaft_radius=sr, tip_radius=0.02,
                   tip_length=0.1, scale='auto')

# Angle arrows and arcs
circ_frac = 0.8
along_axis = 0.7
arc_pitch = semi_circular_arrow(center=(0, al*along_axis, 0), circ_frac=circ_frac,
                                start_angle=-0,
                                circ_radius=al/10, normal=(0, 1, 0),
                                body_radius=0.05, head_length=0.5)
arc_roll = semi_circular_arrow(center=(al*along_axis, 0, 0), circ_frac=circ_frac,
                               start_angle=0,
                               circ_radius=al/10, normal=(1, 0, 0),
                               body_radius=0.05, head_length=0.5)
arc_yaw = semi_circular_arrow(center=(0, 0, al*along_axis), circ_frac=circ_frac,
                              start_angle=0,
                              circ_radius=al/10, normal=(0, 0, 1),
                              body_radius=0.05, head_length=0.5)

# axes labels
axes_label_pts = [[al*1.02, 0., 0.], [0., al*1.05, 0.], [0., 0., al*1.07]]
axes_label_txt = ['x', 'y', 'z']

# angle labels
angles_label_pts = [[al*along_axis, 0., -al/10*1.1],
                    [al/10*1.1, al*along_axis, 0.],
                    [al/10*1.1, 0., al*along_axis]]
angles_label_txt = ['φ', 'θ', 'ψ']

# the fish model came from: https://3dmag.org/en/market/download/item/6255/
reader = pv.get_reader('../resources/herring.stl')
fish = reader.read()

# centre the fish on the origin
b = fish.bounds
offset = (-((b[1]-b[0])/2 + b[0]), (b[3]-b[2])/2 + b[2], (b[5]-b[4])/2 + b[4])
fish.translate(offset, inplace=True)

# rotate the fish to fit our coordinate system
fish.rotate_x(180, inplace=True)
fish.rotate_z(-90, inplace=True)

# scale the fish to length (along the z axis)
length = fish.bounds[5] - fish.bounds[4]
fish.scale(0.3*al/length, inplace=True)

# Assemble the 3D scene
for t in [pv.themes.DocumentTheme(), pv.themes.DarkTheme()]:

    text_colour = 'black'
    if t.name == 'dark':
        text_colour = pv.Color([190, 193, 198])  # to match text color in the docs dark theme
        t.background = pv.Color([20, 33, 41])  # to match the background in the docs dark theme

    p = pv.Plotter(window_size=[1600, 860], theme=t, off_screen=True)
    p.add_mesh(fish, opacity=.9)
    p.add_mesh(arrow_x, color='gray')
    p.add_mesh(arrow_y, color='gray')
    p.add_mesh(arrow_z, color='gray')
    p.add_mesh(arc_pitch, color='green')
    p.add_mesh(arc_roll, color='red')
    p.add_mesh(arc_yaw, color='yellow')

    # the angle labels
    p.add_point_labels(angles_label_pts, angles_label_txt, font_family='times', italic=True,
                       bold=False, shape=None, always_visible=True, show_points=False,
                       font_size=50, text_color=text_colour)
    # the axes labels
    p.add_point_labels(axes_label_pts, axes_label_txt,
                       font_size=50, italic=True, bold=False, shape=None,
                       always_visible=True, show_points=False, font_family='times',
                       text_color=text_colour)

    p.camera_position = [(9.44840097372024, 17.277196718053595, -7.056312001523225),
                         (2.7462545037450483, 2.6898350612751827, 1.695119545588695),
                         (-0.2125924945535939, -0.42901864969164194, -0.877922222908294)]

    # Unfortunately, all exports have issues...
    # p.export_html('coordinate_system2.html')  # loses all text
    # p.export_obj('coordinate_system2.obj')  # no colour?
    # p.export_gltf('coordinate_system2.gltf')  # loses text
    # p.export_vrml('coordinate_system2.vrml')  # no text??
    # p.export_vtksz(resourcesDir/'coordinate_system.vtksz')

    # no greek symbols and scale > 1 loses some of the text
    # p.screenshot('coordinate_system2.png', transparent_background=True, scale=1)

    # Best option for the moment. Html would be preferrable if the text showed up
    if t.name == 'dark':
        savefile = resourcesDir/'coordinate_system_dark.svg'
    else:
        savefile = resourcesDir/'coordinate_system_light.svg'

    p.save_graphic(savefile)  # raster, otherwise good

    # this generates an on-screen version. But doesn't show the greek symbols
    # p.show()

    # p.close()

    # Modify the generate svg to make the labels properly italic
    tree = ET.parse(savefile)
    root = tree.getroot()

    for text in root.iter('{http://www.w3.org/2000/svg}text'):
        text.set('font-style', 'italic')

    tree.write(savefile)
