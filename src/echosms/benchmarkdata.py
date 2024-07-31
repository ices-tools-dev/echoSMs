"""Provide ready access to the benchmark data."""

from pathlib import Path
import pandas as pd


class BenchMarkData:
    """Convenient interface to the benchmark dataset.

    This dataset contains the TS values from Jech et al., 2015.

    Jech, J.M., Horne, J.K., Chu, D., Demer, D.A., Francis, D.T.I., Gorska, N., Jones, B.,
    Lavery, A.C., Stanton, T.K., Macaulay, G.J., Reeder, D.B., Sawada, K., 2015.
    Comparisons among ten models of acoustic backscattering used in aquatic ecosystem research.
    Journal of the Acoustical Society of America 138, 3742–3764. https://doi.org/10.1121/1.4937607
    """

    def __init__(self):

        data_directory = Path(__file__).parent/Path('resources')/Path('BenchMark_Data')

        angle_data_file = data_directory/'Benchmark_Angle_TS.csv'
        freq_data_file = data_directory/'Benchmark_Frequency_TS.csv'

        self.angle_data = pd.read_csv(angle_data_file)
        self.freq_data = pd.read_csv(freq_data_file)

    def dataset_angle(self):
        """Return a Pandas dataframe containing the TS as a function of incidence angle dataset."""
        return self.angle_data

    def dataset_freq(self):
        """Return a Pandas dataframe containing the TS as a function of frequency dataset."""
        return self.freq_data

    # def dataset_angle(self, names):
    #     pass

    # def dataset_freq(self, names):
    #     pass
