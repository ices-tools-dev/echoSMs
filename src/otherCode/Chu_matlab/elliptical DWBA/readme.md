# Elliptical DWBA scattering model

The code in this directory is a Matlab package that computes backscattering by an elongated finite object with an elliptical cross-section (as a function along lengthwise direction) using closed-form DWBA analytical solutions.

The model is explained in the `Model Description.pdf` file in this directory (the source Word document, `Model Description.docx` is also there).

The `example_DWBA_ellipsolid.m` script can calculate 22 different scenarios as described in lines 45 to 67 in the script.

This model was also implemented in the [ZooScatR](https://github.com/AustralianAntarcticDivision/ZooScatR) R package as detailed in [Gastauer et al., 2019](http://doi.org/10.1121/1.5085655).
