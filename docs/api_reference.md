# API reference

This is the API reference for the echoSMs package.

Each type of model is contained in a separate Python class (with name ending in ``Model``), but with common calling signatures across all model classes, as defined in ``ScatterModelBase``. There are also classes to provide ready access to the benchmark models and reference model definitions. There are also utility functions.


## ScatterModelBase
::: echosms.ScatterModelBase

## MSSModel
::: echosms.MSSModel
    options:
        filters:
        - "!^_"

## PSMSModel
::: echosms.PSMSModel
 
## DCMModel
::: echosms.DCMModel

## ReferenceModels
Reference models are the models and parameters defined in the Jech et al, 2015 paper. The parameters are stored in a TOML-formatted file in the echoSMs repository and the ``ReferenceModels`` class provides easy access to the data in that file. 

Additional reference models may be defined in the future and can be added to the TOML file.

::: echosms.ReferenceModels


## BenchmarkData
::: echosms.BenchmarkData
 
 
## Utilities
::: echosms.utils
