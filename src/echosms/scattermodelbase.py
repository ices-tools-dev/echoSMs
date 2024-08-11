"""Base class for scatter model classes."""

import abc
import numpy as np


class ScatterModelBaseClass(abc.ABC):
    """Base class for a class that provides a scattering model.

    All scattering models should inherit from this class and have a name that
    ends with 'Model'.
    """

    # pylint: disable=too-many-instance-attributes
    @abc.abstractmethod
    def __init__(self):
        self.long_name = ''  # the name in words
        self.short_name = ''  # an abbreviation
        self.analytical_type = ''  # 'exact', 'approximate'
        self.model_types = []  # 'fixed rigid', 'pressure release', 'fluid filled'
        self.shapes = []  # the target shapes that this model can simulate
        self.max_frequency = np.nan  # [Hz]
        self.min_frequency = np.nan  # [Hz]

    @abc.abstractmethod
    def calculate_ts(self):
        """Calculate the TS for many parameter sets."""
        pass

    @abc.abstractmethod
    def calculate_ts_single(self):
        """Calculate the TS for one parameter set."""
        pass
