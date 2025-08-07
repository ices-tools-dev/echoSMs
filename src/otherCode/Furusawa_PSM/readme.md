# Furusawa prolate spheroidal model

This directory contains a program by Masahiko Furusawa that implements the acoustic scattering model in [Furusawa (1988)](https://doi.org/10.1250/ast.9.13) and is provided as a historical record of the code behind a popular scattering model that is still used today, some 27 years later.

The code was originally written in [HP Basic](https://en.wikipedia.org/wiki/Rocky_Mountain_BASIC) and ran on a [HP 9000](https://en.wikipedia.org/wiki/HP_9000) computer but has been modified to run on Windows computers using [HTBasic](https://transera.com/).

The `SCTLIBV3.bas` file is the original version for HP Basic, while `KS25A4.bas` is the modified version for HTBasic. Text versions of these two programs are provided as `SCTLIBV3.txt` and `KS25A4.txt`.

The most recent version of HTBasic is HTBasic 2021 and runs on Windows 11. To date, the `KS25A4.bas` version has been tested with release 9.5 of HTBasic, which runs on Windows Vista or lower.

The results from the programs are written into a binary file and which can be converted to an ASCII file by the PF command in the program menu.

The SCTLIBV3 version of the program can read calculated eigenvalues from the LF60609 file to reduce calculation time.
