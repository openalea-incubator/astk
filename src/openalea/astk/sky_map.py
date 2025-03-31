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
    # grid cell relative area on sky hemisphere
    w_c = numpy.radians(d_az) * (numpy.cos(numpy.radians(z_c - d_z / 2)) - numpy.cos(numpy.radians(z_c + d_z / 2)))
    return azimuth, zenith , az_c, z_c, w_c


def closest_point(point_grid, point_list):
    dists = [numpy.sum((point_grid - p)**2, axis=2) for p in point_list]
    return numpy.argmin(numpy.stack(dists, axis=2), axis=2)


def sky_map(grid, luminance_map, directions):
    _, _, az, z, wc = grid

    def _polar(az, z):
        # az is from north, positive clockwise.
        # Theta is from x+ positive counter-clockwise
        # north is along Y+
        theta = numpy.pi / 2 - numpy.radians(az)
        return z * numpy.cos(theta), z * numpy.sin(theta)

    grid_points = numpy.stack(_polar(az, z), axis=2)
    target_points = numpy.array([_polar(a, 90 - el) for el, a in directions])
    targets = closest_point(grid_points, target_points)
    wlum = luminance_map * wc
    slum = numpy.bincount(targets.flatten(), weights=wlum.flatten())
    slum /= numpy.bincount(targets.flatten(), weights=wc.flatten())
    smap = numpy.zeros_like(luminance_map)
    for i, w in enumerate(slum):
        smap[targets==i] = w
    smap *= luminance_map.sum() / smap.sum()
    return slum, smap


def show_sky(grid, sky, cmap='jet', shading='flat'):
    """Display sky luminance polar image

    Args:
        grid: a (azimuth, zenith, az_c, z_c) tuple, such as returned by sky_grid
        sky: a 2-D array of values to be plotted on the grid
    """
    az, z, _, _ , _= grid
    theta = numpy.pi/2 - numpy.radians(az)
    r = z
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.pcolormesh(theta, r, sky, edgecolors='face', cmap=cmap, shading=shading)
    plt.show()


