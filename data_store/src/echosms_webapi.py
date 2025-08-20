"""Proof of concept of echoSMs anatomical data store RESTful API using FastAPI."""

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

schema_url = 'https://ices-tools-dev.github.io/echoSMs/schema/data_store_schema/'

app = FastAPI(title='The echoSMs web API',
              openapi_tags=[{'name': 'get', 
                             'description': 'Calls that get information from the data store'},])


@app.get("/v1/datasets",
         summary="Get dataset_ids with optional filtering",
         response_description='A list of dataset_ids',
         tags=['get'])
async def get_datasets(species: Annotated[str | None, Query(title='Species', description="The scientific species name")] = None,
                       imaging_method: Annotated[str | None, Query(title='Imaging method', description="The imaging method used")] = None,
                       model_type: Annotated[str | None, Query(title='Model type', description="The model type used")] = None,
                       anatomical_category: Annotated[str | None, Query(title='Anatomical category', description="The anatomical category")] = None,
                       shape_method: Annotated[str | None, Query(title='Shape method', description="The shape method")] = None,
                       aphiaID: Annotated[int | None, Query(title='AphiaID', description='The [aphiaID](https://www.marinespecies.org/aphia.php)')] = None):

    def df_query(name, var, end=False):
        return '' if var is None else f'{name} == @{name} & '

    q = df_query('species', species)
    q += df_query('imaging_method', imaging_method)
    q += df_query('model_type', model_type)
    q += df_query('anatomical_category', anatomical_category)
    q += df_query('shape_method', shape_method)
    q += df_query('aphiaID', aphiaID)

    if len(q) == 0:
        return df['dataset_id'].tolist()

    return df.query(q[:-3])['dataset_id'].tolist()


@app.get("/v1/dataset/{dataset_id}",
         summary='Get the dataset with the given dataset_id',
         response_description=f'A dataset structured as per the echoSMs data store [schema]({schema_url})',
         tags=['get'])
async def get_dataset(dataset_id: Annotated[str, Path(description='The dataset ID')],
                      full_data: Annotated[bool, Query(description='If true, all raw data for the dataset will be returned as a zipped file')] = False):

    ds = get_ds(dataset_id)
    if not ds:
        return {"message": "Dataset not found"}
    
    if full_data:
        # zip up the dataset and stream out
        return {'message': 'Not yet implemented'}

    return ds[0]


@app.get("/v1/specimens/{dataset_id}",
         summary='Get the specimen_ids from the dataset with the given dataset_id',
         response_description='A list of specimen_ids',
         tags=['get'])
async def get_specimens(dataset_id: Annotated[str, Path(description='The dataset ID')]):

    ds = get_ds(dataset_id)
    if not ds:
        return {"message": "Dataset not found"}

    return [s['specimen_id'] for s in ds[0]['specimens']]


@app.get("/v1/specimen/{dataset_id}/{specimen_id}",
         summary='Get specimen data with the given dataset_id and specimen_id',
         response_description=f'A specimen dataset structured as per the echoSMs data store [schema]({schema_url})',
         tags=['get'])
async def get_specimen(dataset_id: Annotated[str, Path(description='The dataset ID')],
                       specimen_id: Annotated[str, Path(description='The specimen ID')]):

    ds = get_ds(dataset_id)
    if not ds:
        return {"message": "Dataset not found"}

    return get_sp(ds[0], specimen_id)


@app.get("/v1/specimen_image/{dataset_id}/{specimen_id}",
         summary='Get an image of the specimen shape, with the given dataset_id and specimen_id',
         response_description='An image of the specimen shape',
         tags=['get'],
         response_class=Response,
         responses = {200: {'content': {'image/png': {}}}})
async def get_specimen_image(dataset_id: Annotated[str, Path(description='The dataset ID')],
                             specimen_id: Annotated[str, Path(description='The specimen ID')]):

    ds = get_ds(dataset_id)
    if ds:
        s = get_sp(ds[0], specimen_id)
        if s:
            img = plot_specimen(s[0], dataset_id=ds[0]['dataset_id'], stream=True)
            return Response(img, media_type="image/png")
        

def get_ds(dataset_id):
    """Find datasets with given dataset_id."""
    return [ds for ds in all_datasets if ds['dataset_id'] == dataset_id]


def get_sp(ds, specimen_id):
    """Find specimen with given specimen_id in the given dataset"""
    return [s for s in ds['specimens'] if s['specimen_id'] == specimen_id]


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
