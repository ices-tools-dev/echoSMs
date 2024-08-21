"""Reference model parameters."""

from pathlib import Path
import tomllib
import pandas as pd
pd.options.mode.copy_on_write = True


class ReferenceModels:
    """Provide access to reference scattering model parameters.

    Attributes
    ----------
    definitions : dict
        A dict representation of the ``target definitions.toml`` file.

    Raises
    ------
    KeyError
        If the ``target definitions.toml`` file has multiple target entries with the same name.
    """

    def __init__(self):
        self.defs_filename = Path(__file__).parent/Path('resources')/Path('target definitions.toml')

        self.definitions = []

        with open(self.defs_filename, 'rb') as f:
            self.definitions = tomllib.load(f)

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

    def specification(self, name):
        """Model defintions for a particular model.

        Parameters
        ----------
        name : str
            The name of a model in the ``target definitions.toml`` file.

        Returns
        -------
        : dict
            The model definitions for the requested model or ``None`` if no model with that name.
        """
        # Convert to a DataFrame, find the row with name of 'name', remove columns with nan in
        # them and return the row as a dictionary.
        models = pd.DataFrame(self.definitions['target'])
        m = models.loc[models['name'] == name]
        if len(m) == 1:
            m.dropna(axis=1, how='all', inplace=True)
            return m.iloc[0].to_dict()

        return None

    def parameters(self, name):
        """Model parameters for a particular model.

        Model parameters are a subset of the model specification where the metadata items have
        been removed.

        Parameters
        ----------
        name : str
            The name of a model in the ``target definitions.toml`` file.

        Returns
        -------
        : dict
            The model parameters for the requested model or ``None`` if no model with that name.

        """
        s = self.specification(name)

        if s is None:
            return None

        # Remove the entries that are not parameters
        p = s
        del p['name']
        del p['shape']
        del p['description']
        del p['source']
        return p
