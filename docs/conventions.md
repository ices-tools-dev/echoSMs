# Conventions

## Units

We use SI units for the model parameters, except for angles (degrees instead of radians) and target strength (deciBels).  All model code must accept inputs and produce results using the units below. If the model calculations use different units internally, the code should internally convert between them.

| Parameter | Units | Notes |
|-----------|-------|--|
|length, diameter, radius, thickness, etc|m||
|density|kg/m³||
|sound speed|m/s||
|angle|°|See [Coordinate systems][coordinate-systems]|
|frequency|Hz||
|target strength|dB|reference value is 1 m²|

## Coordinate systems

The right-handed cartesian coordinate system as defined by ISO 80000-2[^1] is to be used, as illustrated below. The acoustic wave is defined to always travel in the positive _z_ direction and the organism is rotated to achieve different acoustic incidence angles.

The [Tait-Bryan](https://en.wikipedia.org/wiki/Euler_angles#Tait–Bryan_angles) _z_-_y'_-_x''_ (intrinsic) convention was chosen to represent organism rotations as it is commonly used in nautical situations. Intrinsic means that the rotations are about the axes of the rotating organism, rather than the original coordinate system. The order of rotations is _z_, then _y_, then _x_.

Rotations about the _z_-axis are yaw (_ψ_), about the _y_-axis are pitch (_θ_), and about the _x_-axis are roll (_ɸ_). The definitions are such that:

- A yaw (_ψ_) value of 0° occurs when the organism lies along the positive _x_-axis (as per the illustration) and positive yaw values (as per the yellow arrow) rotate the organism's head towards the positive _y_-axis,
- Pitch (_θ_) values of 0°, 90°, and 180° correspond to acoustic wave incidence angles of head on, dorsal, and tail on, respectively,
- Roll (_ɸ_) values of –90°, 0°, and 90° correspond to acoustic wave incidences onto the right (starboard), dorsal, and left (port) sides of the organism, respectively.

All model code should accept angles and produce results in this coordinate system. If the model calculations use a different coordinate system, the code should internally convert between the system given above and the version used in the code.

<!--- This code will include an html file, originally used to
include a live 3D view of the coordinate system, but there are
issues with the html so for the moment a 2D image is used.
<p align="center">
<iframe src="../coordinate_system2.html" title="Coordinate system" width="100%" height="500" frameborder="0"></iframe>
</p>
--->

![The coordinate system](resources/coordinate_system_light.svg#only-light)
![The coordinate system](resources/coordinate_system_dark.svg#only-dark)

### Coordinate conversions

Some models use an incident wave vector instead of rotating the target. The appropriate
vector for a given echoSMs yaw, pitch, and roll can be calculated using this Python code:

```
from scipy.spatial.transform import Rotation as R
rot = R.from_euler('ZYX', (yaw, theta-90, -phi), degrees=True)  # angles in degrees
incident_vector = rot.apply([0, 0, 1])
```

## Code style

Contributions of code should follow standardised or community-agreed styles and be provided in (or added to) a structure suitable for packaging and uploading to package libraries. For Python this includes `pip` and/or `conda`, for R this would be `CRAN`, for Matlab this would be a toolbox on the MATLAB File Exchange, etc.

Python code should follow [PEP8](https://peps.python.org/pep-0008) and docstrings should use [PEP257](https://peps.python.org/pep-0257/) with the contents following the [numpydoc style](https://numpydoc.readthedocs.io/en/latest/format.html). An exception to PEP8 is made to allow lines of up to 100 characters.

[^1]: [ISO. 2019.](https://www.iso.org/obp/ui/en/#iso:std:iso:80000:-2:ed-2:v2:en) ISO 80000-2. Part 2: Mathematics.
