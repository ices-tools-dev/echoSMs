"""Proof of concept of echoSMs RESTful API using FastAPI."""

from fastapi import FastAPI, Query, Path
from fastapi.responses import Response
import matplotlib.pyplot as plt
import numpy as np
import io
from typing import Annotated
from pathlib import Path as pp
import json
import pandas as pd


base_dir = pp(r'C:\Users\GavinMacaulay\OneDrive - Aqualyd Limited\Documents\Aqualyd'
              r'\Projects\2024-05 NOAA modelling\working\anatomical data store')
datasets_dir = base_dir/'datasets'

with open(datasets_dir/'datasets-automatically-generated.json', 'r') as f:
    all_datasets = json.load(f)

# make a Pandas version of the dataset attributes that can be searched through easily
searchable_attrs = ['dataset_id', 'species', 'imaging_method', 'model_type', 'aphiaID']
searchable_data = [{key: d[key] for key in searchable_attrs if key in d} for d in all_datasets]
df = pd.DataFrame(searchable_data)

app = FastAPI()


@app.get("/v1/datasets", summary="Get metadata for all datasets")
async def get_datasets(species: Annotated[str | None, Query(
                            title='Species', 
                            description="The scientific species name")] = None,
                       imaging_method: Annotated[str | None, Query(
                           title='Imaging method',
                           description="The imaging method used")] = None,
                       model_type: Annotated[str | None, Query(
                           title='Model type',
                           description="The model type used")]= None,
                       aphiaID: Annotated[int | None, Query(
                           title='AphiaID',
                           description='The aphiaID of this dataset')]= None):
    """Returns dataset metadata and shapes with optional filtering."""
    def df_query(name, var, end=False):
        return '' if var is None else f'{name} == @{name} & '

    q = df_query('species', species)
    q += df_query('imaging_method', imaging_method)
    q += df_query('model_type', model_type)
    q += df_query('aphiaID', aphiaID)

    if len(q) == 0:
        return all_datasets

    return [ds for ds in all_datasets if ds['dataset_id'] in df.query(q[:-3])['dataset_id'].values]


@app.get("/v1/dataset/{dataset_id}")
async def get_dataset(dataset_id: Annotated[str, Path(
                          description='The dataset ID')],
                      full_data: Annotated[bool, Query(
                          description='If true, all raw data for the dataset will '
                                      'be returned as a zipped file')]= False):
    """Return dataset given a dataset id."""
    for ds in all_datasets:
        if ds["dataset_id"] == dataset_id:
            if not full_data:
                return ds
            else:  # zip up the dataset data and send
                return {'message': 'not yet implemented'}
    return {"message": "Specimen not found"}


@app.get("/v1/specimen/{dataset_id}/{specimen_id}")
async def get_specimen(dataset_id: Annotated[str, Path(
                          description='The dataset ID')],
                       specimen_id: Annotated[str, Path(
                          description='The specimen ID')]):
    """Return specimen data given the dataset id and specimen id."""
    for ds in all_datasets:
        if ds["dataset_id"] == dataset_id:
            for specimen in ds['specimens']:
                if specimen['specimen_id'] == specimen_id:
                    return specimen
    return {"message": "Specimen not found"}


@app.get("/v1/specimen_image/{dataset_id}/{specimen_id}")
async def get_specimen_image(dataset_id: Annotated[str, Path(
                                description='The dataset ID')],
                            specimen_id: Annotated[str, Path(
                                description='The specimen ID')]):
    """Return a plot of the specimen shape given the dataset id and specimen id."""
    for ds in all_datasets:
        if ds["dataset_id"] == dataset_id:
            for specimen in ds['specimens']:
                if specimen['specimen_id'] == specimen_id:
                    img = plot_specimen(specimen, dataset_id=dataset_id, stream=True)
                    return Response(img, media_type="image/png")
    return {"message": "Specimen not found"}


def plot_specimen(specimen, dataset_id='', stream=False):
    """Plot the specimen shape."""
    fig, axs = plt.subplots(2, 1, sharex=True, layout='constrained')

    match specimen['shape_type']:
        case 'outline':
            plot_shape_outline(specimen['shapes'], axs)
        case 'surface':
            plot_shape_surface(specimen['shapes'], axs)
        case 'voxels':
            plot_shape_voxels(specimen['shapes'], axs)

    axs[0].text(0, 1.05, 'Dorsal', transform=axs[0].transAxes)
    axs[1].text(0, 1.05, 'Lateral', transform=axs[1].transAxes)

    fig.suptitle(dataset_id + ' ' + specimen['specimen_id'])
    fig.supxlabel('[mm]')
    fig.supylabel('[mm]')

    if stream:
        with io.BytesIO() as buffer:
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            return buffer.getvalue()
    else:
        plt.show()


def plot_shape_outline(shapes, axs):
    """Plot the specimen's outline shape."""
    for s in shapes:
        c = 'C0' if s['boundary'] == 'fluid' else 'C1'
        x = np.array(s['x'])*1e3
        z = np.array(s['z'])*1e3
        y = np.array(s['y'])*1e3
        width_2 = np.array(s['width'])*1e3/2
        zU = (z + np.array(s['height'])*1e3/2)
        zL = (z - np.array(s['height'])*1e3/2)

        # Dorsal view
        axs[0].plot(x, y, c='grey', linestyle='--', linewidth=1)  # centreline
        axs[0].plot(x, y+width_2, c=c)
        axs[0].plot(x, y-width_2, c=c)

        # Lateral view
        axs[1].plot(x, z, c='grey', linestyle='--', linewidth=1)  # centreline
        axs[1].plot(x, zU, c=c)
        axs[1].plot(x, zL, c=c)

        # close the ends of the shapes
        for i in [0, -1]:
            axs[1].plot([x[i], x[i]], [zU[i], zL[i]], c=c)
            axs[0].plot([x[i], x[i]], [(y+width_2)[i], (y-width_2)[i]], c=c)
            axs[i].set_aspect('equal')
            axs[i].xaxis.set_inverted(True)


def plot_shape_surface(specimen, axs):
    """Plot the specimen's 3D triangular shape."""
    for s in specimen['shapes']:
        pass


def plot_shape_voxels(s, axs):
    """Plot the specimen's voxels."""
    pass
