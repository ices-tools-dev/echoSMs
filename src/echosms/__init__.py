"""Setup the public API for echoSMs."""

from .utils import wavenumber, wavelength, Neumann, h1, prolate_swf, spherical_jnpp
from .utils import pro_rad1, pro_rad2, pro_ang1, boundary_type, names_from_aphia_id
from .utils import as_dataframe, as_dataarray, as_dict, split_dict, theoretical_Sa
from .utils import datastore_schema

from .conversions import mesh_from_surface, dwbaorganism_from_datastore, krmorganism_from_datastore
from .conversions import volume_from_datastore, surface_from_stl, outline_from_krm, outline_from_dwba
from .conversions import surface_to_outline, outline_to_surface, mesh_from_geometric

from .plotting import plot_specimen, plot_shape_outline, plot_shape_surface
from .plotting import plot_shape_voxels, plot_shape_categorised_voxels

from .dwbautils import create_dwba_spheroid, create_dwba_cylinder, create_dwba_from_xyza, DWBAorganism, DWBAdata

from .benchmarkdata import BenchmarkData
from .jechetaldata import JechEtAlData
from .referencemodels import ReferenceModels
from .esmodel import ESModel
from .mssmodel import MSSModel
from .psmsmodel import PSMSModel
from .dcmmodel import DCMModel
from .ptdwbamodel import PTDWBAModel
from .dwbamodel import DWBAModel
from .kamodel import KAModel
from .krmmodel import KRMModel
from .hpmodel import HPModel
from .bemmodel import BEMModel
from .krmdata import KRMdata, KRMorganism, KRMshape
