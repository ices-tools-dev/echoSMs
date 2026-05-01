# Schema

The dataset contents are specified by a [JSON schema](https://json-schema.org/) file stored in the echoSMs repository. The schema specifies the required attributes, their structure, valid values, etc.

- [View](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/schema/v1/anatomical_data_store.json) the raw JSON schema file. This is the authorative source of the schema.
- [Browse](#schema-browser) an interactive version of the schema. This version may not show all the details - look at the raw schema file for full details.
- [View](https://github.com/ices-tools-dev/echoSMs/tree/main/data_store/resources) an example datastore file.

Datastore dataset files can be validated against the schema using online validators (e.g., [here](https://www.jsonschemavalidator.net/), [here](https://jsonschema.dev/), or [here](https://www.liquid-technologies.com/online-json-schema-validator)), or within your own code using a JSON schema validation library (e.g., [jsonschema-rs](https://github.com/Stranger6667/jsonschema/tree/master/crates/jsonschema-py) for Python and [jsonvalidate](https://cran.r-project.org/web/packages/jsonvalidate/vignettes/jsonvalidate.html) for R).

It is not necessary to validate your data before submitting it to the datastore, but it will help the uploading happen faster (a validation is done during the uploading process and any dataset format problems will be identified then).

## Schema browser

<iframe src="../schema_doc.html" width=100% height=1000px style="border-width: 0"></iframe>
