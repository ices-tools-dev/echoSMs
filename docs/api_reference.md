# API reference

This is the API reference for the echoSMs package.

Each type of model is contained in a separate Python class (with name ending in ``Model``), but with common calling signatures across all model classes, as defined in ``ScatterModelBase``. There are also classes to provide ready access to the benchmark models and reference model definitions. There are also utility functions.

## ScatterModelBase

::: echosms.ScatterModelBase

## DCMModel

::: echosms.DCMModel

## DWBA models

There are several models that use the distorted-wave Born approximation, documented below:

### DWBA

::: echosms.DWBAModel
    options:
        heading_level: 4

### PT-DWBA

::: echosms.PTDWBAModel
    options:
        heading_level: 4

### SDWBA

::: echosms.SDWBAModel
    options:
        heading_level: 4

### Utilities

::: echosms.utilsdwba
    options:
        heading_level: 4

## ESModel

::: echosms.ESModel

## HPModel

::: echosms.HPModel

## KAModel

::: echosms.KAModel

## KRMModel

::: echosms.KRMModel

## MSSModel

::: echosms.MSSModel

## PSMSModel

::: echosms.PSMSModel

## ReferenceModels

::: echosms.ReferenceModels

## BenchmarkData

::: echosms.BenchmarkData

## Utilities

::: echosms.utils
