# -*- python -*-
#
#       Copyright 2016-2025 Inria - CIRAD - INRAe
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       WebSite : https://github.com/openalea/astk
#
#       File author(s): Christian Fournier <christian.fournier@inrae.fr>
#
# ==============================================================================

"""Creation, aggregation and plotting of sky maps
"""
import numpy
import warnings
matplotlib_installed=True
try:
    from matplotlib import pyplot as plt
except ImportError:
    matplotlib_installed = False
    warnings.warn('matplotlib not found: consider installation before calling plotting functions')


def sky_grid(d_az=1, d_z=1, n_az=None, n_z=None):
    """Sky grid creation

    Args:
        d_az: delta azimuth of grid cells
        d_z: delta zenith of grid cells
        n_az: number of cells in azimutal directions
        n_z: number of cells in zenital directions

    Returns:
        az_c: coordinate matrix of azimuth of grid cells center
        z_c: coordinate matrix of zenith of grid cells center
        sr_c: coordinate matrix of sky vault steradians covered by grid cells
    """
    def _c(x):
        return (x[:-1] + x[1:]) / 2
    # grid cell boundaries
    if n_az is None:
        azimuth = numpy.linspace(0, 360, 360 // d_az + 1)
        n_az = len(azimuth) - 1
    else:
        azimuth = numpy.linspace(0, 360, n_az + 1)
    if n_z is None:
        zenith = numpy.linspace(0, 90, 90 // d_z + 1)
        n_z = len(zenith) - 1
    else:
        zenith = numpy.linspace(0, 90, n_z + 1)

    # grid cell centers positioned in a 2D grid matrix
    az_c, z_c = numpy.meshgrid(_c(azimuth), _c(zenith))
    d_az = numpy.ones_like(az_c)
    d_z = numpy.ones_like(az_c)
    d_az *= 360 / n_az
    d_z *= 90 / n_z
    # steradians of sky vault covered by grid cells
    sr_c = numpy.radians(d_az) * (numpy.cos(numpy.radians(z_c - d_z / 2)) - numpy.cos(numpy.radians(z_c + d_z / 2)))

    return az_c, z_c, sr_c


def cell_boundaries(grid):
    """Azimuth and zenith boundaries of cells of a grid
    """
    az_c, z_c, _ = grid
    zenith = numpy.append(numpy.floor(z_c[:, 0]), int(numpy.max(z_c)) + 1)
    azimuth = numpy.append(numpy.floor(az_c[0]), int(numpy.max(az_c)) + 1)
    return azimuth, zenith


def sky_hi(grid, luminance):
    """Horizontal irradiance of sky cells

    Args:
        grid: a (az_c, z_c, sr_c) tuple of sky coordinates, such as returned by astk.sky_map.sky_grid
        luminance : sky luminance gridded array describing distribution of luminance over the sky hemisphere
    """
    az, z, sr = grid
    return luminance * sr * numpy.cos(numpy.radians(z))


def sky_ni(grid, luminance):
    """Direct normal irradiance of sky cells

    Args:
        grid: a (az_c, z_c, sr_c) tuple of sky coordinates, such as returned by astk.sky_map.sky_grid
        luminance : sky luminance gridded array describing distribution of luminance over the sky hemisphere
    """
    az, z, sr = grid
    return luminance * sr

def sky_lum(grid, ni):
    az, z, sr = grid
    return ni / sr


def scale_sky(grid, luminance, irradiance=1):
    """Rescale sky luminance to force producing a given sky irradiance

    Args:
        grid: a (az_c, z_c, sr_c) tuple of sky coordinates, such as returned by astk.sky_map.sky_grid
        luminance: unscaled relative luminance of cells covering sky vault
        irradiance: global horizontal sky irradiance
    """
    az, z, sr = grid
    hi = sky_hi(grid, luminance)
    scaled_hi = hi / hi.sum() * irradiance
    return scaled_hi / sr / numpy.cos(numpy.radians(z))


def closest_point(point_grid, point_list):
    dists = [numpy.sum((point_grid - p)**2, axis=2) for p in point_list]
    return numpy.argmin(numpy.stack(dists, axis=2), axis=2)


def sky_map(grid, luminance, new_directions, force_hi=False):
    """Aggregate luminance for a given new set of directions

    Args:
        grid: a (az_c, z_c, sr_c) tuple of sky coordinates, such as returned by astk.sky_map.sky_grid
        luminance : sky luminance gridded array describing distribution of luminance over the sky hemisphere
        new_directions : a [(elevation, azimuth),..] list of tuples defining directions of the aggregated sky
        force_hi: if True, aggregated luminance are rescaled to force conservation of global horizontal irradiance.
            If False (default), no rescaled is applied

    Returns:
        luminance_agg: luminance aggregated along new directions
        grid_agg: a (azimuth, zenith, sr) tuple describing the aggregated directions and the associated steradians
        luminance_agg_sky: sky aggregated luminance projected on the original sky grid
    """
    az, z, sr = grid

    def _polar(az, z):
        # az is from north, positive clockwise.
        # Theta is from x+ positive counter-clockwise
        # north is along Y+
        theta = numpy.pi / 2 - numpy.radians(az)
        return z * numpy.cos(theta), z * numpy.sin(theta)

    grid_points = numpy.stack(_polar(az, z), axis=2)
    target_points = numpy.array([_polar(a, 90 - el) for el, a in new_directions])
    targets = closest_point(grid_points, target_points)
    light_flux = luminance * sr
    light_flux_agg = numpy.bincount(targets.flatten(), weights=light_flux.flatten())
    sr_agg = numpy.bincount(targets.flatten(), weights=sr.flatten())
    luminance_agg = light_flux_agg / sr_agg
    new_luminance = numpy.zeros_like(luminance)
    for i, w in enumerate(luminance_agg):
        new_luminance[targets == i] = w

    el_agg, az_agg = list(map(numpy.array, zip(*new_directions)))
    grid_agg = (az_agg, 90 - el_agg, sr_agg)

    if force_hi:
        hi = sky_hi(grid, luminance)
        luminance_agg = scale_sky(grid_agg, luminance_agg, hi.sum())
        for i, w in enumerate(luminance_agg):
            new_luminance[targets == i] = w

    return luminance_agg, grid_agg, new_luminance


def ksi_grid(grid, sun_zenith=0, sun_azimuth=0):
    """acute angle between vector pointing to sky cells and sun vector"""
    def _cartesian(zenith, azimuth):
        theta = numpy.radians(zenith)
        phi = numpy.radians(azimuth)
        return (numpy.sin(theta) * numpy.cos(phi),
                numpy.sin(theta) * numpy.sin(phi),
                numpy.cos(theta))

    def _acute(v1, v2):
        """acute angle between 2 3d vectors"""
        x = numpy.dot(v1, v2) / (numpy.linalg.norm(v1, axis=2) * numpy.linalg.norm(v2))
        angle = numpy.arccos(numpy.clip(x, -1, 1))
        return numpy.degrees(angle)

    sky_azimuth, sky_zenith, _ = grid
    v_sky = numpy.stack(_cartesian(sky_zenith, sky_azimuth), axis=2)
    v_sun = _cartesian(sun_zenith, sun_azimuth)

    return _acute(v_sky, v_sun)


def surfacic_irradiance(grid, luminance, zenith=0, azimuth=0):
    """Surfacic light flux traversing a bi-face surfaces whose normals are given by surface orientation"""

    ksi = ksi_grid(grid, zenith, azimuth)
    ni = sky_ni(grid, luminance)

    return (ni * numpy.abs(numpy.cos(numpy.radians(ksi)))).sum()


def uniform_sky():
    grid = sky_grid()
    az_c, z_c, sr_c = grid
    luminance = numpy.ones_like(az_c)
    return grid, luminance


def show_sky(grid, sky, cmap='jet', shading='flat'):
    """Display sky luminance polar image

    Args:
        grid: a (azimuth, zenith, az_c, z_c) tuple, such as returned by sky_grid
        sky: a 2-D array of values to be plotted on the grid
    """
    if not matplotlib_installed:
        warnings.warn('matplotlib not found: consider installation before calling plotting functions')
    az, z = cell_boundaries(grid)
    theta = numpy.pi/2 - numpy.radians(az)
    r = z
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.pcolormesh(theta, r, sky, edgecolors='face', cmap=cmap, shading=shading)
    plt.show()


