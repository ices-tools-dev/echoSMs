"""Base class for scatter model classes."""

import abc
import pandas as pd
import xarray as xr
import numpy as np
from .utils import as_dataframe


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
    boundary_types : list[str]
        The types of boundary conditions that the model provides, e.g., 'fixed rigid',
        'pressure release', 'fluid filled'
    shapes : list[str]
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

    def __repr__(self):
        """Return a representation of the object."""
        return 'Name: ' + self.__class__.__name__ + ', vars: ' + str(vars(self))

    def __str__(self):
        """Return user-friedly representation of the object."""
        s = self.__class__.__name__ + " class with attributes of:\n"
        s += '\n'.join(['\t' + str(k) + ' = ' + str(v) for k, v in vars(self).items()])
        return s

    def calculate_ts(self, data, expand=False, inplace=False, multiprocess=False):
        """Calculate the target strength (TS) for many parameters.

        Parameters
        ----------
        data : Pandas DataFrame, Xarray DataArray or dict
            Requirements for the different input data types are:

            - **DataFrame**: column names must match the function parameter names in
              calculate_ts_single(). One TS value will be calculated for each row in the DataFrame.
            - **DataArray**: dimension names must match the function parameter names in
              calculate_ts_single(). TS values will be calculated for all combinations of the
              coordinate variables.
            - **dict**: keys must match the function parameters in calculate_ts_single().
              TS values will be calculated for all combinations of the dict values.

        multiprocess : bool
            Split the ts calculation across CPU cores. Multiprocessing is currently provided by
            [mapply](https://github.com/ddelange/mapply) with little customisation. For more
            sophisticated uses it may be preferred to use a multiprocessing package of your choice
            directly on the `calculate_ts_single()` method. See the code in this method
            (`calculate_ts()`) for an example.

        expand : bool
            Only applicable if `data` is a dict. If `True`, will use
            [`as_dataframe()`][echosms.utils.as_dataframe]
            to expand the dict into a DataFrame with one column per dict key
            and return that, adding a column named `ts` for the results.

        inplace : bool
            Only applicable if `data` is a DataFrame. If `True`, the results
            will be added to the input DataFrame in a column named `ts`. If a `ts` column
            already exists, it is overwritten.

        Returns
        -------
        : None, list[float], Series, or DataFrame
            The return type and value are determined by the type of the input variable (`data`) and
            the `expand` and `inplace` parameters:

            - dict input and `expand=False` returns a list of floats.
            - dict input and `expand=True` returns a DataFrame.
            - DataFrame input and `inplace=False` returns a Series.
            - DataFrame input and `inplace=True` modifies `data` and returns `None`.
            - DataArray input always modifies `data` and returns `None`.

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
            from mapply.mapply import mapply
            ts = mapply(data_df, self.__ts_helper, axis=1)
        else:  # this uses just one CPU
            ts = data_df.apply(self.__ts_helper, axis=1)

        match data:
            case dict() if expand:
                data_df['ts'] = ts
                return data_df
            case dict():
                return ts.to_list()
            case pd.DataFrame() if inplace:
                data_df['ts'] = ts
                return None
            case pd.DataFrame():
                return ts.rename('ts', inplace=True)
            case xr.DataArray():
                data.values = ts.to_numpy().reshape(data.shape)
                return None
            case _:
                raise AssertionError('This code should never be reached - unsupported input data '
                                     f'type of {type(data)}.')

    def __ts_helper(self, *args):
        """Convert function arguments and call calculate_ts_single()."""
        p = args[0].to_dict()  # so we can use it for keyword arguments
        return self.calculate_ts_single(**p)

    @abc.abstractmethod
    def calculate_ts_single(self):
        """Calculate the TS for one parameter set."""
