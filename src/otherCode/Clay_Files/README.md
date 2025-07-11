# Clay files

This directory contains code by [Clarence Clay](https://en.wikipedia.org/wiki/Clarence_S._Clay_Jr.) that implements
the acoustic scattering models in [Clay & Horne (1992)](https://doi.org/10.1121/1.404903), along with other work associated with the KRM scattering models.

It is provided as a historical record of the code and data behind a commonly-used scattering model that is still used today (over 30 years later).

The code was written in the Microsoft QuickBasic for Mac language, version 1.0, and was likely run on an Apple Macintosh Plus or later computer. 

The original commit of the files in this directory are the original files provided by Mike Jech, which were recovered from an old Apple Macintosh floppy disk in 2025. Subsequent commits in this directory have modified some of the programs to work with [QB64 PE](https://www.qb64phoenix.com/), an open-source implementation of QuickBasic that that is mostly compatible with QuickBasic for Mac.

## Programs

The `acoustic models clay 10_13_` directory contains the code for the KRM model in the `model fish S(f)_TS.bas` file, which has been edited to run with QB64 PE. In the same directory are four fish definition files (`cod`, `cod A.1`, `cod B`, and `cod C`), which correspond to the four fish shapes used in the Clay & Horne (1992) paper (`cod` is cod D in the paper).

## Modifying code

When modifying code to run with QB64 PE:

- Convert line endings from old Mac (CR) to Windows (CRLF) or Linxu/iOS (LF)
- Add a .bas suffix to the filename
- If editing in QB64 PE, in the Options/Code layout menu:
  - turn off auto indent lines
  - turn off auto single-spacing code elements
  - set the show keywords option to UPPER 
- Load into QB64 PE and save the file; QB64 PE will make some code layout changes (remove leading spaces on lines, add spaces around '=' and other keywords, etc)
- Commit the changes to make any actual code changes easier to see in subsequent commits
- Modify the code to work with QB64 PE
