# Contributing to echoSMs

We welcome all contributions to echoSMs, be it code, test cases, bug reports, discussion of models, etc. Please use the github facilities for this (i.e., issues and pull-requests). We are also happy to accept directly code that we can add to echoSMs on your behalf.

An objective of echoSMs is to provide scattering models in a form that is easy to access, use, and compare to other models. To help with that, we specify model parameter units, angle conventions, and required model outputs that code contributions should support. These are:

| Parameter | Units | Notes |
|-----------|-------|--|
|length, diameter, radius, thickness, etc|m||
|density|kg/m^3||
|sound speed|m/s||
|angle|degrees|See XXX for angle conventions|
|frequency|Hz||
|target strength|dB|reference value is 1 m^2|

In addition, contributions of code should follow standardised or community-agreed styles and be provided in (or added to) a structure suitable for packaging and uploading to package libraries. For Python this includes `pip` and/or `conda`, for R this would be `CRAN`, for Matlab this would be a toolbox on the MATLAB File Exchange, etc.

Python code should follow [PEP8](https://peps.python.org/pep-0008) and docstrings should use [PEP257](https://peps.python.org/pep-0257/) with the contents following the [numpydoc style](https://numpydoc.readthedocs.io/en/latest/format.html).


