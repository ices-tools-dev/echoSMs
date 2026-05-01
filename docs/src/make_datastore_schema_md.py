"""Make a Material for MkDocs markdown version of the anatomical datastore JSON schema."""

from pathlib import Path
from mkdocs.structure.files import File

# The package that was used, but it generates poor-looking output
from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration as gc

def on_files(files, config):
    """Create the schema markdown file.

    This function is called when mkdocs is run and converts the echoSMs anatomical
    data store schema json file into an html file that is referenced into an
    existing markdown file.
    """
    schema_file = Path('data_store')/'schema'/'v1'/'anatomical_data_store.json'
    formatted_schema_file = Path(config["site_dir"])/'schema_doc.html'

    # make doc from the JSON schema using json schema for humans
    cc = gc(expand_buttons=True,
            link_to_reused_ref=False,
            collapse_long_descriptions=True,
            description_is_markdown=True,
            with_footer=False,
            template_name='js',
            )
    
    generate_from_filename(schema_file, formatted_schema_file, config=cc)

    # Add to Files object
    mkdfile = File(path=formatted_schema_file.name,
                   src_dir=config["site_dir"],
                   dest_dir=config["site_dir"],
                   use_directory_urls=config["use_directory_urls"])

    files.append(mkdfile)

    return files
