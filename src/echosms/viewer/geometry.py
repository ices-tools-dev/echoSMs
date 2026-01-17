import numpy as np


def generate_sphere(radius, num_points=100):
    """Generate KRM-style sphere data."""
    # Centered at 0
    x = np.linspace(-radius, radius, num_points)
    val = radius**2 - x**2
    val[val < 0] = 0
    z = np.sqrt(val)

    return {
        "name": f"Sphere (a={radius*100:.1f}cm)",
        "x_b": x.tolist(),
        "z_bU": z.tolist(),
        "z_bL": (-z).tolist(),
        "w_b": (2*z).tolist(),
        "x_sb": [], "z_sbU": [], "z_sbL": [], "w_sb": []
    }


def generate_prolate_spheroid(minor_radius, length, num_points=100):
    """Generate KRM-style prolate spheroid data."""
    major_radius = length / 2.0
    x = np.linspace(-major_radius, major_radius, num_points)
    val = 1 - (x/major_radius)**2
    val[val < 0] = 0
    z = minor_radius * np.sqrt(val)

    return {
        "name": f"Prolate Spheroid (a={minor_radius*100:.1f}cm, "
                f"L={length*100:.1f}cm)",
        "x_b": x.tolist(),
        "z_bU": z.tolist(),
        "z_bL": (-z).tolist(),
        "w_b": (2*z).tolist(),
        "x_sb": [], "z_sbU": [], "z_sbL": [], "w_sb": []
    }


def generate_cylinder(radius, length, num_points=100):
    """Generate KRM-style cylinder data."""
    x = np.linspace(0, length, num_points)
    z = np.full_like(x, radius)

    return {
        "name": f"Cylinder (a={radius*100:.1f}cm, L={length*100:.1f}cm)",
        "x_b": x.tolist(),
        "z_bU": z.tolist(),
        "z_bL": (-z).tolist(),
        "w_b": (2*z).tolist(),
        "x_sb": [], "z_sbU": [], "z_sbL": [], "w_sb": []
    }


def generate_bent_cylinder(radius, length, rho_c, num_points=100):
    """Generate DWBA-style bent cylinder data."""
    # Angle subtended
    theta_total = length / rho_c
    t = np.linspace(-theta_total/2, theta_total/2, num_points)

    x_c = rho_c * np.sin(t)
    z_c = rho_c * np.cos(t) - rho_c
    y_c = np.zeros_like(x_c)
    a = np.full_like(x_c, radius)

    name_str = f"Bent Cyl (a={radius*100:.1f}, L={length*100:.1f}, " \
               f"rho={rho_c*100:.1f}cm)"

    return {
        "name": name_str,
        "x": x_c.tolist(),
        "y": y_c.tolist(),
        "z": z_c.tolist(),
        "a": a.tolist()
    }
