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

"""Creation and plotting of sky maps
"""
import numpy
from matplotlib import pyplot as plt


def sky_grid(d_az=1, d_z=1, n_az=None, n_z=None):
    """Azimuth and zenital grid coordinates"""
    def _c(x):
        return (x[:-1] + x[1:]) / 2
    # grid cell boundaries
    if n_az is None:
        azimuth = numpy.linspace(0, 360, 360 // d_az + 1)
    else:
        azimuth = numpy.linspace(0, 360, n_az + 1)
    if n_z is None:
        zenith = numpy.linspace(0, 90, 90 // d_z + 1)
    else:
        zenith = numpy.linspace(0, 90, n_z + 1)

    # grid cell centers positioned in a 2D grid matrix
    az_c, z_c = numpy.meshgrid(_c(azimuth), _c(zenith))
    # grid cell relative area on sky hemisphere
    w_c = numpy.radians(d_az) * (numpy.cos(numpy.radians(z_c - d_z / 2)) - numpy.cos(numpy.radians(z_c + d_z / 2)))
    return azimuth, zenith , az_c, z_c, w_c


def sky_dirs(d_az=10, d_z=10, n_az=None, n_z=None):
    _,_,az, z, _ = sky_grid(d_az=d_az, d_z=d_z, n_az=n_az, n_z=n_z)
    return [*zip(90 - z.flatten(), az.flatten())]


def sun_path(sky_irradiance):
    irr = sky_irradiance
    return [*zip(irr.sun_elevation, irr.sun_azimuth)]


def sky_turtle(sectors=46):
    # Hierarchical direction from tutle.xls file of J Dauzat
    elevations_h = [90.] + [26.57] * 5 + [52.62] * 5 + [10.81] * 5 + [69.16] * 5 + [
        47.41] * 5 + [31.08] * 10 + [9.23] * 10
    az1 = [0, 72, 144, 216, 288]
    az2 = [36, 108, 180, 252, 324]
    azimuths_h = [180.] + az1 + az2 * 2 + az1 * 2 + [
        23.27, 48.73, 95.27, 120.73, 167.27, 192.73, 239.27, 264.73, 311.27, 336.73] + [
        12.23, 59.77, 84.23, 131.77, 156.23, 203.77, 228.23, 275.77, 300.23, 347.77]
    nb_sect = [1, 6, 16, 46][numpy.searchsorted([1, 6, 16, 46], min(46, sectors))]
    return [*zip(elevations_h[:nb_sect], azimuths_h[:nb_sect])]


def closest_point(point_grid, point_list):
    dists = [numpy.sum((point_grid - p)**2, axis=2) for p in point_list]
    return numpy.argmin(numpy.stack(dists, axis=2), axis=2)


def sky_map(luminance_grid, luminance_map, directions):
    _, _, az, z, _ = luminance_grid

    def _polar(az, z):
        theta = numpy.radians(az)
        return z * numpy.cos(theta), z * numpy.sin(theta)

    grid_points = numpy.stack(_polar(az, z), axis=2)
    target_points = numpy.array([_polar(a,90- el) for el,a in directions])
    targets = closest_point(grid_points, target_points)
    slum = numpy.bincount(targets.flatten(), weights=luminance_map.flatten())
    smap = numpy.zeros_like(luminance_map)
    for i, w in enumerate(slum):
        smap[targets==i] = w
    elevation, azimuth= zip(*directions)
    sky_sources = list(zip(elevation, azimuth, slum))
    return sky_sources, smap


def show_sky(grid, sky, cmap='jet', shading='flat'):
    """Display sky luminance polar image

    Args:
        grid: a (azimuth, zenith, az_c, z_c) tuple, such as returned by sky_grid
        sky: a 2-D array of values to be plotted on the grid
    """
    az, z, _, _ , _= grid
    theta = numpy.radians(az)
    r = z
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.pcolormesh(theta, r, sky, edgecolors='face', cmap=cmap, shading=shading)
    plt.show()


