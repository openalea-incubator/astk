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
""" A collection of equation for modelling distribution of sky luminance
"""
from __future__ import division

import numpy
from matplotlib import pyplot as plt

from alinea.astk.meteorology.sky_irradiance import horizontal_irradiance, all_weather_sky_clearness, f_clear_sky


def cie_luminance_gradation(z, a=4, b=-0.7):
    """ function giving the dependence of the luminance of a sky element
    to its zenith angle

    CIE, 2002, Spatial distribution of daylight CIE standard general sky,
    CIE standard, CIE Central Bureau, Vienna

    z : zenith angle of the sky element (deg)
    a, b : coefficient for the type of sky
    """
    def _f(z):
        return 1 + numpy.where(z == 90, 0,
                               a * numpy.exp(b / numpy.cos(numpy.radians(z))))
    return _f(z) / _f(0)


def _ksi(sky_zenith, sky_azimuth, sun_zenith=0, sun_azimuth=0):
    """acute angle between an array of sky elements and the sun """

    def _xyz(zenith, azimuth):
        theta = numpy.radians(zenith)
        phi = numpy.radians(azimuth)
        return (numpy.sin(theta) * numpy.cos(phi),
                numpy.sin(theta) * numpy.sin(phi),
                numpy.cos(theta))

    def _angle3(v1, v2):
        """acute angle between 2 3d vectors"""
        x = numpy.dot(v1, v2) / (numpy.linalg.norm(v1, axis=2) * numpy.linalg.norm(v2))
        angle = numpy.arccos(numpy.clip(x, -1, 1))
        return numpy.degrees(angle)

    v_sky = numpy.stack(_xyz(sky_zenith, sky_azimuth), axis=2)
    v_sun = _xyz(sun_zenith, sun_azimuth)

    return _angle3(v_sky, v_sun)


def cie_scattering_indicatrix(ksi, ksi_sun=0, c=10, d=-3, e=-0.45):
    """ function giving the dependence of the luminance
    to its angular distance to the sun

    CIE, 2002, Spatial distribution of daylight CIE standard general sky,
    CIE standard, CIE Central Bureau, Vienna

    ksi: angular distance to the sun (deg)
    ksi_sun: angular distance of zenith to the sun, ie zenith angle of the sun (deg)
    c, d, e : coefficient for the type of sky
    """
    def _f(k):
        ksi_r = numpy.radians(k)
        return 1 + c * (
            numpy.exp(d * ksi_r) - numpy.exp(d * numpy.pi / 2)) + e * numpy.power(
        numpy.cos(ksi_r), 2)
    return _f(ksi) / _f(ksi_sun)


def cie_relative_luminance(sky_zenith, sky_azimuth=None, sun_zenith=None,
                           sun_azimuth=None, type='soc'):
    """ cie relative luminance of a sky element relative to the luminance
    at zenith

    sky_zenith : zenith angle of the sky element (deg)
    sky_azimuth: azimuth angle of the sky element (deg)
    sun_zenith : zenith angle of the sun (deg)
    sun_azimuth: azimuth angle of the sun (deg)
    type is one of 'soc' (standard overcast sky), 'uoc' (uniform radiance)
    or 'clear_sky' (standard clear sky low turbidity)
    """

    if type == 'clear_sky' and (
                sun_zenith is None or sun_azimuth is None or sky_azimuth is None):
        raise ValueError('Clear sky requires sun position')

    if type == 'soc':
        ab = {'a': 4, 'b': -0.7}
    elif type == 'uoc':
        ab = {'a': 0, 'b': -1}
    elif type == 'clear_sky':
        ab = {'a': -1, 'b': -0.32}
    else:
        raise ValueError('unknown sky_type:' + type)

    gradation = cie_luminance_gradation(numpy.array(sky_zenith), **ab)

    indicatrix = 1
    if type == 'clear_sky':
        cde = {'c': 10, 'd': -3, 'e': 0.45}
        ksi_sun = sun_zenith
        ksi = _ksi(sky_zenith, sky_azimuth, sun_zenith, sun_azimuth)
        indicatrix = cie_scattering_indicatrix(ksi, ksi_sun=ksi_sun, **cde)

    return gradation * indicatrix


