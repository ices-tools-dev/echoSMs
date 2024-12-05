"""Provide ready access to the benchmark data."""

from pathlib import Path
import pandas as pd


class BenchmarkData:
    """Convenient interface to the benchmark dataset.

    This dataset contains the TS results from Jech et al. (2015).

    Attributes
    ----------
    angle_dataset : Pandas DataFrame
        The angle dataset from the benchmark model runs.

    freq_dataset : Pandas DataFrame
        The frequency dataset from the benchmark model runs.

    Notes
    -----
    The column names in the source benchmark files have been changed to be the same as those used
    in the [referencemodels] model definitions.

    References
    ----------
    Jech, J.M., Horne, J.K., Chu, D., Demer, D.A., Francis, D.T.I., Gorska, N., Jones, B.,
    Lavery, A.C., Stanton, T.K., Macaulay, G.J., Reeder, D.B., Sawada, K., 2015.
    Comparisons among ten models of acoustic backscattering used in aquatic ecosystem research.
    Journal of the Acoustical Society of America 138, 3742-3764. <https://doi.org/10.1121/1.4937607>
    """
    f_rename = {'Sphere_WeaklyScattering': 'weakly scattering sphere',
                'Sphere_Rigid': 'fixed rigid sphere',
                'Sphere_PressureRelease': 'pressure release sphere',
                'Sphere_Gas': 'gas filled sphere',
                'ShellSphere_PressureRelease': 'spherical fluid shell with pressure release interior',
                'ShellSphere_Gas': 'spherical fluid shell with gas interior',
                'ShellSphere_WeaklyScattering': 'spherical fluid shell with weakly scattering interior',
                'Cylinder_Rigid': 'fixed rigid finite cylinder',
                'Cylinder_PressureRelease': 'pressure release finite cylinder',
                'Cylinder_Gas': 'gas filled finite cylinder',
                'Cylinder_WeaklyScattering': 'weakly scattering finite cylinder',
                'ProlateSpheroid_Rigid': 'fixed rigid prolate spheroid',
                'ProlateSpheroid_PressureRelease': 'pressure release prolate spheroid',
                'ProlateSpheroid_Gas': 'gas filled prolate spheroid',
                'ProlateSpheroid_WeaklyScattering': 'weakly scattering prolate spheroid',
                'Frequency_kHz': 'frequency (kHz)'}

    a_rename = {'Cylinder_Rigid': 'fixed rigid finite cylinder',
                'Cylinder_PressureRelease': 'pressure release finite cylinder',
                'Cylinder_Gas': 'gas filled finite cylinder',
                'Cylinder_WeaklyScattering': 'weakly scattering finite cylinder',
                'ProlateSpheroid_Rigid': 'fixed rigid prolate spheroid',
                'ProlateSpheroid_PressureRelease': 'pressure release prolate spheroid',
                'ProlateSpheroid_Gas': 'gas filled prolate spheroid',
                'ProlateSpheroid_WeaklyScattering': 'weakly scattering prolate spheroid',
                'Angle_deg': 'angle (deg)'}

    def __init__(self):

        data_directory = Path(__file__).parent/Path('resources')/Path('BenchMark_Data')

        angle_data_file = data_directory/'Benchmark_Angle_TS.csv'
        freq_data_file = data_directory/'Benchmark_Frequency_TS.csv'

        self.angle_dataset = pd.read_csv(angle_data_file)
        self.freq_dataset = pd.read_csv(freq_data_file)

        # Change the column names to match the reference model names used in ReferenceModels
        self.angle_dataset.rename(columns=BenchmarkData.a_rename, inplace=True)
        self.freq_dataset.rename(columns=BenchmarkData.f_rename, inplace=True)
