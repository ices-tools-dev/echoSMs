# Clay files

This directory contains code by [Clarence Clay](https://en.wikipedia.org/wiki/Clarence_S._Clay_Jr.) that implements
the acoustic scattering models in [Clay & Horne (1994)](https://doi.org/10.1121/1.410245), along with other work associated with the KRM scattering models.

It is provided as a historical record of the code and data behind a popular scattering model that is still used today (over 30 years later).

The code was written in the [Microsoft QuickBasic for Mac](https://winworldpc.com/product/quickbasic/10x-for-mac) language, version 1.0, and was likely run on an Apple Macintosh Plus or later computer. 

The original commit of the files in this directory are the original files provided by Mike Jech, which were recovered in 2025 from an old Apple Macintosh floppy disk. Subsequent commits in this directory have modified some of the programs to work with [QB64 PE](https://www.qb64phoenix.com/), an open-source implementation of QuickBasic that that is mostly compatible with QuickBasic for Mac.

## Programs

There are several directories of programs and data under this directory, two of which have been updated to run with QB64 PE.

### Directory `acoustic models clay 10_13_`

This directory contains two programs converted to work with QB64 PE:

- `model fish S(f)_TS.bas`. This program reads in a fish definitions (body and swimbladder shape) and calculates and can plot the TS using the KRM model.
- `fish data file maker.bas`. This program creates fish definition files, calculates fish properties (volume, etc), and can plot the body shape.

 In the same directory as the codes listed above are four fish definition files (`cod`, `cod A.1`, `cod B`, and `cod C`). These correspond to the four fish shapes used in the Clay & Horne (1992) paper (`cod` is cod D in the paper).

## Modifying code

The unmodified QuickBasic programs have no suffix but are easily identified by the presence of a companion file with the same name but ending with `Apl` (the `Apl` file is a compiled version of the code).

When modifying code to run with QB64 PE:

- Convert line endings from old Mac (CR) to Windows (CRLF) or Linux/iOS (LF)
- Add a .bas suffix to the filename
- If editing in QB64 PE, in the Options/Code layout menu:
  - turn off auto indent lines
  - turn off auto single-spacing code elements
  - set the show keywords option to UPPER 
- Load into QB64 PE and save the file; QB64 PE will make some code layout changes (remove leading spaces on lines, add spaces around '=' and other keywords, etc)
- Commit the changes so that any subsequent actual code changes are easier to see in subsequent commits
- Modify the code to work with QB64 PE and commit
