# -*- python -*-
#
#       Copyright 2016 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       WebSite : https://github.com/openalea-incubator/astk
#
#       File author(s): Christian Fournier <Christian.Fournier@supagro.inra.fr>
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
    return azimuth, zenith , az_c, z_c


def show_sky(grid, sky, cmap='jet', shading='flat'):
    """Display sky luminance polar image

    Args:
        grid: a (azimuth, zenith, az_c, z_c) tuple, such as returned by sky_grid
        sky: a 2-D array of values to be plotted on the grid
    """
    az, z, _, _ = grid
    theta = numpy.radians(az)
    r = z
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.pcolormesh(theta, r, sky, edgecolors='face', cmap=cmap, shading=shading)
    plt.show()


