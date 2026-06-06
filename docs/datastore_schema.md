# Schema

The dataset contents are specified by a [JSON schema](https://json-schema.org/) file stored in the echoSMs repository. The schema specifies the required attributes, their structure, valid values, etc.

- [View](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/schema/v1/anatomical_data_store.json) the raw JSON schema file. This is the authorative source of the schema.
- [Browse](#schema-browser) an interactive version of the schema.
- [View](https://github.com/ices-tools-dev/echoSMs/tree/main/data_store/resources) an example datastore file.

## Validation

Datastore dataset files can be validated against the schema with:

- online validators (e.g., [here](https://www.jsonschemavalidator.net/), [here](https://jsonschema.dev/), or [here](https://www.liquid-technologies.com/online-json-schema-validator)),
- your own code using a JSON schema validation library (e.g., [jsonschema-rs](https://github.com/Stranger6667/jsonschema/tree/master/crates/jsonschema-py) for Python and [jsonvalidate](https://cran.r-project.org/web/packages/jsonvalidate/vignettes/jsonvalidate.html) for R), or 
- the `validate-toml` command line script that is installed when echoSMs is installed.

It is not necessary to validate your data before submitting it to the datastore, but it will help the uploading happen faster (a validation is done during the uploading process and any dataset format problems will be identified then).

## Schema browser

???+ warning

    The schema browser does not show property dependencies, such as when the presence of an optional
    property requires that another property be present (e.g., if `latitude` is present, 
    then `latitude_units` is required). Such dependencies are given in the `dependentRequired`
    sections of the datastore schema.

{{ datastore_schema_as_html() }}
