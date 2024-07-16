"""Reference model parameters."""

from pathlib import Path
import pandas as pd
import tomllib
pd.options.mode.copy_on_write = True


class ReferenceModels:
    """Provide access to reference scattering model parameters."""

    def __init__(self):
        self.defsFilename = Path(r'target definitions.toml')

        with open(self.defsFilename, 'rb') as f:
            self.defs = tomllib.load(f)

        # check that the names parameter is unique across all models

        # Substitute parameters names in the target section by the values of those
        # parameters.
        for t in self.defs['target']:
            for k, v in t.items():
                try:
                    t[k] = self.defs['parameters'][v]
                except (KeyError, TypeError):
                    pass

    def models(self):
        """Return the full set of model definitions."""
        return self.defs

    def model_names(self):
        """Return the names of all model definitions."""
        return [n['name'] for n in self.defs['target']]

    def get_model_parameters(self, name):
        """Get the model defintions for a particular model."""
        models = pd.DataFrame(self.defs['target'])
        m = models.query('name == @name')
        if len(m) == 1:
            m.dropna(axis=1, how='all', inplace=True)
            return m.iloc[0].to_dict()
        else:
            return None
