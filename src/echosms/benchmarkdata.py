"""Provide ready access to the bnechmark data."""

from pathlib import Path
import pandas as pd


class BenchMarkData:
    """Doc."""

    def __init__(self):

        data_directory = Path(r'BenchMark_Data')

        angle_data_file = data_directory/'Benchmark_Angle_TS.csv'
        freq_data_file = data_directory/'Benchmark_Frequency_TS.csv'

        self.angle_data = pd.read_csv(angle_data_file)
        self.freq_data = pd.read_csv(freq_data_file)

    def dataset_angle(self):
        return self.angle_data

    def dataset_freq(self):
        return self.freq_data

    # def dataset_angle(self, names):
    #     pass

    # def dataset_freq(self, names):
    #     pass
