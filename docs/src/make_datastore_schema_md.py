"""Make a Material for MkDocs markdown version of the anatomical datastore JSON schema."""

from pathlib import Path

# The package that was used, but it generates poor-looking output
# from json_schema_for_humans.generate import generate_from_filename
# from json_schema_for_humans.generation_configuration import GenerationConfiguration as gc

# Hacky version now used, written solely to do the echoSMs schema, so only supports schema
# structures used by echoSMs
from schema_to_markdown import generate

def on_pre_build(config):
    """Create the schema markdown file.

    This function is called when mkdocs is run and converts the echoSMs anatomical
    data store schema json file into a markdown file and places that in with the
    rest of the markdown files.
    """
    schema_file = Path('data_store')/'schema'/'v1'/'anatomical_data_store.json'
    schema_md_file = Path('docs')/'data_store_schema.md'

    # make doc from the JSON schema using json schema for humans
    # cc = gc(copy_css=True, expand_buttons=True, show_breadcrumbs=False,
    #         link_to_reused_ref=False, show_toc=False, template_name='md',
    #         template_md_options={'badge_as_image': True,
    #                              'show_heading_numbers': False,
    #                              'properties_table_columns':
    #                              ['Property', 'Type', 'Title/Description']})
    # generate_from_filename(schema_file, schema_md_file, config=cc)

    # make doc from the JSON schema using echoSMs own code
    generate(schema_file, schema_md_file)
