"""Script to make a figure showing the outline shape coordinates"""

# This script is not complete

import vedo as vd
import numpy as np
from pathlib import Path
import requests

# This code generates the figure

# Use one of the Clay&Horne cod as the example data
baseURI = 'https://echosms-data-store-app-ogogm.ondigitalocean.app/'
r = requests.get(baseURI + 'v2/specimen/CLAY_HORNE_A/data')
specimen = r.json()
shapes = specimen['shapes']

# %%

al = 0.050  # axes length
sr = 0.01  # shaft radius for axes and arrows

bd = [shape for shape in shapes if shape['anatomical_type'] == 'body'][0]
sb = [shape for shape in shapes if shape['anatomical_type'] == 'swimbladder'][0]

discs = []
centrelines = []

for s, c in zip([bd, sb], ['green', 'blue']):
    x = s['x']
    y = s['y']
    z = s['z']
    w = s['width']
    h = s['height']
    spacing = np.abs(np.mean(np.diff(np.array(x))))

    pts = []
    for xx, yy, zz, in zip(x, y, z):
        pts.append((xx, yy, zz))
    centrelines.append(vd.Line(pts, c='black', lw=2))

    for i, _ in enumerate(x):
        discs.append(vd.Cylinder(pos=(x[i],y[i],z[i]), r=h[i]/2, height=spacing,
                                 axis=(-1,0,0), alpha=1, c=c))


# Axes arrows
axes = vd.Arrows(start_pts=[[0, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]],
                 end_pts=[[al, 0, 0],
                          [0, al, 0],
                          [0, 0, al]],
                 shaft_radius=sr, head_radius=0.02, head_length=0.1, res=15)



plt = vd.Plotter(size=(800, 600), bg='white')
plt.show(discs, centrelines, axes)


# %%
resourcesDir = Path(r'../resources')



# the fish model came from: https://3dmag.org/en/market/download/item/6255/
fish = vd.Mesh(str(resourcesDir / 'herring.stl'))
fish.color('green7', alpha=0.9)

# centre the fish on the origin, rotate, and scale
b = fish.bounds()
offset = [-((b[1]-b[0])/2 + b[0]), (b[3]-b[2])/2 + b[2], (b[5]-b[4])/2 + b[4]]
scale = 0.3*al/(b[5] - b[4])
fish.apply_transform(vd.LinearTransform().translate(offset).rotate_x(180).rotate_z(-90))
fish.apply_transform(vd.LinearTransform().scale(scale))

# Axes labels
axes_label_pts = [[al*1.02, 0., 0.], [0., al*1.05, 0.], [0., 0., al*1.07]]
axes_label_txt = ['x', 'y', 'z']


# Rotation arrows
circ_frac = 0.8
along_axis = 0.7
radius = al/10
tube_radius = 0.05

theta = np.arange(0, circ_frac*2*np.pi, 2*np.pi/100)
x = radius * np.cos(theta)
y = radius * np.sin(theta)
z = np.full(x.size, along_axis*al)

rot_line_x = vd.Line(list(zip(z, y, x)))
rot_line_y = vd.Line(list(zip(x, z, y)))
rot_line_z = vd.Line(list(zip(x, y, z)))

rot_arrow_x = vd.Tube(rot_line_x, r=tube_radius, c='red')
rot_arrow_y = vd.Tube(rot_line_y, r=tube_radius, c='green')
rot_arrow_z = vd.Tube(rot_line_z, r=tube_radius, c='yellow')

# need to add arrow heads to these lines

# Rotation labels


# Camera position

plt = vd.Plotter(size=(800, 600), bg='white')
plt.show(fish, axes, rot_arrow_x, rot_arrow_y, rot_arrow_z)

# plt.export(str(resourcesDir/'coordinate_system.html'))
