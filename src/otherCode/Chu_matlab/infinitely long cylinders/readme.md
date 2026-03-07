# Infinitely long cylinders

The code in this directory implements exact solutions for scattering by an infinitely long cylinder (or the normalised scattering amplitude from a finite length cylinder).

Four Matlab scripts are provided, each implementing different boundary conditions:

|Boundary conditions|Model file name|
|---|---|
|Elastic|`elastic_fc.m`|
|Fluid-filled|`fluid_fc.m`|
|Rigid fixed or soft (pressure release)|`rgd_sft_fc.m`|
|Elastic shell|`shell_fc.m`|

Each script includes documentation on how to call the model and the `test_models.m` script demonstrates how to run each model.
