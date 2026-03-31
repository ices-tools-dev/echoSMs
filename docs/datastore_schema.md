# Schema

The dataset contents are specified by a [JSON schema](https://json-schema.org/) file stored in the echoSMs. The schema documents the required attributes, their structure, valid values, etc. The schema is a very technical document and is perhaps more easily understood via the interative online version.

- [Browse](https://json-schema.app/view/%23?url=https%3A%2F%2Fraw.githubusercontent.com%2Fices-tools-dev%2FechoSMs%2Frefs%2Fheads%2Fmain%2Fdata_store%2Fschema%2Fv1%2Fanatomical_data_store.json) the schema online.
- [View](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/schema/v1/anatomical_data_store.json) the raw JSON schema file. This is the authorative source of the schema.
- [View](https://github.com/ices-tools-dev/echoSMs/tree/main/data_store/resources) an example datastore file.

Datastore dataset files can be validated against the schema using online validators (e.g., [here](https://www.jsonschemavalidator.net/), [here](https://jsonschema.dev/), or [here](https://www.liquid-technologies.com/online-json-schema-validator)), or within your own code using a JSON schema validation library (e.g., [jsonschema-rs](https://github.com/Stranger6667/jsonschema/tree/master/crates/jsonschema-py) for Python and [jsonvalidate](https://cran.r-project.org/web/packages/jsonvalidate/vignettes/jsonvalidate.html) for R).

It is not necessary to validate your data before submitting it to the datastore, but it will help the uploading happen faster (a validation is done during the uploading process and any dataset format problems will be identified then).
