"""Provide ready access to the model results in the Jech et al paper."""

from pathlib import Path
import pandas as pd


class JechEtAlData:
    """Simple access to all model results in Jech et al (2015).

    Attributes
    ----------
    data : dict[pd.DataFrame]
        One entry in the dict for each model results file.
    data_directory : Path
        The directory containing the model results files.

    References
    ----------
    Jech, J.M., Horne, J.K., Chu, D., Demer, D.A., Francis, D.T.I., Gorska, N., Jones, B.,
    Lavery, A.C., Stanton, T.K., Macaulay, G.J., Reeder, D.B., Sawada, K., 2015.
    Comparisons among ten models of acoustic backscattering used in aquatic ecosystem research.
    Journal of the Acoustical Society of America 138, 3742-3764. <https://doi.org/10.1121/1.4937607>
    """

    def __init__(self):
        self.data_directory = Path(__file__).parent/Path('resources')/Path('Jechetal_allmodels')
        self.data = {f.stem: pd.read_csv(f) for f in self.data_directory.glob('*.csv')}
