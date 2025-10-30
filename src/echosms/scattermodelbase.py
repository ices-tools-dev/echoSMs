"""Base class for scatter model classes."""

import abc
import pandas as pd
import xarray as xr
import numpy as np
from tqdm import tqdm
from .utils import as_dataframe, boundary_type


class ScatterModelBase(abc.ABC):
    """Base class for a class that provides a scattering model.

    All scattering models should inherit from this class, have a name that
    ends with 'Model', and provide initialisation and calculate_ts_single() functions.
    """

    @abc.abstractmethod
    def __init__(self):
        """Initialise.

        Attributes
        ----------
        long_name : str
            The long name of the model.
        short_name : str
            A short version of the model's long name, typically an acronym.
        analytical_type : str
            Whether the model implements an ``exact`` or an ``approximate`` model.
        boundary_types : list[boundary_type]
            The types of boundary conditions that the model provides, e.g., 'fixed rigid',
            'pressure release', 'fluid filled'
        shapes : list[str]
            The target shapes that the model can represent.
        max_ka : float
            An approximate maximum ka value that will result in accurate target strength results.
            Note that ka is often not the only parameter that determines the accuracy of the
            model (e.g., aspect ratio and incident angle can also affect the accuracy).
        no_expand_parameters : list[str]
            The model parameters that are not expanded into Pandas DataFrame columns or
            Xarray DataArray coordinates. They will instead end up as a dict in the DataFrame or
            DataArray `attrs` attribute.
        """
        self.long_name = ''
        self.short_name = ''
        self.analytical_type = ''
        self.boundary_types = []
        self.shapes = []
        self.max_ka = np.nan
        self.no_expand_parameters = []

    def __repr__(self):
        """Return a representation of the object."""
        return 'Name: ' + self.__class__.__name__ + ', vars: ' + str(vars(self))

    def __str__(self):
        """Return user-friendly representation of the object."""
        s = self.__class__.__name__ + " class with attributes of:\n"
        s += '\n'.join(['\t' + str(k) + ' = ' + str(v) for k, v in vars(self).items()])
        return s

    def calculate_ts(self, data, expand=False, inplace=False, multiprocess=False, progress=False):
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
            [mapply](https://github.com/ddelange/mapply). For more
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

        progress : bool
            If `True`, will produce a progress bar while running models

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
                data_df = as_dataframe(data, self.no_expand_parameters)
            case pd.DataFrame():
                data_df = data
            case xr.DataArray():
                data_df = data.to_dataframe().reset_index()
                data_df.attrs = data.attrs
            case _:
                raise ValueError(f'Data type of {type(data)} is not supported'
                                 ' (only dictionaries, Pandas DataFrames and'
                                 ' Xarray DataArrays are).')

        self.validate_parameters(data_df)

        # Get the non-expandable model parameters
        p = data_df.attrs['parameters'] if 'parameters' in data_df.attrs else {}

        # Note: the args argument in the apply call below requires a tuple. data_df.attrs is a
        # dict and the default behaviour is to make a tuple using the dict keys. The trailing comma
        # and parenthesis instead causes the tuple to have one entry of the dict.

        if multiprocess:
            from mapply.mapply import mapply
            ts = mapply(data_df, self.__ts_helper, args=(p,), axis=1, progressbar=progress)
        else:  # this uses just one CPU
            if progress:
                tqdm.pandas(desc=self.short_name, unit=' models',
                            bar_format='{l_bar}{bar} [{n_fmt}/{total_fmt}; {rate_noinv_fmt}]')
                ts = data_df.progress_apply(self.__ts_helper, args=(p,), axis=1)
            else:
                ts = data_df.apply(self.__ts_helper, args=(p,), axis=1)

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
        p |= args[1]  # merge in the dict of non-expandable model parameters
        return self.calculate_ts_single(**p, validate_parameters=False)

    @abc.abstractmethod
    def validate_parameters(self, p: dict | pd.DataFrame | xr.DataArray):
        """Validate the model parameters.

        Parameters
        ----------
        p :
            The model parameters.

        Raises
        ------
        ValueError
            If any of the model parameters are invalid.
        KeyError
            If any required model parameters are not present.
        """

    def _present_and_in(self, p: dict, names: list, valid_values: list):
        """Check that that parameters are present and contains values in `valid_values`.

        Parameters
        ----------
        p :
            Model parameters.
        name :
            Model parameter names to validate.
        valid_values :
            List of valid parameter values.

        Raises
        ------
        ValueError
            If any of the model parameters are invalid.
        KeyError
            If any required model parameters are not present.
        """
        # The values in p can be any iterable or scalar variable. This function has to cope
        # with all of these. A simple way to deal with this is to use np.atleast_1d() to
        # get a consistent type type to work with.

        for name in names:
            if name not in p:
                raise KeyError(f"Models require a '{name}' parameter.")
            if not all(x in valid_values for x in np.unique(np.atleast_1d(p[name]))):
                raise ValueError(f"Model parameter '{name}' contains 1 or more invalid values.")

    def _present_and_positive(self, p: dict, names: list, mask=None):
        """Check that that parameters are present and have a positive value.

        Parameters
        ----------
        p :
            Model parameters
        name :
            Model parameter names to validate.
        mask : np.array | None
            When checking for positive values, only check those where the mask is True.

        Raises
        ------
        ValueError
            If any of the model parameters are invalid.
        KeyError
            If any required model parameters are not present.
        """
        # The values in p can be any iterable or scalar variable. This function has to cope
        # with all of these. A simple way to deal with this is to use np.atleast_1d() to
        # get a consistent type type to work with.

        for name in names:
            if name not in p:
                raise KeyError(f"Models require a '{name}' parameter.")
            if p[name] is None:
                raise ValueError(f"Model parameter '{name}' must not be None.")
            if mask is None:
                mask = np.full(len(p[name]), True)
            if np.min(np.atleast_1d(p[name])[mask]) <= 0:
                raise ValueError(f"Model parameter '{name}' must be greater than zero.")

    @abc.abstractmethod
    def calculate_ts_single(self):
        """Calculate the TS for one parameter set."""
