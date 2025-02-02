"""Provide ready access to the benchmark data."""

from pathlib import Path
import pandas as pd


class BenchmarkData:
    """Convenient interface to the benchmark dataset.

    This dataset contains the benchmark TS results from Jech et al. (2015).

    Notes
    -----
    The column names in the source benchmark files have been changed to be the same as those used
    in the [ReferenceModels][echosms.ReferenceModels] model definitions.

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
                'ShellSphere_PressureRelease':
                    'spherical fluid shell with pressure release interior',
                'ShellSphere_Gas': 'spherical fluid shell with gas interior',
                'ShellSphere_WeaklyScattering':
                    'spherical fluid shell with weakly scattering interior',
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

        self.freq_dataset['frequency (kHz)'] *= 1e3  # want Hz not kHz

        # Remove units from the column names (we have the echoSMs units convention instead)
        self.freq_dataset.rename(columns={'frequency (kHz)': 'frequency'}, inplace=True)
        self.angle_dataset.rename(columns={'angle (deg)': 'angle'}, inplace=True)

        self.angle_dataset.set_index('angle', inplace=True)
        self.freq_dataset.set_index('frequency', inplace=True)

    def angle_names(self) -> list:
        """Provide the model names for the angle benchmark data.

        Returns
        -------
        :
            List of model names.

        """
        return self.angle_dataset.columns.values.tolist()

    def freq_names(self) -> list:
        """Provide the model names for the frequency benchmark data.

        Returns
        -------
        :
            List of model names.
        """
        return self.freq_dataset.columns.values.tolist()

    def freq_data(self, name: str) -> tuple:
        """Provide the benchmark TS values verses frequency for the `name` model.

        Parameters
        ----------
        name :
            The name of the benchmark model (available from `freq_names()`).

        Returns
        -------
        :
            Tuple containing the frequencies (Hz) and TS (dB) for the requested benchmark model.
        """
        if name not in self.freq_names():
            raise ValueError(f'The requested model ({name}) '
                             'is not in the frequency benchmark dataset.')
        return (self.freq_dataset.index.values, self.freq_dataset[name].values)

    def angle_data(self, name: str) -> tuple:
        """Provide the benchmark TS values verses angle for the `name` model.

        Parameters
        ----------
        name :
            The name of the benchmark model (available from `angle_names()`).

        Returns
        -------
        :
            Tuple containing the angles (°) and TS (dB) for the requested benchmark model.
        """
        if name not in self.angle_names():
            raise ValueError(f'The requested model ({name}) is not in the angle benchmark dataset.')
        return (self.angle_dataset.index.values, self.angle_dataset[name].values)

    def angle_as_dataframe(self) -> pd.DataFrame:
        """Provide the angle benchmark dataset as a Pandas DataFrame.

        Returns
        -------
        :
            Dataframe containing the benchmark data.
        """
        return self.angle_dataset

    def freq_as_dataframe(self) -> pd.DataFrame:
        """Provide the frequency benchmark dataset as a Pandas DataFrame.

        Returns
        -------
        :
            Dataframe containing the benchmark data.
        """
        return self.freq_dataset
