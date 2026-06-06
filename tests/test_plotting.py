"""Test plotting of datastore shapes."""

import pytest
from echosms import plot_specimen

@pytest.mark.skip(reason="Not implemented yet")
def plot_geometric():
  s = {
    "uuid": "91984396-2daf-433c-a2ac-55393b9a91b3",
    "version_number": 1,
    "version_time": "2026-04-05T00:00:00Z",
    "version_note": "Initial version",
    "description": [
      "An example of a geometric shape type"
    ],
    "anatomical_category": "other",
    "aphia_id": 0,
    "date_collection": "",
    "date_image": "",
    "imaging_method": "not applicable",
    "shape_method": "other",
    "dataset_size": 0.0,
    "dataset_size_units": "megabyte",
    "specimen_name": "sphere example",
    "specimen_condition": "other",
    "length": 1.0,
    "length_units": "m",
    "length_type": "other",
    "shape_type": "geometric",

  "shapes": [
      {
        "name": "sphere",
        "geometric_form": "spheroid",
        "equatorial_radius": 0.07,
        "polar_radius": 0.07,
        "origin_location_units": "m",
        "shape_units": "m",
        "anatomical_feature": "other"
      },
      {
        "geometric_form": "cylinder",
        "radius": 0.07,
        "length": 0.15,
        "origin_location_units": "m",
        "shape_units": "m",
        "anatomical_feature": "other"
      },
      {
        "geometric_form": "cylinder",
        "radius": 0.05,
        "length": 0.1,
        "origin_location": [
          0.1,
          0.1,
          0.1
        ],
        "pitch": 45,
        "orientation_units": "degrees",
        "origin_location_units": "m",
        "shape_units": "m",
        "anatomical_feature": "other"
      }
    ]
      }


  plot_specimen(s)
