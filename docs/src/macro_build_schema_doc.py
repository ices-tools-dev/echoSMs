from pathlib import Path
from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration as gc

def define_env(env):
    # Call this in a markdown document via:
    # {{ datastore_schema_as_html() }}
    @env.macro
    def datastore_schema_as_html():
        schema_file = Path('data_store')/'schema'/'v1'/'anatomical_data_store.json'
        html_file = Path('site')/'schema'/'schema_doc.html'
        html_file.parent.mkdir(parents=True, exist_ok=True)

        # make doc from the JSON schema using json schema for humans
        cc = gc(expand_buttons=True,
                link_to_reused_ref=False,
                collapse_long_descriptions=True,
                description_is_markdown=True,
                with_footer=False,
                template_name='js',
                )

        generate_from_filename(schema_file, html_file, config=cc)

        return '<iframe src="./schema/schema_doc.html" width=100% height=1000px style="border-width: 0"></iframe>'