def sky_grid(daz=1,dz=1):
    """Azimuth and zenital grid coordinates"""
    def _c(x):
        return (x[:-1] + x[1:]) / 2
    # grid cell boundaries
    azimuth = numpy.linspace(0, 360, 360 // daz + 1)
    zenith = numpy.linspace(0, 90, 90 // dz + 1)
    # grid cell centers positioned in a 2D grid matrix
    az_c, z_c = numpy.meshgrid(_c(azimuth), _c(zenith))
    return azimuth, zenith , az_c, z_c


def sky_luminance(sky_type='soc', sky_irradiance=None, da=1):
    """Sky luminance map for different conditions and sky types

    Args:
        sky_type (str): sky type, one of ('soc', 'uoc', 'clear_sky', 'sun_soc', 'blended')
        sky_irradiance: a datetime indexed dataframe specifying sky irradiances for the period, such as returned by
        astk.sky_irradiance.sky_irradiances. Needed for all sky_types except 'uoc' and 'soc'
    """

    azimuth, zenith, az_c, z_c = sky_grid(daz=da, dz=da)
    lum = numpy.zeros_like(azimuth)
    hi = 0
    # set diffuse part, if any
    if sky_type != 'clear_sky':
        t = 'soc'
        if sky_type == 'uoc':
            t = 'uoc'
        lum = cie_relative_luminance(z_c, az_c, type=t)
        lum /= lum.sum()
        hi = horizontal_irradiance(lum, 90 - z_c).sum()
    # add sun-related part, if any
    if sky_type in ('clear_sky', 'sun_soc', 'blended'):
        assert sky_irradiance is not None
        if sky_type == 'sun_soc':
            # scale diffuse part to sum of diffuse irradiance
            lum *= (sky_irradiance.dhi.sum() / hi)
            for row in sky_irradiance.itertuples():
                i, j = int(row.sun_zenith // da), int(row.sun_azimuth // da)
                lum[i, j] += row.dni
            lum /= lum.sum()
            hi = horizontal_irradiance(lum, 90 - z_c).sum()
        else:
            if sky_type == 'blended':
                epsilon = all_weather_sky_clearness(sky_irradiance.dni, sky_irradiance.dhi, sky_irradiance.sun_zenith)
                f_soc = 1 - f_clear_sky(epsilon)
                # scale diffuse part
                lum *= (sky_irradiance.ghi / hi * f_soc).sum()
            for row in sky_irradiance.itertuples():
                _lum = cie_relative_luminance(z_c, az_c,
                                                   sun_zenith=row.sun_zenith,
                                                   sun_azimuth=row.sun_azimuth,
                                                   type='clear_sky')
                _lum /= _lum.sum()
                _hi = horizontal_irradiance(_lum, 90 - z_c).sum()
                if sky_type == 'clear_sky':
                    lum += (row.ghi / _hi * _lum)
                elif sky_type == 'blended':
                    epsilon = all_weather_sky_clearness(row.dni, row.dhi,row.sun_zenith)
                    lum += (row.ghi / _hi * _lum * f_clear_sky(epsilon))
                else:
                    raise ValueError('undefined direct lightning strategy for sky type: ' + sky_type)
            lum /= lum.sum()
            hi = horizontal_irradiance(lum, 90 - z_c).sum()
    return azimuth, zenith, lum, hi


def show_sky(sky, cmap='jet', shading='flat'):
    """Display sky luminance polar image

    Args:
        sky: a azimuth, zenith, luminance tuple
    """
    az, z, lum, _ = sky
    theta = numpy.radians(az)
    r = z
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.pcolormesh(theta, r, lum, edgecolors='face', cmap=cmap, shading=shading)
    plt.show()



