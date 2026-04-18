# Introduction

The workshop is/was from 10:00 to 13:00 (UTC+2) on 19 April 2026. Online participants can join through the meeting link (sent separately).

The workshop presentation (what you are looking at now) is part of the echoSMs documentation, available at:

<https://ices-tools-dev.github.io/echoSMs/training/2026 WGFAST workshop/overview/>

The workshop files and notebooks are automatically on your online computer (and also in a github repository [here](https://github.com/gavinmacaulay/echoSMs-2026-FAST-workshop)).

The aims of this workshop are for you to:

- Provide shapes to the datastore,
- Obtain shapes from the datastore,
- Run echoSMs scattering models,
- Help you choose appropriate scattering models
- Provide feedback on the models and datastore

???+ "Ask questions, provide feedback, etc, at any time"
    Or talk to or email us later ([Gavin](mailto:gavin@aqualyd.nz), [Mike](mailto:michael.jech@noaa.gov)).

__Shape datastore__
:    The echoSMs project is developing an online datastore for scattering model shapes and associated metadata. The aim is to facilitate long-term access to good quality scattering model input data, especially the shapes.

    Three echoSMs datastore hackathons have been held (21 Jan, 28 Jan, and 24 March 2026) with interested users. The datastore design has benefited considerably from these hackathons and what you'll see today is a near-final version.

__Scattering models__
:    We'll use the echoSMs scattering model Python package (has nine models relevant to fish and plankton acoustics).

__Selecting scattering models__
:    A common request from the echoSMs workshop at the 2025 WGFAST meeting was for guidance on selecting appropriate acoustics scattering models. We have added a short section on that to today's workshop.

## Virtual workshop computer

To reduce setup time we provide individual online Linux computers with pre-configured software and resources. You are welcome to work on your local computer if you want to but we won't have much time to help with configuration problems (the workshop files are available [here](ttps://github.com/gavinmacaulay/echoSMs-2026-FAST-workshop), the web API code [here](https://github.com/gavinmacaulay/data_store_testing.git), and the web API setup script is [here](https://github.com/nmfs-opensci/container-images/blob/main/images/acoustics/Dockerfile) on lines 16-21).

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
    1. `cd /data_store_testing`
    1. `fastapi dev`

JupyterHub notebooks are in the `notebooks` directory on your online computer and data files are in the `shapes` directory. You can upload the download files to the online computer using XXXX.
