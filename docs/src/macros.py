import sys
import importlib.util
from pathlib import Path
from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration as gc

# A convoluted method to import just the constants.py file from the echoSMs
# source code directory. This is mainly so that when this code runs as a github
# actions (when an installed echoSMs package is not available), it can get access
# to a constant in the constants.py file without having to install all of the
# echoSMs dependencies (as it would if it implicitly imported the __init__.py file in
# the echoSMs module).

file_path = Path(__file__).parent.parent.parent/'src'/'echosms'/'constants.py'
module_name = file_path.stem
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

# This is a temporary solution until Zensical implements modules and/or there is a plugin
# for including JSON schema into Zensical docs.

def define_env(env):
    env.variables['datastore_uri'] = module.DATASTORE_URI

    @env.macro
    def ds_uri(p):
        return module.DATASTORE_URI + p

    # Call this in a markdown document via:
    # {{ datastore_schema_as_html() }}
    @env.macro
    def datastore_schema_as_html():
        schema_file = Path('data_store')/'schema'/'v1'/'anatomical_data_store.json'
        html_filename = 'schema/schema_doc.html'

        html_file = Path(env.conf['site_dir'])/html_filename
        html_file.parent.mkdir(parents=True, exist_ok=True)

        generate_from_filename(schema_file, html_file,
            config=gc(
                expand_buttons=True,
                link_to_reused_ref=False,
                collapse_long_descriptions=False,
                description_is_markdown=True,
                with_footer=False,
                template_name='js',
                show_breadcrumbs=False,  # just clutters the 'js' template output
                )
            )
        # The large height is enough to show all of the schema when all entries are expanded
        # Having a height larger than the expanded contents means that a separate scrollbar
        # is not generated for the iframe (which is confusing)
        return (
            f'<iframe src="../{html_filename}" '
            'width="100%" height="30000px" style="border-width: 0"></iframe>'
        )
