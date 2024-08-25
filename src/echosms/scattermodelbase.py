"""Base class for scatter model classes."""

import abc
import numpy as np
from .utils import as_dataframe
import pandas as pd
import xarray as xr


class ScatterModelBase(abc.ABC):
    """Base class for a class that provides a scattering model.

    All scattering models should inherit from this class, have a name that
    ends with 'Model', and provide initialisation and calculate_ts_single() functions.

    Attributes
    ----------
    long_name : str
        The long name of the model.
    short_name : str
        A short version of the model's long name, typically an ancronym.
    analytical_type : str
        Whether the model implements an ``exact`` or an ``approximate`` model.
    boundary_types : list of str
        The types of boundary conditions that the model provides, e.g., 'fixed rigid',
        'pressure release', 'fluid filled'
    shapes : list of str
        The target shapes that the model can represent.
    max_ka : float
        An approximate maximum ka value that will result in accurate target strength results. Note
        that ka is often not the only parameter that determines the accuracy of the model (e.g.,
        aspect ratio and incident angle can also affect the accuracy).

    """

    @abc.abstractmethod
    def __init__(self):
        self.long_name = ''
        self.short_name = ''
        self.analytical_type = ''
        self.boundary_types = []
        self.shapes = []
        self.max_ka = np.nan

    def calculate_ts(self, data, multiprocess=False, result_type=None):
        """Calculate the TS for many parameter sets.

        Parameters
        ----------
        data : Pandas DataFrame, Xarray DataArray or dict
            Requirements for the different input data types are:
            
            - **DataFrame**: column names must match the function parameter names in
              calculate_ts_single(). One TS value will be calculated for each row in the DataFrame.
            - **DataArray**: dimension names must match the function parameter names in
              calculate_ts_single(). TS will be calculated for all combinations of the
              coordinate variables.
            - **dict**: keys must match the function parameters in calculate_ts_single().
              TS will be calculated for all combinations of the dict values.

        multiprocess : boolean
            Split the ts calculation across CPU cores.

        result_type : str or None
            Only applicable if `data` is a dict:

            - `None`: return a list of TS values. This is the default.
            - `expand`: return a DataFrame with a column for each key in the dict. The TS values
               will be in a column named `ts`.

        Returns
        -------
        : list, Series, DataFrame, or DataArray
            Returns the TS. Variable type is determined by the type of `data`:

            - dict input returns a list or DataFrame (if `result_type` is `expand`).
            - DataFrame input returns a Series
            - DataArray input returns the given DataArray with the values set to the TS 

        """
        match data:
            case dict():
                data_df = as_dataframe(data)
            case pd.DataFrame():
                data_df = data
            case xr.DataArray():
                data_df = data.to_dataframe().reset_index()
            case _:
                raise ValueError(f'Data type of {type(data)} is not supported'
                                 ' (only dictionaries, Pandas DataFrames and'
                                 ' Xarray DataArrays are).')

        if multiprocess:
            # Using mapply:
            # ts = mapply(data_df, self.__ts_helper, axis=1)
            # Using swifter
            # ts = data_df.swifter.apply(self.__ts_helper, axis=1)
            ts = data_df.apply(self.__ts_helper, axis=1)
        else:  # this uses just one CPU
            ts = data_df.apply(self.__ts_helper, axis=1)

        match data:
            case dict():
                if result_type == 'expand':
                    data_df['ts'] = ts
                    return data_df
                else:
                    return ts.to_list()
            case pd.DataFrame():
                return ts.rename('ts', inplace=True)
            case xr.DataArray():
                data.values = ts.to_numpy().reshape(data.shape)
                return data
            case _:
                return ts

    def __ts_helper(self, *args):
        """Convert function arguments and call calculate_ts_single()."""
        p = args[0].to_dict()  # so we can use it for keyword arguments
        return self.calculate_ts_single(**p)

    @abc.abstractmethod
    def calculate_ts_single(self):
        """Calculate the TS for one parameter set."""
        pass
