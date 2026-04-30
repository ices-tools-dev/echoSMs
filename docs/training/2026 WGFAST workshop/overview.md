# Introduction

The 2026 WGFAST workshop was held on 19 April 2026, prior to the 2026 WGFAST meeting. The
workshop material is now part of the echoSMs documentation, with some edits to work as
stand-alone training material.

???+ note
    The workshop used an online virtual computer configured with echoSMs and
    related packages, and Jupyter notebooks. Assuming that this online computer will not
    continue to be available, the instructions have been updated to work on a local computer or
    other virtual computers.

The aims of this workshop are for you to:

- Provide shapes to the datastore,
- Obtain shapes from the datastore,
- Run echoSMs scattering models,
- Help you choose appropriate scattering models
- Provide feedback on the models and datastore

__Shape datastore__
:    The echoSMs project is developing an online datastore for scattering model shapes and associated metadata. The aim is to facilitate long-term access to good quality scattering model input data, especially the shapes.

    Three echoSMs datastore hackathons have been held (21 Jan, 28 Jan, and 24 March 2026) with interested users. The datastore design has benefited considerably from these hackathons and what you'll see today is a near-final version.

__Scattering models__
:    We'll use the echoSMs scattering model Python package (has nine models relevant to fish and plankton acoustics).

__Selecting scattering models__
:    A common request from the echoSMs workshop at the 2025 WGFAST meeting was for guidance on selecting appropriate acoustics scattering models. We have added a short section on that to today's workshop.

The workshop files and notebooks are in a github repository [here](https://github.com/gavinmacaulay/echoSMs-2026-FAST-workshop).
There is a `notebooks` directory for the Jupyter notebooks and a `shapes` directory for example shape data.

## Manual setup for local or online computer

The workshop requires a recent version of Python with the following packages installed. Use your
preferred package and virtual environment manager (e.g., uv, pip, pixi, etc) to install the packages.
Using pip would require this command:

``` sh
pip install echosms requests pyworms orjson fastapi[standard] stream_zip rtoml jsonschema_rs jmespath tomli_w
```

## Virtual workshop computer

!!! note
    These instructions only apply to the setup used during the workshop.

To reduce setup time we provide individual online Linux computers with pre-configured software and resources. You are welcome to work on your local computer if you want to but we won't have much time to help with configuration problems (the workshop files are available [here](https://github.com/gavinmacaulay/echoSMs-2026-FAST-workshop)).

Access to your online computer is entirely via your web browser:

1. Click this [link](https://workshop.nmfs-openscapes.2i2c.cloud/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fgavinmacaulay%2FechoSMs-2026-FAST-workshop&urlpath=lab%2Ftree%2FechoSMs-2026-FAST-workshop%2FREADME.md&branch=main) to start your server and download/update the workshop files to your online computer.
1. Sign in with an email address (any unique email address will work)
1. The password will be given during the workshop
1. Choose the `Py-R - echoSMs hackathon - latest` image
1. The default resource allocation is fine
1. Click on `Start`
1. You'll end up in a JupyterHub instance in your web browser - it can take a few minutes to get there
1. Right click on the file that the link opened and choose `Show Markdown Preview`
1. Open a Terminal (click on the new tab icon: `+`) and type these lines:
    1. `pip install echosms --upgrade`
    1. `pip install jmespath`

