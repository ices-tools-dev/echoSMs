from pathlib import Path
from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration as gc

# This is a temporary solution until Zensical implements modules and/or there is a plugin
# for including JSON schema into Zensical docs.

def define_env(env):
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

        return f'<iframe src="../{html_filename}" width=100% height=1000px style="border-width: 0"></iframe>'
