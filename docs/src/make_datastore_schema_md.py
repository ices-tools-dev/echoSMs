"""Make a markdown version of the anatomical datastore JSON schema."""

from pathlib import Path
from mkdocs.structure.files import File
from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration as gc


def on_files(files, config):
    """Create the schema markdown file."""
    schema_file = Path('schemas')/'anatomical_data_store'/'v1'/'anatomical_data_store.json'
    schema_md_dir = Path(config["site_dir"])/'schema'
    schema_md_dir.mkdir(exist_ok=True, parents=True)
    schema_md_file = schema_md_dir/'anatomical_data_store_schema.md'

    # make doc from the JSON schema
    cc = gc(copy_css=True, expand_buttons=True, show_breadcrumbs=False,
            link_to_reused_ref=False, show_toc=False, template_name='md',
            template_md_options={'badge_as_image': True,
                                 'show_heading_numbers': False,
                                 'properties_table_columns':
                                 ['Property', 'Type', 'Title/Description']})

    generate_from_filename(schema_file, schema_md_file, config=cc)

    # Add to Files object
    mkdfile = File(path=f'schema/{schema_md_file.name}',
                   src_dir=config["site_dir"],
                   dest_dir=config["site_dir"],
                   use_directory_urls=config["use_directory_urls"])

    files.append(mkdfile)

    # Add the schema page immediately after the 'Anatomical data store' nav
    # link if present
    idx = [link[0] for link in enumerate(config['nav'])
           if list(link[1].keys())[0] == 'Anatomical data store']

    if idx:
        config['nav'].insert(idx[0]+1, {'Schema': mkdfile.src_path})
    else:  # not found, so it goes at the end of the nav section
        config['nav'].append({'Schema': mkdfile.src_path})

    return files
