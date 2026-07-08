"""Test plotting of datastore shapes."""

import pytest
from echosms import plot_specimen

@pytest.mark.skip(reason="Not implemented yet")
def plot_geometric():
    s = {
          "uuid": "91984396-2daf-433c-a2ac-55393b9a91b3",
          "license": "CC0 1.0",
          "version_number": 1,
          "version_time": "2026-04-05T00:00:00Z",
          "version_note": "Initial version",
          "description": [
            "n example of a geometric shape type, namely a cylinder with spherical endcaps"
          ],
          "anatomical_category": "other",
          "aphia_id": 0,
          "date_collection": "",
          "date_image": "",
          "imaging_method": "not applicable",
          "shape_method": "other",
          "dataset_size": 0.0,
          "dataset_size_units": "megabyte",
          "specimen_name": "geometric example",
          "specimen_condition": "other",
          "length": 1.0,
          "length_units": "m",
          "length_type": "other",
          "shape_type": "geometric",
          "shapes": [
            {
              "name": "cylinder with endcaps",
              "anatomical_feature": "body",
              "orientation_units": "degrees",
              "shape_units": "m",
              "mass_density": 1024,
              "mass_density_units": "kg/m^3",
              "sound_speed_compressional": 1460,
              "sound_speed_compressional_units": "m/s",
              "components": [
                {
                  "component_shape": "spheroid",
                  "equatorial_radius": 0.05,
                  "polar_radius": 0.05,
                  "centroid_location": [
                    0.125,
                    0,
                    0
                  ]
                },
                {
                  "component_shape": "spheroid",
                  "equatorial_radius": 0.05,
                  "polar_radius": 0.05,
                  "centroid_location": [
                    -0.125,
                    0,
                    0
                  ]
                },
                {
                  "component_shape": "cylinder",
                  "radius": 0.05,
                  "length": 0.25
                }
              ]
            }
          ]
        }

    plot_specimen(s)
