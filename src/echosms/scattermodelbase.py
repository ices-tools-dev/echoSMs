"""Base class for scatter model classes."""

import numpy as np


class ScatterModelBaseClass:
    """Base class for a class that provides a scattering model.

    All scattering models should inherit from this class and have a name that
    ends with 'Model'.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.long_name = ''  # the name in words
        self.short_name = ''  # an abbreviation
        self.analytical_type = ''  # 'exact', 'approximate'
        self.model_types = []  # 'fixed rigid', 'pressure release', 'fluid filled'
        self.shapes = []  # the target shapes that this model can simulate
        self.max_frequency = np.nan  # [Hz]
        self.min_frequency = np.nan  # [Hz]
