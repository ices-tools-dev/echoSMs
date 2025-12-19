"""Utilities for working with the echoSMs anatomical datastore."""
import trimesh
import numpy as np
from pathlib import Path
import numpy.typing as npt
import matplotlib.pyplot as plt
from matplotlib import colors, colormaps
from math import floor
from .utils import boundary_type as bt

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
    idx = [i for i, s in enumerate(shapes) if s['anatomical_type'] == 'body']
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
                     anatomical_type: str = 'body',
                     boundary: str = 'pressure-release') -> dict:
    """Create an echoSMs surface shape from an .stl file.

    Parameters
    ----------
    stl_file :
        An .stl file
    dim_scale :
        Scaling factor applied to the node positions. Use to convert from one
        length unit to another (e.g., 1e-3 will convert from mm to m).
    anatomical_type :
        The anatomical type for this shape, as per the echoSMs datastore schema.
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
    return {'anatomical_type': anatomical_type, 'boundary': boundary,
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
                     anatomical_type: str = "body",
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
    anatomical_type :
        The anatomical type for this shape, as per the echoSMs datastore schema.
    boundary :
        The boundary type for this shape, as per the echoSMs datastore schema.

    Returns
    -------
     An echoSMs outline shape representation.
    """
    y = np.zeros(len(x))
    height = np.array(height_u) - np.array(height_l)
    z = -(np.array(height_l) + height / 2.0)

    return {'anatomical_type': anatomical_type, 'boundary': boundary,
            'shape_units': 'm',
            'x': np.array(x).tolist(),
            'y': y.tolist(),
            'z': z.tolist(),
            'height': height.tolist(),
            'width': np.array(width).tolist()}


def outline_from_dwba(x, z, radius, anatomical_type: str = "body",
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
    anatomical_type :
        The anatomical type for this shape, as per the echoSMs datastore schema.
    boundary :
        The boundary type for this shape, as per the echoSMs datastore schema.

    Returns
    -------
     An echoSMs outline shape representation.

    """
    return {'anatomical_type': anatomical_type,
            'boundary': boundary,
            'shape_units': 'm',
            'x': np.array(x).tolist(),
            'y': np.zeros(len(x)).tolist(),
            'z': (-np.array(z)).tolist(),
            'height': (2*np.array(radius)).tolist(),
            'width': (2*np.array(radius)).tolist()}


def plot_specimen(specimen: dict, dataset_id: str='', title: str='',
                  savefile: str|None=None, dpi: float=150) -> None:
    """Plot the specimen shape.

    Produces a relevant plot for all echoSMs anatomical datastore shape types.

    Parameters
    ----------
    specimen :
        Specimen data as per the echoSMs anatomical datastore schema.
    dataset_id :
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
    t = title if title else dataset_id + ' ' + specimen['specimen_id']

    match specimen['shape_type']:
        case 'outline':
            fig, axs = plt.subplots(2, 1, sharex=True, layout='tight')
            fig.set_tight_layout({'h_pad': 1, 'w_pad': 1})
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

    Normally called via [plot_specimen()][echosms.utils_datastore.plot_specimen].

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


def plot_shape_surface(shapes, ax):
    """Plot an echoSMs anatomical surface shape.

    Normally called via [plot_specimen()][echosms.utils_datastore.plot_specimen].

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


def plot_shape_voxels(s, title=''):
    """Plot the specimen's voxels.

    Normally called via [plot_specimen()][echosms.utils_datastore.plot_specimen].

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


def plot_shape_categorised_voxels(s, title=''):
    """Plot the specimen's categorised voxels.

    Normally called via [plot_specimen()][echosms.utils_datastore.plot_specimen].

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
