---
hide:
    - toc
---
<!-- Make the window wider so that the schema text displays well -->
<style>
  .md-main__inner.md-grid, 
  .md-grid { 
    max-width: 100% !important; 
  }
  .md-content {
    max-width: none !important;
  }
</style>

# Schema browser

???+ warning

    The schema browser does not show property dependencies, such as when the presence of an optional
    property requires that another property be present (e.g., if `latitude` is present, 
    then `latitude_units` is required). Such dependencies are given in the `dependentRequired`
    sections of the datastore schema [file](https://github.com/ices-tools-dev/echoSMs/blob/main/data_store/schema/v1/anatomical_data_store.json).

{{ datastore_schema_as_html() }}
