# API reference

This is the API reference for the echoSMs package.

Each type of model is contained in a separate Python class (with name ending in ``Model``), but with common calling signatures across all model classes, as defined in ``ScatterModelBase``. There are also classes to provide ready access to the benchmark models and reference model definitions. There are also utility functions.

## ::: echosms.ScatterModelBase

## ::: echosms.DCMModel

## DWBA models

There are several models that use the distorted-wave Born approximation, documented below. There are also some functions to
make cylinder and spheroid shapes for use in the DWBA models.

::: echosms.DWBAModel
::: echosms.PTDWBAModel
::: echosms.dwbautils

## ::: echosms.ESModel

## ::: echosms.HPModel

## ::: echosms.KAModel

## KRM model & utilities

::: echosms.KRMModel
::: echosms.KRMdata
::: echosms.KRMorganism
::: echosms.KRMshape

## ::: echosms.MSSModel

## ::: echosms.PSMSModel

## Utilities

::: echosms.BenchmarkData
::: echosms.ReferenceModels
::: echosms.JechEtAlData
::: echosms.utils
    options:
        members_order: source
::: echosms.shape_conversions

## Anatomical datastore

::: echosms.utils_datastore
