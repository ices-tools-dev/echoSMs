"""Converts a JSON schema to markdown.

Designed to work with the echoSMs datastore schema so only implements
the features used in that.
"""
import json


def parse_property(pname, p, required, defs):
    """Parse a JSON schema property definition."""
    if pname in defs:
        p = defs[pname]

    desc = p.get('description', '')
    type_ = p.get('type', '')

    constraints = []
    if 'enum' in p:
        constraints.append('one of ' + ', '.join([f'``{item}``' for item in p['enum']]))

    for c in ['minimum', 'maximum', 'minItems', 'maxItems']:
        if c in p:
            constraints.append(f'{c}: {p[c]}')

    constraints = '<br>'.join(constraints)

    req = 'yes' if required else 'no'

    if 'const' in p:
        type_ = f'``{p["const"]}``'

    return pname, req, desc, type_, constraints


def parse_object(d, defs):
    """Parse a JSON schema object definition."""
    if 'required' in d:
        prequired = d['required']
    else:
        prequired = []

    rows = []
    for pname, pdata in d['properties'].items():
        name, required, desc, type_, constraints = parse_property(pname, pdata, pname in prequired, defs)

        # This code doesn't dea =l with nested arrays (e.g, array of array of array of int).
        # This doesn't occur often with the echoSMs schema, so bodge it...
        if type_ == 'array':
            name, _, _, type_, item_constraints = parse_property(pname, pdata['items'], prequired, defs)
            if type_ != 'object':
                type_ = 'Array of ' + type_

                # The bodge...
                if type_ == 'Array of array':
                    item_constraints = 'minItems: 1<br>minItems: 1<br>minimum: 0'
                    if name in ['mass_density', 'sound_speed_compressional']:
                        type_ = 'Array of array of array of number'
                    elif name == 'categories':
                        type_ = 'Array of array of array of integer'

                # join constraints from the property and from the array item
                cc = '<br>'.join([constraints, item_constraints])
                rows.append((name, required, desc, type_, cc))
            else:
                rows.append((name, required, desc, 'Array of object', constraints))

                rows.append(('start table','caption', f'Where the ``{name}`` object is:\n\n','',''))
                object_rows = parse_object(pdata['items'], defs)
                rows.extend(object_rows)
        else:
            rows.append((name, required, desc, type_, constraints))

        if 'oneOf' in d:
            first = True
            for option in d['oneOf']:
                of_rows = parse_object(option, defs)
                if first:
                    rows.append(('normal text',
                                 f'and includes these properties as per the value of ``{of_rows[0][0]}``\n'))
                    first = False
                rows.append(('normal text', f'=== "{of_rows[0][3]}"\n'))
                rows.append(('start table', 'indent', '', '', ''))
                rows.extend(of_rows[1:])
                rows.append(('end table', ''))
                # rows.append(('normal text', '\n\n'))

    return rows

def generate(schema_json_file, schema_md_file):
    """Parse a JSON schema and write out a Markdown version."""
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
        indent = ''
        for r in rows:
            if r[0] == 'start table':
                if r[1] == 'indent':
                    indent = '    '

                md.write('\n')

                if r[1] == 'caption':
                    md.write(f'\n{r[2]}\n')

                # Table header row
                md.write(indent + '|Property|Required|Description|Type|Constraints|\n')
                md.write(indent + '|---|---|---|---|---|\n')
            elif r[0] == 'normal text':
                md.write(f'\n{r[1]}\n')
            elif r[0] == 'end table':
                indent = ''
                md.write('\n')
            else:
                md.write(indent + f'|{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[4]}|\n')
