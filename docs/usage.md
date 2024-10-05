# Using echoSMs

EchoSMs is (currently) a Python package that implements acoustic scattering models. Each different model is a separate Python class in the echoSMs package. They all inherit from a common base class that defines a common calling convention for all models.

## Installation

EchoSMs is available on [PyPi](https://pypi.org) as [`echosms`](https://pypi.org/project/echosms/). Install it with:

    pip install echosms

Some of the models in echoSMs use spheroidal wave functions. A high-accuracy implementation of these is available in the Python package [`spheroidalwavefunctions`](https://pypi.org/project/spheroidalwavefunctions/), as the versions provided by [scipy](https://docs.scipy.org/doc/scipy/reference/special.html#spheroidal-wave-functions) are insufficient. This should be installed automatically when you install echosms, but note that `spheroidalwavefunctions` is currently only available for Linux and Windows on x86_64 CPU architectures (create an [issue](https://github.com/ices-tools-dev/echoSMs/issues) if you want it on a system that is not currently supported).

## Version

The installed version of echosms can be printed with this code:

    import importlib
    print(importlib.metadata.version('echosms'))

## Model overview

Currently, the following models are available in echoSMs:

|Model type|Python class name|Description|
|----------|----------|-----------|
|Modal series solution|MSSModel|Spheres with various boundary conditions, including shells|
|Deformed cylinder model|DCMModel|Truncated cylinders with various boundary conditions|
|Prolate spheroidal modal series|PSMSModel|Prolate spheroids with various boundary conditions|
|Elastic sphere|ESModel|Elastic spheres, such as echosounder calibration spheres|
|Phase-tracking distorted wave Born approximation|PTDWBAModel|Weakly scattering objects of any shape with inhomogeneous interiors|

Future models will include more types of DWBA models, the Kirchhoff-type models, and potentially finite element and boundary element models.

## Running a model

Each echoSMs model expects input parameters that define the particulars of the model (e.g., size, shape, material properties, etc). These can be provided in three ways:

- A Python **dictionary** with an entry for each parameter,
- A Pandas **DataFrame** with columns for each required parameter and a row for each model run to be done,
- An Xarray **DataArray** with as many dimensions as required parameters. The parameter values are given by the DataArray coordinate variables.

To use a model, you need to know what parameters it requires. These are documented in the `calculate_ts_single` function that each model has (refer to the echoSMS [API reference](https://ices-tools-dev.github.io/echoSMs/api_reference) for details). For example, the MSSModel, when simulating the scattering from a pressure release sphere, needs the following parameters:

|Parameter name|Description|
|--------------|-----------|
|medium_c|Sound speed in the fluid medium surrounding the target [m/s]|
|medium_rho|Density of the fluid medium surrounding the target [kg/m³]|
|a|Radius of the spherical target [m]|
|f|Frequency to calculate the scattering at [Hz]|
|theta|Pitch angle to calculate the scattering at [°]. An angle of 0 is head on, 90 is dorsal, and 180 is tail on|
|boundary_type|The boundary type. Supported types are `fixed rigid`, `pressure release`, and `fluid filled`|

The simplest way to provide these to the model is a dictionary:

```py
    p = {'medium_rho': 1026.8,
         'medium_c': 1477.4,
         'a': 0.01, 
         'boundary_type': 'pressure release',
         'f': 38000,
         'theta': 90}
```

An instance of the model can then be created and the `calculate_ts` function called with these parameters:

```py
    from echosms import MSSModel
    model = MSSModel()
    model.calculate_ts(p)
```

This will return one TS value corresponding to the parameters given. If you want to run the model for a range of parameters, the relevant dictionary items can contain multiple values:

```py hl_lines="7"
        import numpy as np
        p = {'medium_rho': 1026.8,
             'medium_c': 1477.4,
             'a': 0.01,
             'theta': 90,
             'boundary_type': 'pressure release',
             'f', np.arange(10, 100, 1)*1000}
        model.calculate_ts(p)
```

It is also fine to have multiple items with multiple values:

```py hl_lines="3 4 6"
        p = {'medium_rho': 1026.8,
             'medium_c': 1477.4,
             'a': np.arange(0.01, 0.02, 0.001),
             'theta': [0, 30, 60, 90],
             'boundary_type': 'pressure release',
             'f': np.arange(10, 100, 1)*1000}
        model.calculate_ts(p)
```

The TS will be calculated for all combinations of the parameters. To do this, EchoSMs expands the parameters into a Pandas DataFrame with one column for each parameter and one row for each of the combinations. It then runs the model on each row of the DataFrame. That DataFrame, with the TS included, can be returned instead of a list of TS values by using the `expand` option:

```py
        model.calculate_ts(p, expand=True)
```

An introductory [Jupyter notebook](https://github.com/ices-tools-dev/echoSMs/blob/main/docs/tutorial.ipynb) is available that covers the above concepts and a Python script that covers this and more is available [here](https://github.com/ices-tools-dev/echoSMs/blob/main/src/example_code.py).

## Using DataFrames and DataArrays directly

Instead of passing a dictionary to the `calculate_ts` function, a DataFrame or DataArray can be passed instead. The crucial aspect is that the DataFrame columns must have the same names as the parameters that the model requires. For a DataArray, the coordinate dimensions must have the same names as the model parameters.

EchoSMS provides two utility functions ([`as_dataframe`](https://ices-tools-dev.github.io/echoSMs/api_reference/#echosms.utils.as_dataframe), and [`as_dataarray`](https://ices-tools-dev.github.io/echoSMs/api_reference/#echosms.utils.as_dataarray)) to convert from a dictionary representation of model parameters to a DataFrame or DataArray, or you can construct your own, or modify those returned by the `as_dataframe` and `as_dataarray` functions. 

The benefit of using a DataFrame is that you have fine control over what model runs will happen - it doesn't have to be the full set of combinations of the input parameters. The benefit of using a DataArray is that it is easy to extract subsets of the results for further analysis and plotting.

For a DataFrame, the number of model runs will be the number of rows in the DataFrame. For a DataArray the number of models run will be the size of the DataArray (e.g., `DataArray.size()`)

When passing a DataFrame to a model, you can choose whether the TS results are returned as a `Series` or are added to the existing DataFrame (in a column called `ts`). Use the `inplace = True` parameter in the call to `calculate_ts` for this. When passing a DataArray to a model, the TS results are always returned as the data part of the passed in DataArray.

## Multiprocessing

_This is an experimental feature._

The `multiprocess = True` parameter in the call to `calculate_ts` will cause echoSMs to divide the requested model runs over as many cores as your computer has. Total solution time will decrease almost linearly with the number of models runs.

## More complex model parameters

Some models require parameters for which it is not sensible to duplicate them across rows in a DataFrame or as a dimension in a DataArray (e.g., the data that specifies the three-dimensional shape of a fish swimbladder).
EchoSMs allows for this with the concept of _non-expandable_ parameters - these are not expanded into DataFrame columns or DataArray dimensions.

But, as it is very convenient to have all the model parameters in one data structure, echoSMs will store the non-expandable parameters as DataFrame or DataArray attributes. Due to a bug in the DataFrame implementation, the parameters are actually stored as a nested dictionary under a `parameters` key. An example of this is the `PTDWBAModel`:

```py
    from echosms import PTDWBAModel, as_dataframe
    import numpy as np

    model = PTDWBAModel()
    m = {'volume': np.full((5,5,5), 0),
         'f': np.arange(10, 100, 1)*1000,
         'rho': [1024, 1025],  
         'c': [1500, 1501],
         'voxel_size': (0.001, 0.001, 0.001),
         'theta': 90,
         'phi': 0}
    m['volume'][3,3,3] = 1  #  something to produce scatter
    p = as_dataframe(m, model.no_expand_parameters)
    model.calculate_ts(p, inplace=True)
    print(p)
```

For the PTDWBA model, only `theta` and `phi` are expandable, so `p` contains just two columns. The remaining parameters are available via:

```py
    p.attrs['parameters']
```

Note that while `rho`, and `c` look like parameters that would be expanded, they are in the list of non-expandable parameters, so are not expanded. This is because the structure of the PTDWBA model means that it it not sensible to have variable parameters for `rho` and `c`. 

If you pass the dictionary form of the parameters to a model, this treatment of non-expanding parameters is done automatically, where

```py
    model.calculate_ts(m, expand=True)
```

returns the same results as

```py
    p = as_dataframe(m, model.no_expand_parameters)
    model.calculate_ts(p, inplace=True)`
    print(p)
```

## Reference model definitions

[Jech et al., (2015)](https://doi.org/10.1121/1.4937607) presented _reference_ models for a range of scattering objects: spheres, spherical shells, prolate spheroids, and finite cylinders for several boundary conditions (fixed rigid, pressure release, fluid-filled) and parameters (backscatter as a function of frequency and incident angle). These model definitions are included in echoSMs via the [`ReferenceModels`](https://ices-tools-dev.github.io/echoSMs/api_reference/#referencemodels) class. For example, the names of all the model definitions are available with:

```py
    from echosms import ReferenceModels
    rm = ReferenceModels()
    rm.names()
```

which returns:

```py
['fixed rigid sphere',
 'pressure release sphere',
 'gas filled sphere',
 'weakly scattering sphere',
 'spherical fluid shell with pressure release interior',
 'spherical fluid shell with gas interior',
 'spherical fluid shell with weakly scattering interior',
 'fixed rigid prolate spheroid',
 'pressure release prolate spheroid',
 'gas filled prolate spheroid',
 'weakly scattering prolate spheroid',
 'fixed rigid finite cylinder',
 'pressure release finite cylinder',
 'gas filled finite cylinder',
 'weakly scattering finite cylinder',
 'WC38.1 calibration sphere',
 'Cu60 calibration sphere']
```

and the specification for a particular model is given by:

```py
    rm.specification('spherical fluid shell with weakly scattering interior')
```

which returns:

```py
{'name': 'spherical fluid shell with weakly scattering interior',
 'shape': 'sphere',
 'boundary_type': 'fluid shell fluid interior',
 'description': 'A fluid spherical shell with a weakly scattering shell and interior',
 'a': 0.01,
 'shell_thickness': 0.001,
 'medium_rho': 1026.8,
 'medium_c': 1477.4,
 'shell_rho': 1028.9,
 'shell_c': 1480.3,
 'target_rho': 1031.0,
 'target_c': 1483.3,
 'source': 'https://doi.org/10.1121/1.4937607',
 'benchmark_model': 'mss'}
```

Note that the specification contains more information that the model itself needs, so the subset needed for running a model is available via:

```py
    m = rm.parameters('spherical fluid shell with weakly scattering interior')
    print(m)
```

which returns:

```py
{'boundary_type': 'fluid shell fluid interior',
 'a': 0.01,
 'shell_thickness': 0.001,
 'medium_rho': 1026.8,
 'medium_c': 1477.4,
 'shell_rho': 1028.9,
 'shell_c': 1480.3,
 'target_rho': 1031.0,
 'target_c': 1483.3}
```

Note that the `parameters()` call does not return all of the parameters needed by a model. For example, `f` and `theta` are not there and need to be added before running a model:

```py
    m['f'] = [38000, 40000, 42000]
    m['theta'] = 90

    from echosms import MSSModel
    model = MSSModel()
    model.calculate_ts(m)
```

## Benchmark model TS

[Jech et al., (2015)](https://doi.org/10.1121/1.4937607) presented _benchmark_ model runs for the reference models. The TS results from these benchmarks are available in echoSMs via the [`BenchMarkData`](https://ices-tools-dev.github.io/echoSMs/api_reference/#benchmarkdata) class. This class is a simple wrapper around code that reads the CSV-formatted file of benchmark values into a Pandas DataFrame, whereupon they can be readily accessed like this:

```py
    from echosms import BenchmarkData
    bm = BenchmarkData()
    bm.angle_dataset  # the TS as a function of angle at 38 kHz
    bm.freq_dataset  # the TS as a function of frequency
```

The TS and frequency values for a particular benchmark are available via:

```py
    bm.freq_dataset['weakly scattering sphere']
    bm.freq_dataset['frequency (kHz)']
```

or for the angle dataset:

```py
    bm.angle_dataset['weakly scattering sphere']
    bm.angle_dataset['angle (deg)']
```
