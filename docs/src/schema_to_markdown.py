"""Converts a JSON schema to markdown.

Designed to work with the echoSMs datastore schema so only implements
the features used in that.
"""
import json
from pathlib import Path


def parse_property(pname, p, required, defs):

    if pname in defs:
        p = defs[pname]

    if 'description' in p:
        desc = p['description']
    else:
        desc = ''

    if 'type' in p:
        type_ = p['type']
    else:
        type_ = ''

    constraints = []
    if 'enum' in p:
        constraints.append('one of ' + ', '.join([f'``{item}``' for item in p['enum']]))

    for c in ['minimum', 'maximum', 'minItems', 'maxItems']:
        if c in p:
            constraints.append(f'{c}: {p[c]}')

    constraints = '<br>'.join(constraints)

    req = 'yes' if required else 'no'

    if 'const' in p:
        #desc = f'When {pname} is set to ``{p["const"]}``'
        type_ = f'``{p["const"]}``'

    return pname, req, desc, type_, constraints


def parse_object(d, defs):
    if 'required' in d:
        prequired = d['required']
    else:
        prequired = []

    rows = []
    for pname, pdata in d['properties'].items():
        name, required, desc, type_, constraints = parse_property(pname, pdata, pname in prequired, defs)

        if type_ == 'array':
            name, _, _, type_, item_constraints = parse_property(pname, pdata['items'], prequired, defs)
            if type_ != 'object':
                type_ = 'Array of ' + type_
                # join constraints from the property and from the array item
                cc = '<br>'.join([constraints, item_constraints])
                rows.append((name, required, desc, type_, cc))
            else:
                rows.append((name, required, desc, 'Array of object', constraints))

                rows.append(('new table','caption', f'Where the ``{name}`` object is:\n\n','',''))
                object_rows = parse_object(pdata['items'], defs)
                rows.extend(object_rows)
        else:
            rows.append((name, required, desc, type_, constraints))

        if 'oneOf' in d:
            # rows.append(('normal text', 'And one of:\n\n', '', '', ''))
            for option in d['oneOf']:
                of_rows = parse_object(option, defs)

                rows.append(('normal text', 
                             f'And when {of_rows[0][0]} is ``{of_rows[0][3]}`` this includes:'))
                rows.append(('new table', '', '', '', ''))
                rows.extend(of_rows[1:])

    return rows

def generate(schema_json_file, schema_md_file):

    # Load the json schema
    with open(schema_json_file) as f:
        schema = json.load(f)

    # Write out the markdown file
    with open(schema_md_file, 'w') as md:
        md.write(f'# {schema["title"]}\n\n')
        md.write(f'{schema["description"]}\n\n')
        md.write('|Property|Required|Description|Type|Constraints|\n')
        md.write('|---|---|---|---|---|\n')

        defs = schema['$defs']

        rows = parse_object(schema, defs)
        for r in rows:
            if r[0] == 'new table':
                md.write('\n')
                if r[1] == 'caption':
                    md.write(f'\n{r[2]}\n')
                md.write('|Property|Required|Description|Type|Constraints|\n')
                md.write('|---|---|---|---|---|\n')
            elif r[0] == 'normal text':
                md.write(f'\n{r[1]}\n')
            else:
                md.write(f'|{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[4]}|\n')
