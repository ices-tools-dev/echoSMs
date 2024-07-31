# Benchmark Data
Benchmark data for the acoustic scattering models in [Jech et al., 2015](https://doi.org/10.1121/1.4937607).

## Benchmark TS(f)
Benchmark target strength (TS, db re m<sup>2</sup>) as a function of acoustic frequency. The data file [Benchmark_Frequency_TS.csv](https://github.com/ices-tools-dev/echoSMs/blob/main/BenchMark_Data/Benchmark_Frequency_TS.csv) is a text file with comma-separated variable format (.csv). TS values are given to 2-decimal-place precision (i.e., 0.01 dB)

The column names and descriptions are:

| Column Name/Variable | Description |
|----------------------|-------------|
| Frequency_kHz | acoustic frequency in kiloHertz. TS values are given at 2-kHz increments from 12 to 400 kHz. |
| Sphere_Rigid | Benchmark values for the rigid sphere. |
| Sphere_PressureRelease | Benchmark values for the pressure-release sphere. |
| Sphere_Gas | Benchmark values for the gas-filled sphere. |
| Sphere_WeaklyScattering | Benchmark values for the weakly-scattering sphere. |
| ShellSphere_PressureRelease | Benchmark values for the pressure-release shelled sphere. |
| ShellSphere_Gas | Benchmark values for the gas-filled shelled sphere. |
| ShellSphere_WeaklyScattering | Benchmark values for the weakly-scattering shelled sphere. |
| ProlateSpheroid_Rigid | Benchmark values for the rigid prolate spheroid. Valid TS values were computed for 12-80 kHz. NA represents TS values that were not computed. |
| ProlateSpheroid_PressureRelease | Benchmark values for the pressure-release prolate spheroid. Valid TS values were computed for 12-80 kHz. NA represents TS values that were not computed. |
| ProlateSpheroid_Gas | Benchmark values for the gas-filled prolate spheroid. No benchmark TS values were computed. NA represents TS values that were not computed. |
| ProlateSpheroid_WeaklyScattering | Benchmark values for the weakly-scattering prolate spheroid. |
| Cylinder_Rigid | Benchmark values for the rigid cylinder. |
| Cylinder_PressureRelease | Benchmark values for the pressure-release cylinder. |
| Cylinder_Gas | Benchmark values for the gas-filled cylinder. |
| Cylinder_WeaklyScattering | Benchmark values for the weakly-scattering cylinder. |

## Benchmark TS(&theta;) @ 38 kHz
Benchmark target strength (TS, db re m<sup>2</sup>) as a function of insonifying angle of incidence (&theta;) for the prolate spheroid and cylinder shapes. The data file [Benchmark_Angle_TS.csv](https://github.com/ices-tools-dev/echoSMs/blob/main/BenchMark_Data/Benchmark_Angle_TS.csv) is a text file with comma-separated variable format (.csv). TS values are given to 2-decimal-place precision (i.e., 0.01 dB). 90-degree &theta; is broadside incidence and 0-degree is end-on incidence. 

The column names and descriptions are:

| Column Name/Variable | Description |
|----------------------|-------------|
| Angle_deg | Angle of incidence. TS values are given at 2-degree increments from 0 to 90 degrees. |
| ProlateSpheroid_Rigid | Benchmark values for the rigid prolate spheroid. |
| ProlateSpheroid_PressureRelease | Benchmark values for the pressure-release prolate spheroid. |
| ProlateSpheroid_Gas | Benchmark values for the gas-filled prolate spheroid. |
| ProlateSpheroid_WeaklyScattering | Benchmark values for the weakly-scattering prolate spheroid. |
| Cylinder_Rigid | Benchmark values for the rigid cylinder. TS values for end-on (0 degree) incidence were not computed.|
| Cylinder_PressureRelease | Benchmark values for the pressure-release cylinder. TS values for end-on (0 degree) incidence were not computed. |
| Cylinder_Gas | Benchmark values for the gas-filled cylinder. TS values for end-on (0 degree) incidence were not computed. |
| Cylinder_WeaklyScattering | Benchmark values for the weakly-scattering cylinder. TS values for end-on (0 degree) incidence were not computed. |






