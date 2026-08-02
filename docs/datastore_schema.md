# Schema

The dataset contents are specified by a [JSON schema](https://json-schema.org/) file stored in the echoSMs repository. The schema specifies the required attributes, their structure, valid values, etc.

- [View](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/schema/v1/anatomical_data_store.json) the raw JSON schema file. This is the authoritative source of the schema.
- [Browse](datastore_schema_browser.md#schema-browser) an interactive version of the schema.
- View an example datastore file (in [TOML](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/resources/example_metadata%20A.toml) format and [JSON](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/resources/example_metadata%20A.json) format).

## Validation

Datastore dataset files can be validated against the schema with:

- the `validate-toml` command line script that is installed when echoSMs is installed.
- online validators (e.g., [jsonschema](https://jsonschema.dygalo.dev), [JSON Schema Validator](https://www.jsonschemavalidator.net/),
  [JSONSchema.dev](https://jsonschema.dev/),
  or [JSON Validator](https://www.liquid-technologies.com/online-json-schema-validator)),
- your own code using a JSON schema validation library
  (e.g., [jsonschema-rs](https://github.com/Stranger6667/jsonschema/tree/master/crates/jsonschema-py)
  for Python and [jsonvalidate](https://cran.r-project.org/web/packages/jsonvalidate/vignettes/jsonvalidate.html) for R), or

It is not necessary to validate your data before submitting it to the datastore, but it will help the uploading happen faster (a validation is done during the uploading process and any dataset format problems will be identified then).

???+ Note
    The JSON schema validation libraries expect either a Python data structure or a JSON file - none
    work directly with TOML files. The `validate-toml` script has an option to convert a TOML
    dataset into a JSON file (use the `-j` option) or use a TOML-reading library to read into
    memory and then validate or write out as JSON.
