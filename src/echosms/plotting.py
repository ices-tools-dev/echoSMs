"""Functions to create plots of specimens."""
import numpy as np
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from matplotlib import colors, colormaps
import trimesh
from math import floor
from .utils import boundary_type as bt

def plot_specimen(specimen: dict, dataset_label: str='', title: str='',
                  savefile: str|None=None, dpi: float=150) -> None:
    """Plot the specimen shape.

    Produces a relevant plot for all echoSMs anatomical datastore shape types.

    Parameters
    ----------
    specimen :
        Specimen data as per the echoSMs anatomical datastore schema.
    dataset_label :
        Used to form a plot title if `title` is an empty string.
    title :
        A title for the plot.
    savefile :
        Filename to save the plot to. If None, generate the plot in the
        interactive terminal (if that's supported).
    dpi :
        The resolution of the figure in dots per inch.

    """
    labels = ['Dorsal', 'Lateral']
    t = title if title else dataset_label + ' ' + specimen['specimen_name']

    match specimen['shape_type']:
        case 'outline':
            fig, axs = plt.subplots(2, 1, sharex=True, layout='tight')
            fig.set_layout_engine('tight', h_pad=1, w_pad=1)
            plot_shape_outline(specimen['shapes'], axs)
            for label, a in zip(labels, axs):
                a.set_title(label, loc='left', fontsize=8)
                a.axis('scaled')
            axs[0].set_title(t)
            _fit_to_axes(fig)
        case 'surface':
            fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
            plot_shape_surface(specimen['shapes'], ax)
            plt.tight_layout()
            ax.set_title(t)
        case 'voxels':
            plot_shape_voxels(specimen['shapes'][0], t)
        case 'categorised voxels':
            plot_shape_categorised_voxels(specimen['shapes'][0], t)
        case 'geometric':
            fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
            plot_shape_geometric(specimen['shapes'], ax)
            plt.tight_layout()
            ax.set_title(t)

        case _:
            # valid specimen data structures will never get here
            raise ValueError('Specimen shape_type of "{}" is not yet supported'.format(specimen['shape_type']))
        

    if savefile:
        plt.savefig(savefile, format='png', dpi=dpi, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def _fit_to_axes(fig):
    """Change figure size to fit the axes."""
    w = h = 0.0
    for a in fig.axes:
        bbox = a.get_window_extent()
        w = max(w, bbox.width)
        h += bbox.height
    fig.set_size_inches(w/fig.dpi, h/fig.dpi)


def plot_shape_outline(shapes: list[dict], axs: list) -> None:
    """Plot an echoSMs anatomical outline shape.

    Normally called via [plot_specimen()][echosms.plotting.plot_specimen].

    Parameters
    ----------
    shapes :
        Outline shapes to be plotted
    axs :
        Two matplotlib axes - one for the dorsal view and one for the
        lateral view
    """
    for s in shapes:
        c = 'C0' if s['boundary'] == bt.fluid_filled else 'C1'
        x = np.array(s['x'])*1e3
        z = np.array(s['z'])*1e3
        y = np.array(s['y'])*1e3
        width_2 = np.array(s['width'])/2*1e3
        zU = (z + np.array(s['height'])/2*1e3)
        zL = (z - np.array(s['height'])/2*1e3)

        # Dorsal view
        axs[0].plot(x, y, c='grey', linestyle='--', linewidth=1)  # centreline
        axs[0].plot(x, y+width_2, c=c)
        axs[0].plot(x, y-width_2, c=c)

        # Lateral view
        axs[1].plot(x, z, c='grey', linestyle='--', linewidth=1)  # centreline
        axs[1].plot(x, zU, c=c)
        axs[1].plot(x, zL, c=c)

        # close the ends of the shapes
        for i in [0, -1]:
            axs[1].plot([x[i], x[i]], [zU[i], zL[i]], c=c)
            axs[0].plot([x[i], x[i]], [(y+width_2)[i], (y-width_2)[i]], c=c)
            axs[i].xaxis.set_inverted(True)
            axs[i].yaxis.set_inverted(True)


def plot_shape_surface(shapes: list[dict], ax):
    """Plot an echoSMs anatomical surface shape.

    Normally called via [plot_specimen()][echosms.plotting.plot_specimen].

    Parameters
    ----------
    shapes :
        Surface shapes to be plotted
    ax :
        A matplotlib axis.
    """
    for s in shapes:
        c = 'C0' if s['boundary'] == bt.fluid_filled else 'C1'
        facets = np.array([s['facets_0'], s['facets_1'], s['facets_2']]).transpose()
        x = 1e3 * np.array(s['x'])
        y = 1e3 * np.array(s['y'])
        z = 1e3 * np.array(s['z'])

        ax.plot_trisurf(x, y, z, triangles=facets, alpha=0.6, color=c)
        ax.view_init(elev=210, azim=-60, roll=0)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        ax.set_aspect('equal')
        ax.xaxis.set_inverted(True)
        ax.yaxis.set_inverted(True)


def plot_shape_voxels(s: list[dict], title: str=''):
    """Plot the specimen's voxels.

    Normally called via [plot_specimen()][echosms.plotting.plot_specimen].

    Parameters
    ----------
    s :
        The voxel shape data structure as per the echoSMs datastore.

    title :
        Title for the plot.

    """
    # Show density. Could do sound speed or some impedance proxy.
    d = np.array(s['sound_speed_compressional'])
    voxel_size = np.array(s['voxel_size'])
    shape = d.shape

    # Make the colours ignore extreme high value and the lowest low values
    norm = colors.Normalize(vmin=np.percentile(d.flat, 1),
                            vmax=np.percentile(d.flat, 99))

    row_dim = np.linspace(0, voxel_size[0]*1e3*shape[0], shape[0]+1)
    slice_dim = np.linspace(0, voxel_size[2]*1e3*shape[2], shape[2]+1)

    cmap = colormaps['viridis']

    # Create 25 plots along the organism's echoSMs x-axis
    fig, axs = plt.subplots(5, 5, sharex=True, sharey=True)
    cols = np.linspace(0, shape[1]-1, num=25)

    for col, ax in zip(cols, axs.flat):
        c = int(floor(col))
        # The [::-1] and .invert_ axis calls give the appropriate
        # x and y axes directions in the plots.
        im = ax.pcolormesh(slice_dim[::-1], row_dim[::-1], d[:,c,:],
                           norm=norm, cmap=cmap)

        ax.set_aspect('equal')
        ax.invert_xaxis()
        ax.invert_yaxis()

        ax.text(0.05, .86, f'{col*1e3*voxel_size[1]:.0f} mm',
                transform=ax.transAxes, fontsize=6, color='white')

    # A single colorbar in the plot
    cbar = fig.colorbar(im, ax=axs, orientation='vertical',
                        fraction=0.1, extend='both', cmap=cmap)
    cbar.ax.set_ylabel('[kg m$^{-3}$]')
    fig.supxlabel('y [mm]')
    fig.supylabel('z [mm]')
    fig.suptitle(title)


def plot_shape_categorised_voxels(s: list[dict], title: str=''):
    """Plot the specimen's categorised voxels.

    Normally called via [plot_specimen()][echosms.plotting.plot_specimen].

    Parameters
    ----------
    s :
        The categorised voxel shape data structure as per the echoSMs datastore.
    title :
        Title for the plot.
    """
    d = np.array(s['categories'])
    voxel_size = np.array(s['voxel_size'])
    shape = d.shape

    cats = np.unique(d)
    norm = colors.Normalize(vmin=min(cats), vmax=max(cats))

    row_dim = np.linspace(0, voxel_size[0]*1e3*shape[0], shape[0]+1)
    slice_dim = np.linspace(0, voxel_size[2]*1e3*shape[2], shape[2]+1)

    cmap = colormaps['Dark2']

    # Create 25 plots along the organism's echoSMs x-axis
    fig, axs = plt.subplots(5, 5, sharex=True, sharey=True)
    cols = np.linspace(0, shape[1]-1, num=25)

    for col, ax in zip(cols, axs.flat):
        c = int(floor(col))
        # The [::-1] and .invert_ axis calls give the appropriate
        # x and y axes directions in the plots.
        ax.pcolormesh(slice_dim[::-1], row_dim[::-1], d[:,c,:],
                      norm=norm, cmap=cmap)

        ax.set_aspect('equal')
        ax.invert_xaxis()
        ax.invert_yaxis()

        ax.text(0.05, .86, f'{col*1e3*voxel_size[1]:.0f} mm',
                transform=ax.transAxes, fontsize=6, color='white')

    fig.supxlabel('y [mm]')
    fig.supylabel('z [mm]')
    fig.suptitle(title)


def plot_shape_geometric(shapes: list[dict], ax):
    """Plot an echoSMs geometric shape.

    Normally called via [plot_specimen()][echosms.plotting.plot_specimen].

    Parameters
    ----------
    shapes :
        Surface shapes to be plotted
    ax :
        A matplotlib axis.
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

    # Merge the meshes into one
    mesh = trimesh.boolean.union(meshes, check_volume=False)

    # plot the mesh
    p = mesh.vertices
    ax.plot_trisurf(p[:,0], p[:,1], p[:,2], triangles=mesh.faces, alpha=0.8, shade=True,
                    cmap='viridis')

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    # The plot is currently oriented wrong (z-axis increases upwards when it should be 
    # shown increasing downwards, as per the echoSMs coordinate convention). Also want to 
    # have the 'head' of the shape to the left rather than right of the plot.

    # These two options can do some of that, but have undesirable visual effects...
    # ax.invert_zaxis()
    # ax.view_init(elev=30, azim=30, vertical_axis='z')
    scaling = (np.ptp(p[:,0]), np.ptp(p[:,1]), np.ptp(p[:,2]))
    ax.set_box_aspect(scaling)

        
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
