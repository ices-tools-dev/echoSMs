"""Reference model parameters."""

from pathlib import Path
import sys
import pandas as pd
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
pd.options.mode.copy_on_write = True


class ReferenceModels:
    """Provide access to reference scattering model parameters.

    Reference models are the models and parameters defined in Jech et al. (2015).
    The parameters are stored in a TOML-formatted file in the echoSMs repository
    and this class provides easy access to the data in that file. Additional reference
    models may be defined in the future and added to the TOML file (for example, entries
    have been added for all known calibration sphere sizes).

    Attributes
    ----------
    definitions : dict
        A dict representation of the ``target definitions.toml`` file.

    Raises
    ------
    TOMLDecodeError
        If the ``target definitions.toml`` file is not valid TOML.
    KeyError
        If the ``target definitions.toml`` file has multiple target entries with the same name.

    References
    ----------
    Jech, J.M., Horne, J.K., Chu, D., Demer, D.A., Francis, D.T.I., Gorska, N., Jones, B.,
    Lavery, A.C., Stanton, T.K., Macaulay, G.J., Reeder, D.B., Sawada, K., 2015.
    Comparisons among ten models of acoustic backscattering used in aquatic ecosystem research.
    Journal of the Acoustical Society of America 138, 3742–3764. <https://doi.org/10.1121/1.4937607>
    """

    def __init__(self):
        self.defs_filename = Path(__file__).parent/Path('resources')/Path('target definitions.toml')

        self.definitions = []

        with open(self.defs_filename, 'rb') as f:
            try:
                self.definitions = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise SyntaxError(f'Error while parsing file "{self.defs_filename.name}"') from e

        # Flag duplicate target names
        pda = pd.Series(self.names())
        duplicates = list(pda[pda.duplicated()])
        if duplicates:
            raise KeyError(f'The "{self.defs_filename.name}" file has multiple targets '
                           f'with the same name: '+', '.join(duplicates))

        # Substitute parameters names in the target section by the values of those
        # parameters.
        for t in self.definitions['target']:
            for k, v in t.items():
                try:
                    t[k] = self.definitions['parameters'][v]
                except (KeyError, TypeError):
                    pass

    def names(self):
        """Names of all model definitions.

        Returns
        -------
        : iterable of str
            All model names in the ``target definitions.toml`` file.
        """
        return [n['name'] for n in self.definitions['target']]

    def specification(self, name: str) -> dict:
        """Model definitions for a particular model.

        Parameters
        ----------
        name :
            The name of a model in the ``target definitions.toml`` file.

        Returns
        -------
        :
            The model definitions for the requested model or an empty dict if no model
            with that name.
        """
        s = [t for t in self.definitions['target'] if t['name'] == name]
        if not s:
            return {}

        return s[0]

    def parameters(self, name: str) -> dict:
        """Model parameters for a particular model.

        Model parameters are a subset of the model specification where the metadata items have
        been removed.

        Parameters
        ----------
        name :
            The name of a model in the ``target definitions.toml`` file.

        Returns
        -------
        :
            The model parameters for the requested model or an empty dict if no model with
            that name.

        """
        s = self.specification(name)

        if not s:
            return {}

        # Remove the entries that are not parameters
        p = s.copy()
        for k in ['name', 'shape', 'description', 'source', 'benchmark_model']:
            p.pop(k, None)
        return p
