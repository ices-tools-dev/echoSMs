# Benchmark Data

The benchmark data for the acoustic scattering models in [Jech et al. (2015)](https://doi.org/10.1121/1.4937607) are included in the echoSMs package. These comprise target strength values for two sets of benchmarks:

- Model runs over a range of frequencies
- Model runs over a range of incident angles at a frequency of 38 kHz

These are provided as text files (see below), or as Pandas DataFrames via the [benchmarkdata] class.

## TS(f)

This dataset contains target strength (TS re 1 m² [dB]) as a function of acoustic frequency. The data file, [Benchmark_Frequency_TS.csv](https://github.com/ices-tools-dev/echoSMs/tree/main/src/echosms/resources/BenchMark_Data/Benchmark_Frequency_TS.csv), is formatted as comma-separated TS values given to a precision of two decimal places (i.e., 0.01 dB). The first row in the file contains column labels, indicating the model type for that column. NA represents TS values that were not computed.

The column names and descriptions are:

| Column Name | Description |
|-------------|-------------|
| Frequency_kHz | Acoustic frequency in kHz. TS values are given at 2 kHz increments from 12 to 400 kHz. |
| Sphere_Rigid | Benchmark values for the rigid sphere. |
| Sphere_PressureRelease | Benchmark values for the pressure release sphere. |
| Sphere_Gas | Benchmark values for the gas filled sphere. |
| Sphere_WeaklyScattering | Benchmark values for the weakly scattering sphere. |
| ShellSphere_PressureRelease | Benchmark values for the pressure release shelled sphere. |
| ShellSphere_Gas | Benchmark values for the gas filled shelled sphere. |
| ShellSphere_WeaklyScattering | Benchmark values for the weakly scattering shelled sphere. |
| ProlateSpheroid_Rigid | Benchmark values for the rigid prolate spheroid. Valid TS values were computed for 12-80 kHz |
| ProlateSpheroid_PressureRelease | Benchmark values for the pressure release prolate spheroid. Valid TS values were computed for 12-80 kHz. |
| ProlateSpheroid_Gas | Benchmark values for the gas filled prolate spheroid. No benchmark TS values were computed. |
| ProlateSpheroid_WeaklyScattering | Benchmark values for the weakly scattering prolate spheroid. |
| Cylinder_Rigid | Benchmark values for the rigid cylinder. |
| Cylinder_PressureRelease | Benchmark values for the pressure release cylinder. |
| Cylinder_Gas | Benchmark values for the gas filled cylinder. |
| Cylinder_WeaklyScattering | Benchmark values for the weakly scattering cylinder. |

## TS(θ) at 38 kHz

This dataset contains target strength (TS re 1m² [dB]) as a function of insonifying angle of incidence (θ) for the prolate spheroid and cylinder shapes. The data file [Benchmark_Angle_TS.csv](https://github.com/ices-tools-dev/echoSMs/blob/main/src/echosms/resources/BenchMark_Data/Benchmark_Angle_TS.csv) is formatted a comma-separated Ts values given to a precision of two decimal places (i.e., 0.01 dB). Incidence angle is as per the [echoSMs convention][coordinate-systems]. The first row in the file contains column labels, indicating the model type for that column. NA represents TS values that were not computed.

The column names and descriptions are:

| Column Name | Description |
|-------------|-------------|
| Angle_deg | Angle of incidence. TS values are given at 2-degree increments from 0 to 90°. |
| ProlateSpheroid_Rigid | Benchmark values for the rigid prolate spheroid. |
| ProlateSpheroid_PressureRelease | Benchmark values for the pressure release prolate spheroid. |
| ProlateSpheroid_Gas | Benchmark values for the gas filled prolate spheroid. |
| ProlateSpheroid_WeaklyScattering | Benchmark values for the weakly scattering prolate spheroid. |
| Cylinder_Rigid | Benchmark values for the rigid cylinder. TS values for end-on (0°) incidence were not computed.|
| Cylinder_PressureRelease | Benchmark values for the pressure release cylinder. TS values for end-on (0°) incidence were not computed. |
| Cylinder_Gas | Benchmark values for the gas filled cylinder. TS values for end-on (0°) incidence were not computed. |
| Cylinder_WeaklyScattering | Benchmark values for the weakly scattering cylinder. TS values for end-on (0°) incidence were not computed. |
