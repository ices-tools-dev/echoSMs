# Developing echoSMs

> These notes are a work in progress.

This page contains notes and instructions on developing and adding new models to echoSMs.

## Obtaining the source code

The echoSMs [source code](https://github.com/ices-tools-dev/echoSMs) is kept on github under an [ICES](http://www.ices.dk/) account. Clone the repository with this URL:

    https://github.com/ices-tools-dev/echoSMs.git

## Generating packages for PyPI

EchoSMs is a pure Python package. The build configuration is done via a [pyproject.toml](https://github.com/ices-tools-dev/echoSMs/blob/main/pyproject.toml) file and [`hatchling`](https://hatch.pypa.io/latest/) is used to produce packages.

A github [action](https://github.com/ices-tools-dev/echoSMs/blob/main/.github/workflows/publish-to-pypi.yml) in the echoSMS repository will generate a Python wheel and source package and upload these to [PyPI](https://pypi.org/project/echosms/). This action is triggered whenever a tagged commit occurs to the repository. The tag is used as the new version number. EchoSMs version numbers follow the [semantic versioning](http://semver.org) convention.

Every commit to the echoSMs repository will generate a development package being uploaded to [TestPyPI](https://test.pypi.org/project/echosms/#history). This is used to always check that a commit does not prevent production of a package and is where a package containing the latest commit can be obtained.

## Documentation

The echoSMs documentation is produced using [`mkdocs`](https://www.mkdocs.org/) and [`mkdocstrings`](https://mkdocstrings.github.io/). The documentation pages are hosted by github and are regenerated after every commit to the repository using a github [action](https://github.com/ices-tools-dev/echoSMs/actions/workflows/build-docs.yml).

Documentation edits can be tested locally by running:

    mkdocs serve

in the top level of the echoSMs repository. The documentation is then available at <http://127.0.0.1:8000>.

## Tests

EchoSMs uses the pytest testing framework. After installing pytest, run the tests using

    pytest -v
    
in the top level of the echoSMs repository.

## Adding a new scattering model

TBD.
