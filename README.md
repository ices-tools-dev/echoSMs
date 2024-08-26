# echoSMs

![Static badge](https://img.shields.io/pypi/v/echosms.svg)
![Static badge](https://img.shields.io/github/license/ices-tools-dev/echosms)
![Build docs](https://github.com/ices-tools-dev/echosms/actions/workflows/build-docs.yml/badge.svg)
[![python](https://img.shields.io/pypi/pyversions/echosms.svg?logo=python&logoColor=white)](https://pypi.org/project/echosms/)

Making acoustic scattering models available to fisheries and plankton scientists via the world wide web.

Full documentation is available [here](https://ices-tools-dev.github.io/echoSMs/).

## Background

This project is an international collaboration that is, in part, a component of a U.S. NOAA-Fisheries active acoustic strategic initiative [AA-SI](https://github.com/nmfs-fish-tools/AA-SI/tree/main).

Quantitative interpretation of acoustic echograms require software expertise to develop advanced analytical methods for echo classification using mathematical models that predict acoustic backscatter (e.g., target strength, TS, dB re m<sup>2</sup>). These models and predictions can be used to inform echo classification by validating empirical measurements and generating training data for machine learning (ML), artificial intelligence (AI), and other advanced analytical methods, such as inverse methods. Application of these models to fish and plankton requires anatomical and morphological data that are easily accessible and available to the models.

The goal of this project is to make acoustic scattering models available to fisheries and plankton acoustic scientists via the world wide web. By providing the models in an open-access and open-source software language (e.g, Python, R) and providing morphological and anatomical data in open data formats (e.g., HDF5, relational database), the proper and appropriate use of these models can extend to the entire fisheries and plankton acoustics’ community.

## Scattering Models

The initial set of acoustic scattering models will be those used by [Jech et al. (2015)](https://doi.org/10.1121/1.4937607) (Comparisons among ten models of acoustic backscattering used in aquatic ecosystem research. JASA. 138(6): 3742-3764). Acoustic model coding will follow 3 - 4 phases, where the first phase will focus on exact solutions and canonical shapes (Table 1), the second phase will focus on approximate analytical models applied to canonical shapes (Table 2), the third phase will focus on approximate analytical models applied to complex shapes approximating biological targets such as fish and zooplankton, and the fourth phase (if funding and time allows) will focus on numerical models applied to canonical shapes and biological targets.

## Exact Solutions

| Model                             | Shape  | Description | References |
|-----------------------------------|--------|-------------|------------|
| Modal Series<br> solution (MSS)   | Sphere | Fluid       | 1,2        |
|                                   |        | Fixed-rigid | 2,3        |
|                                   |        | Pressure-release | 2     |
|  |  | Fluid-filled | 1,2 |
|  |  | Gas-filled | 2 |
|  |  | Weakly-scattering | 2 |
|  |  | Spherical fluid shell with<br> fluid interior | 2 |
|  |  | Fixed-rigid spherical shell | 2 |
|  |  | Spherical fluid shell with<br> pressure-release interior | 2 |
|  |  | Spherical fluid shell with<br> gas interior | 2 |
|  |  | Spherical fluid shell with<br> weakly-scattering interior | 2 |
| Prolate spheroid<br> modal series<br> solution | Prolate spheroid | Rigid-fixed | 2,4,5 |
|  |  | Pressure-release | 2,4,5 |
|  |  | Gas-filled | 2,4,5 |
| Infinite cylinder? |  |  | 3 |
| Infinite plane? |  |  |  |

1. [Anderson, V. C. 1950. Sound scattering from a fluid sphere. JASA. 22(4): 426-431](https://doi.org/10.1121/1.1906621)
2. [Jech et al. 2015. Comparisons among ten models of acoustic backscattering used in aquatic ecosystem research. JASA. 138: 3742-3764](https://doi.org/10.1121/1.4937607)
3. [Faran, J. J. 1951. Sound scattering by solid cylinders and spheres. JASA. 23(4): 405-418.](https://doi.org/10.1121/1.1906621)
4. Skudrzyk. 1971. The Foundations of Acoustics (Springer, NY), pp. 455-465.
5. Furusawa. 1988. Prolate spheroidal models for predicting general trends of fish target strength,” J. Acoust. Soc. Jpn. (E) 9, 13–14.

## Approximate Analytical Models and Shapes

| Model                             | Shape  | Description | References |
|-----------------------------------|--------|-------------|------------|
| Modal Series-based<br> deformed cylinder<br> model | Finite cylinder | Fixed rigid | 1,2,3 |
|  |  | Pressure-release | 1,2,3 |
|  |  | Gas-filled | 1,2,3 |
|  |  | Weakly-scattering | 1,2,3 |
|  | Prolate spheroid | Fixed rigid | 1,2,3 |
|  |  | Pressure-release | 1,2,3 |
|  |  | Gas-filled | 1,2,3 |
|  |  | Weakly-scattering | 1,2,3 |
| Kirchhoff<br> approximation (KA) | Sphere | Fixed rigid | 3,4,5 |
|  | Prolate spheroid | Fixed rigid | 3,4,5 |
|  | Finite cylinder | Fixed rigid | 3,4,5 |
| Kirchhoff ray mode<br> (KRM) | Sphere | Gas filled | 3,6,7,8 |
|  |  | Weakly scattering | 3,6,7,8 |
|  | Spherical shell | gas filled | 3,6,7,8 |
|  |  | Weakly scattering | 3,6,7,8 |
|  | Prolate spheroid | gas filled | 3,6,7,8 |
|  |  | Weakly scattering | 3,6,7,8 |
|  | Finite cylinder | gas filled | 3,6,7,8 |
|  |  | Weakly scattering | 3,6,7,8 |
| Distorted wave Born<br> approximation (DWBA) | Sphere | Weakly scattering | 3,9,10,11 |
|  | Prolate spheroid | Weakly scattering | 3,9,10,11 |
|  | Finite cylinder | Weakly scattering | 3,9,10,11 |
| Phase-tracking<br> distorted wave Born<br> approximation<br> (PT-DWBA) | Sphere | Weakly scattering | 3,12 |
|  | Spherical shell | Weakly scattering | 3,12 |
|  | Prolate spheroid | Weakly scattering | 3,12 |
|  | Finite cylinder | Weakly scattering | 3,12 |
| Stochastic distorted<br> wave Born<br> approximation<br> (SDWBA) | Sphere | Weakly scattering | 13,14,15 |
|  | Prolate spheroid | Weakly scattering | 13,14,15 |
|  | Finite cylinder | Weakly scattering | 13,14,15 |

1. [Stanton. 1988. Sound scattering by cylinders of finite length. I. Fluid cylinders. JASA. 83, 55–63.](https://doi.org/10.1121/1.396184)
2. [Stanton. 1989. Sound scattering by cylinders of finite length. III. Deformed cylinders. JASA. 86: 691-705](https://doi.org/10.1121/1.398193)
3. [Jech et al. 2015. Comparisons among ten models of acoustic backscattering used in aquatic ecosystem research. JASA. 138: 3742-3764.](https://doi.org/10.1121/1.4937607)
4. [Foote. 1985. Rather-high-frequency sound scattering by swimbladdered fish. JASA. 78: 688-700](https://doi.org/10.1121/1.392438)
5. [Foote and Francis. 2002. Comparing Kirchhoff approximation and boundary-element models for computing gadoid target strengths. JASA. 111: 1644-1654.](https://doi.org/10.1121/1.1458939)
6. [Clay and Horne. 1994. Acoustic models of fish: The Atlantic cod (Gadus morhua). JASA. 96: 1661-1668.](https://doi.org/10.1121/1.404903)
7. [Clay. 1991. Low-resolution acoustic scattering models: Fluid-filled cylinders and fish with swim bladders. JASA. 89: 2168-2179.](https://doi.org/10.1121/1.400910)
8. [Clay. 1992. Composite ray-mode approximations for backscattered sound from gas-filled cylinders and swimbladders. JASA. 92: 2173-2180.](https://doi.org/10.1121/1.405211)
9. [Chu et al. 1993. Further analysis of target strength measurements of Antarctic krill at 38 and 120 kHz: Comparison with deformed cylinder model and inference of orientation distribution. JASA. 93: 2985-2988.](https://doi.org/10.1121/1.405818)
10. [Stanton et al. 1993. Average echoes from randomly oriented random-length finite cylinders: Zooplankton models. JASA. 94: 3463-3472.](https://doi.org/10.1121/1.407200)
11. [Stanton et al. 1998. Sound scattering by several zooplankton groups II: Scattering models. JASA. 103: 236-253.](https://doi.org/10.1121/1.421110)
12. [Jones et al. 2009. Use of the distorted wave Born approximation to predict scattering by inhomogeneous objects: Application to squid. JASA. 125: 73-88.](https://doi.org/10.1121/1.3021298)
13. [Demer and Conti. 2003. Reconciling theoretical versus empirical target strengths of krill: Effects of phase variability on the distorted wave Born approximation. ICES J. Mar. Sci. 60: 429-434.](https://doi.org/10.1016/S1054–3139(03)00002-X)
14. [Demer and Conti. 2004. Erratum: Reconciling theoretical versus empirical target strengths of krill; effects of phase variability on the distorted-wave, Born approximation. ICES J. Mar. Sci. 61: 157-158.](https://doi.org/10.1016/j.icesjms.2003.12.003)
