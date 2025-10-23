"""Make a Material for MkDocs markdown version of the anatomical datastore JSON schema."""

from pathlib import Path
from mkdocs.structure.files import File

# The package that was used, but it generates poor-looking output
# from json_schema_for_humans.generate import generate_from_filename
# from json_schema_for_humans.generation_configuration import GenerationConfiguration as gc

# Hacky version now used, written solely to do the echoSMs schema, so only supports schema
# structures used by echoSMs
from schema_to_markdown import generate

def on_files(files, config):
    """Create the schema markdown file.

    This function is called when mkdocs is run and converts the echoSMs anatomical
    data store schema json file into a markdown file, then adds that to the echoSMs
    documentation that mkdocs generates.
    """
    schema_file = Path('data_store')/'schema'/'v1'/'anatomical_data_store.json'
    schema_md_dir = Path(config["site_dir"])/'schema'
    schema_md_dir.mkdir(exist_ok=True, parents=True)
    schema_md_file = schema_md_dir/'data_store_schema.md'

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

    # Add to Files object
    mkdfile = File(path=f'schema/{schema_md_file.name}',
                   src_dir=config["site_dir"],
                   dest_dir=config["site_dir"],
                   use_directory_urls=config["use_directory_urls"])

    files.append(mkdfile)

    # Add the schema page in the 'Anatomical data store' section
    for s in config['nav']:
        if 'Anatomical data store' in s:
            s['Anatomical data store'].insert(2, ({'Schema': mkdfile.src_path}))

    return files
