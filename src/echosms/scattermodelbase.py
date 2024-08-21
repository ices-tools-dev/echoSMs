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
    model_types : list of str
        The types of boundary conditions that the model provides.
    shapes : list of str
        The shapes that the model can represent.
    max_ka : float
        An approximate maximum ka value that will result in accurate target strength results. Note
        that ka is often not the only parameter that determines the accuracy of the model (e.g.,
        aspect ratio and incident angle can also affect the accuracy).

    """

    @abc.abstractmethod
    def __init__(self):
        self.long_name = ''  # the name in words
        self.short_name = ''  # an abbreviation
        self.analytical_type = ''  # 'exact', 'approximate'
        self.model_types = []  # e.g., 'fixed rigid', 'pressure release', 'fluid filled'
        self.shapes = []  # the target shapes that this model can simulate
        # An indication of the maximum ka value that this model provides accurate results for
        self.max_ka = np.nan  # [1]

    def calculate_ts(self, data, multiprocess=False):
        """Calculate the TS for many parameter sets.

        Parameters
        ----------
        data : Pandas DataFrame or Xarray DataArray or dictionary
            If a DataFrame, must contain column names as per the function parameters in the
            calculate_ts_single() function in this class. Each row in the DataFrame will generate
            one TS output. If a DataArray, must contain coordinate names as per the function
            parameters in calculate_ts_single(). The TS will be calculated for all combinations of
            the coordinate variables. If dictionary, it will be converted to a DataFrame first.

        multiprocess : boolean
            Split the ts calculation across CPU cores.

        Returns
        -------
        : Numpy array
            Returns the target strength calculated for all input parameters.

        """
        if isinstance(data, dict):
            data = as_dataframe(data)
        elif isinstance(data, pd.DataFrame):
            pass
        elif isinstance(data, xr.DataArray):
            # For the moment just convert DataArrays into DataFrames
            data = data.to_dataframe().reset_index()
        else:
            raise ValueError(f'Data type of {type(data)} is not supported'
                             ' (only dictionaries, Pandas DataFrames and Xarray DataArrays are).')

        if multiprocess:
            # Using mapply:
            # ts = mapply(data, self.__ts_helper, axis=1)
            # Using swifter
            # ts = df.swifter.apply(self.__ts_helper, axis=1)
            ts = data.apply(self.__ts_helper, axis=1)
        else:  # this uses just one CPU
            # ts = data.apply(self.__ts_helper, args=(model_type,), axis=1)
            ts = data.apply(self.__ts_helper, axis=1)

        return ts.to_numpy()  # TODO - return data type that matches the input data type

    def __ts_helper(self, *args):
        """Convert function arguments and call calculate_ts_single()."""
        p = args[0].to_dict()  # so we can use it for keyword arguments
        return self.calculate_ts_single(**p)

    @abc.abstractmethod
    def calculate_ts_single(self):
        """Calculate the TS for one parameter set."""
        pass
