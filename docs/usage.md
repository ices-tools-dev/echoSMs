# Using echoSMs

EchoSMs is (currently) a Python package that implements acoustic scattering models. Each different model is a separate Python class in the echoSMs package. They all inherit from a common base class that defines a common calling convention.

## Installation

EchoSMs is available on [PyPi](https://pypi.org) as [`echosms`](https://pypi.org/project/echosms/). Install it with:

    pip install echosms

## Versions

The changelogs for echoSMs are listed [here](https://github.com/ices-tools-dev/echoSMs/releases) and the latest release is always at the top of that list.

The installed version of echosms can be printed with this Python code:

```py
from importlib.metadata import version
version('echosms')
```

To upgrade echosms to the latest version use:

```py
pip install echosms --upgrade
```

## Model overview

The following models are available in echoSMs:

|Model type|Python class name(s)|Description|
|----------|----------|-----------|
|Deformed cylinder|DCMModel|Truncated cylinders with various boundary conditions|
|Distorted-wave Born approximation|DWBAModel|Weakly scattering objects with piecewise circular cross-sections and homogenous interiors with an optional stochastic variant (the SDWBA)|
|Elastic sphere|ESModel|Elastic spheres, such as echosounder calibration spheres|
|High-pass|HPModel|Approximate models for simple shapes|
|Kirchhoff approximation|KAModel|Surfaces that are mainly convex|
|Kirchhoff ray mode|KRMModel|A fish body and swimbladder model for high and low frequencies|
|Modal series solution|MSSModel|Spheres with various boundary conditions, including shells|
|Prolate spheroidal modal series|PSMSModel|Prolate spheroids with various boundary conditions|
|Phase-tracking distorted-wave Born approximation|PTDWBAModel|Weakly scattering objects of any shape with inhomogeneous interiors|

Future models will include the Fourier matching method and potentially the finite element and boundary element models. We welcome contributions or suggestions of additional models.

## Running a model

Each echoSMs model expects input parameters that define the model (e.g., size, shape, material properties, etc). These can be provided in three ways:

- A Python **dictionary** with an entry for each parameter,
- A Pandas **DataFrame** with columns for each parameter and a row for each model run,
- An Xarray **DataArray** with as many dimensions as parameters. The parameter values are in the DataArray coordinate variables.

To use a model, you need to know what parameters it requires. These are documented in the `calculate_ts_single` function that each model has (refer to the echoSMS [API reference](api_reference.md) for details). The units for numerical parameters will always follow the echoSMs unit [convention](conventions.md#units). For example, the MSSModel, when simulating the scattering from a pressure release sphere, needs the following parameters:

|Name|Description|
|--------------|-----------|
|medium_c|Sound speed in the fluid medium surrounding the target [m/s]|
|medium_rho|Density of the fluid medium surrounding the target [kg/m³]|
|a|Radius of the spherical target [m]|
|f|Frequency to calculate the scattering at [Hz]|
|boundary_type|The boundary type. Supported types are `fixed rigid`, `pressure release`, and `fluid filled`|

The simplest way to provide these to the model is a dictionary:

```py
p = {'medium_rho': 1026.8,
     'medium_c': 1477.4,
     'a': 0.01, 
     'boundary_type': 'pressure-release',
     'f': 38000}
```

An instance of the model can then be created and the `calculate_ts` function called with these parameters:

```py
from echosms import MSSModel
model = MSSModel()
model.calculate_ts(p)
```

This will return one TS value corresponding to the parameters given. If you want to run the model for a range of parameters, the relevant dictionary items can contain multiple values:

```py hl_lines="6"
import numpy as np
p = {'medium_rho': 1026.8,
     'medium_c': 1477.4,
     'a': 0.01,
     'boundary_type': 'pressure-release',
     'f': np.arange(10, 100, 1)*1000}  # [Hz]
model.calculate_ts(p)
```

It is also fine to have multiple items with multiple values:

```py hl_lines="3 4 5"
p = {'medium_rho': 1026.8,
     'medium_c': 1477.4,
     'a': np.arange(0.01, 0.02, 0.001),  # [m]
     'boundary_type': ['pressure-release', 'fixed-rigid'],
     'f': np.arange(10, 100, 1)*1000}  # [Hz]
model.calculate_ts(p)
```

The TS will be calculated for all combinations of the parameters. To do this, echoSMs expands the parameters into a Pandas DataFrame with one column for each parameter and one row for each of the combinations. It then runs the model on each row of the DataFrame. That DataFrame, with the TS included, can be returned instead of a list of TS values by using the `expand` option:

```py
model.calculate_ts(p, expand=True)
```

An introductory [Jupyter notebook](https://github.com/ices-tools-dev/echoSMs/blob/main/docs/tutorial.ipynb) is available that covers the above concepts and a Python script that covers this and more is available [here](https://github.com/ices-tools-dev/echoSMs/blob/main/src/example_code.py).

## Using DataFrames and DataArrays directly

Instead of passing a dictionary to the `calculate_ts` function, a DataFrame or DataArray can be passed instead. The crucial aspect is that the DataFrame columns must have the same names as the parameters that the model requires. For a DataArray, the coordinate dimensions must have the same names as the model parameters.

EchoSMS provides two utility functions ([`as_dataframe`](api_reference.md#echosms.utils.as_dataframe), and [`as_dataarray`](api_reference.md#echosms.utils.as_dataarray)) to convert from a dictionary representation of model parameters to a DataFrame or DataArray, or you can construct your own, or modify those returned by the `as_dataframe` and `as_dataarray` functions.

The benefit of using a DataFrame is that you have fine control over what model runs will happen - it doesn't have to be the full set of combinations of input parameters. The benefit of using a DataArray is that it is easy to extract subsets of the results for further analysis and plotting.

For a DataFrame, the number of model runs will be the number of rows in the DataFrame. For a DataArray the number of models run will be the size of the DataArray (e.g., `DataArray.size()`)

When passing a DataFrame to a model, you can choose whether the TS results are returned as a `Series` or are added to the existing DataFrame (in a column called `ts`). Use the `inplace = True` parameter in the call to `calculate_ts` for this. When passing a DataArray to a model, the TS results are always returned in the data part of the passed in DataArray.

## More complex model parameters

Some models use parameters that are not sensibly duplicated across rows in a DataFrame or as a dimension in a DataArray (e.g., the data that specifies the three-dimensional shape of a fish swimbladder). EchoSMs allows for this with the concept of _non-expandable_ parameters - these are not expanded into DataFrame columns or DataArray dimensions. Non-expandable parameter names are available from the models' `no_expand_parameters` attribute.

But, as it is very convenient to have all the model parameters in one data structure, echoSMs will store the non-expandable parameters as a dict in the DataFrame or DataArray attributes. An example of this is the `PTDWBAModel`:

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
m['volume'][3,3,3] = 1  # something to produce scatter

p = as_dataframe(m, model.no_expand_parameters)
model.calculate_ts(p, inplace=True)
print(p)
```

For the PTDWBA model, only `theta` and `phi` are expandable, so `p` contains three columns (`theta`, `phi`, and `ts`). The remaining parameters are available via:

```py
p.attrs['parameters']
```

Note that while `rho` and `c` look like parameters that would be expanded, they are in the list of non-expandable parameters, so are not expanded. This is because the structure of the PTDWBA model means that it it not sensible to have variable parameters for `rho` and `c`. 

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

## Multiprocessing

EchoSMs can use more than one CPU to run models. Internally, echoSMs uses a Pandas DataFrame to store
the parameters for each model run (one row per parameter set) and the multiprocessing is achieved with a package that runs an echoSMs model on each row in the DataFrame, split across separate CPUs. This is enabled with the `multiprocess = True` parameter in the call to `calculate_ts()`. The total solution time will decrease almost linearly with the number of CPUs.

A progress bar can be shown via the `progress = True` option, but note that this tends to not work correctly in some Python terminals (e.g. the Spyder terminal). The progress bar shows the number of chunks that the DataFame has been split into and the number of chunks completed (in contrast, the non-multiprocessing progress bar shows the number of model runs completed).

EchoSMs currently uses the [mapply](https://github.com/ddelange/mapply) package to distribute the model runs. Mapply is limited to CPUs on the one computer - it does not support multiprocessing across multiple computers. A different multiprocessing package would be needed to support running on multiple computers (e.g. clusters of computers).

## Reference model definitions

[Jech et al., (2015)](https://doi.org/10.1121/1.4937607) presented _reference_ models for a range of scattering objects: spheres, spherical shells, prolate spheroids, and finite cylinders for several boundary conditions (fixed rigid, pressure release, fluid-filled) and parameters (backscatter as a function of frequency and incident angle). These model definitions are included in echoSMs via the [`ReferenceModels`](api_reference.md#echosms.ReferenceModels) class, along with other objects, such as calibration spheres. For example, the names of all the model definitions are available with:

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
 'WC20 calibration sphere',
 'WC21 calibration sphere',
 'WC22 calibration sphere',
 'WC25 calibration sphere',
 'WC38.1 calibration sphere',
 'WC57.2 calibration sphere',
 'WC60 calibration sphere',
 'WC64 calibration sphere',
 'Cu13.7 calibration sphere',
 'Cu23 calibration sphere',
 'Cu32 calibration sphere',
 'Cu42 calibration sphere',
 'Cu45 calibration sphere',
 'Cu60 calibration sphere',
 'Cu63 calibration sphere',
 'Cu64 calibration sphere']
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

Note that the `parameters()` call does not return all of the parameters needed by a model. For example, `f` is not there and needs to be added before running a model:

```py
m['f'] = [38000, 40000, 42000]

from echosms import MSSModel
model = MSSModel()
model.calculate_ts(m)
```

## Benchmark model TS

[Jech et al., (2015)](https://doi.org/10.1121/1.4937607) presented benchmark TS values for the reference models. The TS results from these benchmarks are available in echoSMs via the [`BenchmarkData`](api_reference.md#echosms.BenchmarkData) class. This class reads the CSV-formatted files of benchmark values and provides methods that list the benchmark names, returns TS as a function of frequency and angle for each benchmark model. For more complex uses of the benchmark data, they are also available as Pandas DataFrames.

```py
from echosms import BenchmarkData
bm = BenchmarkData()

# Lists of the benchmark model names
bm.freq_names()
bm.angle_names()

# TS as a function of frequency for a model
f, ts = bm.freq_data('fixed rigid sphere')

# TS as a function of angle for a model
theta, ts = bm.angle_data('fixed rigid prolate spheroid')

# As Pandas DataFrames
bm.freq_as_dataframe()
bm.angle_as_dataframe()
```
