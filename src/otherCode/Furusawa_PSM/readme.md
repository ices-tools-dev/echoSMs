# Furusawa prolate spheroidal model

This directory contains a program by Masahiko Furusawa that implements the acoustic scattering model in [Furusawa (1988)](https://doi.org/10.1250/ast.9.13) and is provided as a historical record of the code behind a popular scattering model that is still used today, some 27 years later.

The code was originally written in [HP Basic](https://en.wikipedia.org/wiki/Rocky_Mountain_BASIC) and ran on a [HP 9000](https://en.wikipedia.org/wiki/HP_9000) computer, but has been subsequently modified by Kouichi Sawada to run on Windows computers with [HTBasic](https://transera.com/).

## The code

The `SCTLIBV3.bas` file is the original version for HP Basic, while `KS25A4.bas` is the modified version for HTBasic. Text versions of these two programs are provided as `SCTLIBV3.txt` and `KS25A4.txt`.

The most recent version of HTBasic is HTBasic 2021 and runs on Windows 11. To date, the `KS25A4.bas` version has been tested with release 9.5 of HTBasic, which runs on Windows Vista or lower. HTBasic is commercial software, but is available for free trials.

The results from the program are written into a binary file and can be converted to an ASCII file by the `PF` command in the menus of the `SCTLIBV3.bas` and `KS25A4.bas` programs.

The SCTLIBV3 version of the program can read calculated eigenvalues from the `LF60609` file to reduce calculation time.

## Using an HP9000 emulator

There is an HP98x6 emulator available for Windows computers that may be able to run the prolate spheroidal model code. This has not been tested, but some information and links are provided here in case someone wishes to try.

The emulator is available [here](https://sites.google.com/site/olivier2smet2/hp_projects/hp98x6) and there is some discussion about using it to run HP Basic programs [here](https://groups.io/g/HP-Agilent-Keysight-equipment/topic/hpbasic_for_windows/79258624?page=4). There is also a PDF with step-by-step instructions from a link in the 5th post of [this](https://groups.io/g/VintHPcom/topic/hp_98x6_emulator/102119518) discussion ([direct link](https://groups.io/g/VintHPcom/attachment/10443/0/HP%20Emulator%20guide_V1.2.pdf)).

Manuals for the HP 9000 series of computers and the HP Basic that ran on them are available on the Internet. Relevant titles include:

|Title|HP part number|
|-----|--------------|
|Programming with HP Basic|82301-90015|
|HP BASIC Language Processer. Programmer's Reference Guide|82301-90002|
|Using the BASIC 5.0/5.1 System. HP 9000 Series 200/300 Computers|98613-90000|
|BASIC 4.0 Language Reference. HP 9000 Series 200/300 Computers|98613-90051|
|BASIC Language Reference. Volume 1: A-N. HP 9000 Series 200/300 Computers|98613-90052|
|BASIC Language Reference. Volume 2: O-Z. HP 9000 Series 200/300 Computers|98613-90052|
|Installing, Using, and Maintaining the BASIC 5.0 System. HP 9000 Series 200/200 Computers|98613-90042|
