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
import numpy
from alinea.astk.meteorology.sky_irradiance import (horizontal_irradiance, all_weather_sky_clearness, f_clear_sky,
                                                    all_weather_sky_brightness)


def sky_hi(grid, luminance):
    _, _, _, sky_zenith, _ = grid
    return horizontal_irradiance(luminance, 90 - sky_zenith).sum()


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


def cie_relative_luminance(sky_zenith=None, grid=None, sun_zenith=None,
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

    if sky_zenith is None and grid is None:
        raise ValueError('Either sky_zenith or grid should be passed')
    sky_azimuth = None
    if grid is not None:
        _, _, _, sky_zenith, _ = grid
    else:
        sky_zenith = numpy.array(sky_zenith)

    if type == 'soc':
        ab = {'a': 4, 'b': -0.7}
    elif type == 'uoc':
        ab = {'a': 0, 'b': -1}
    elif type == 'clear_sky':
        ab = {'a': -1, 'b': -0.32}
    else:
        raise ValueError('unknown sky_type:' + type)

    gradation = cie_luminance_gradation(sky_zenith, **ab)

    indicatrix = 1
    if type == 'clear_sky':
        cde = {'c': 10, 'd': -3, 'e': 0.45}
        ksi_sun = sun_zenith
        ksi = ksi_grid(grid, sun_zenith, sun_azimuth)
        indicatrix = cie_scattering_indicatrix(ksi, ksi_sun=ksi_sun, **cde)

    return gradation * indicatrix


def all_weather_abcde(sun_zenith, clearness, brightness):
    """Parameters of the all weather sky model (Perez et al. 1993)

    Args:
        sun_zenith: zenith angle of the sun (deg)
        clearness: sky clearness as defined in Perez et al. (1993
        brightness: sky brightness as defined in Perez et al. (1993)

    Returns:
        a tuple of 5 parameters to be used by CIE sky luminance functions

    Details:
        R. Perez, R. Seals, J. Michalsky, "All-weather model for sky luminance distribution—Preliminary configuration and
        validation", Solar Energy, Volume 50, Issue 3, 1993, Pages 235-245,
    """

    def _awfit(p1, p2, p3, p4, zen, br):
        p1 = numpy.array(p1)
        p2 = numpy.array(p2)
        p3 = numpy.array(p3)
        p4 = numpy.array(p4)
        return p1 + p2 * zen + br * (p3 + p4 * zen)

    bins = [1, 1.065, 1.23, 1.5, 1.95, 2.8, 4.5, 6.2]
    a1 = (1.3525, -1.2219, -1.1000, -0.5484, -0.6000, -1.0156, -1.0000, -1.0500)
    a2 = (-0.2576, -0.7730, -0.2215, -0.6654, -0.3566, -0.3670, 0.0211, 0.0289)
    a3 = (-0.2690, 1.4148, 0.8952, -0.2672, -2.5000, 1.0078, 0.5025, 0.4260)
    a4 = (-1.4366, 1.1016, 0.0156, 0.7117, 2.3250, 1.4051, -0.5119, 0.3590)
    b1 = (-0.7670, -0.2054, 0.2782, 0.7234, 0.2937, 0.2875, -0.3000, -0.3250)
    b2 = (0.0007, 0.0367, -0.1812, -0.6219, 0.0496, -0.5328, 0.1922, 0.1156)
    b3 = (1.2734, -3.9128, -4.5000, -5.6812, -5.6812, -3.8500, 0.7023, 0.7781)
    b4 = (-0.1233, 0.9156, 1.1766, 2.6297, 1.8415, 3.3750, -1.6317, 0.0025)
    c1 = (2.8000, 6.9750, 24.7219, 33.3389, 21.0000, 14.0000, 19.0000, 31.0625)
    c2 = (
        0.6004, 0.1774, -13.0812, -18.3000, -4.7656, -0.9999, -5.0000, -14.5000)
    c3 = (
        1.2375, 6.4477, -37.7000, -62.2500, -21.5906, -7.1406, 1.2438, -46.1148)
    c4 = (1.0000, -0.1239, 34.8438, 52.0781, 7.2492, 7.5469, -1.9094, 55.3750)
    d1 = (1.8734, -1.5798, -5.0000, -3.5000, -3.5000, -3.4000, -4.0000, -7.2312)
    d2 = (0.6297, -0.5081, 1.5218, 0.0016, -0.1554, -0.1078, 0.0250, 0.4050)
    d3 = (0.9738, -1.7812, 3.9229, 1.1477, 1.4062, -1.0750, 0.3844, 13.3500)
    d4 = (0.2809, 0.1080, -2.6204, 0.1062, 0.3988, 1.5702, 0.2656, 0.6234)
    e1 = (0.0356, 0.2624, -0.0156, 0.4659, 0.0032, -0.0672, 1.0468, 1.5000)
    e2 = (-0.1246, 0.0672, 0.1597, -0.3296, 0.0766, 0.4016, -0.3788, -0.6426)
    e3 = (-0.5718, -0.2190, 0.4199, -0.0876, -0.0656, 0.3017, -2.4517, 1.8564)
    e4 = (0.9938, -0.4285, -0.5562, -0.0329, -0.1294, -0.4844, 1.4656, 0.5636)

    index = max(0, numpy.searchsorted(bins, clearness) - 1)
    z = numpy.radians(sun_zenith)
    a = _awfit(a1, a2, a3, a4, z, brightness)[index]
    b = _awfit(b1, b2, b3, b4, z, brightness)[index]
    c = _awfit(c1, c2, c3, c4, z, brightness)[index]
    d = _awfit(d1, d2, d3, d4, z, brightness)[index]
    e = _awfit(e1, e2, e3, e4, z, brightness)[index]

    if clearness <= 1.065:
        c = numpy.exp(numpy.power(brightness * (c1[0] + c2[0] * z), c3[0])) - \
            c4[0]
        d = -numpy.exp(brightness * (d1[0] + d2[0] * z)) + d3[0] + d4[
                                                                       0] * brightness

    return a, b, c, d, e


def ksi_grid(grid, sun_zenith=0, sun_azimuth=0):
    """acute angle between an array of sky elements and the sun """

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

    _, _, sky_azimuth, sky_zenith, _ = grid
    v_sky = numpy.stack(_cartesian(sky_zenith, sky_azimuth), axis=2)
    v_sun = _cartesian(sun_zenith, sun_azimuth)

    return _acute(v_sky, v_sun)


def all_weather_relative_luminance(grid, sun_zenith, sun_azimuth, clearness, brightness):
    """All weather relative luminance of a sky element relative to the luminance
    at zenith

    Args:
        grid: a (azimuth, zenith, az_c, z_c) tuple, such as returned by astk.sky_grid
        sun_zenith : zenith angle of the sun (deg)
        sun_azimuth: azimuth angle of the sun (deg)
        clearness: sky clearness as defined in Perez et al. (1993
        brightness: sky brightness as defined in Perez et al. (1993)

        Details:
            R. Perez, R. Seals, J. Michalsky, "All-weather model for sky luminance distribution—Preliminary configuration and
            validation", Solar Energy, Volume 50, Issue 3, 1993, Pages 235-245,

    """
    a, b, c, d, e = all_weather_abcde(sun_zenith, clearness, brightness)
    _, _, _, sky_zenith, _ = grid
    gradation = cie_luminance_gradation(sky_zenith, a=a, b=b)
    ksi_sun = sun_zenith
    ksi = ksi_grid(grid, sun_zenith, sun_azimuth)
    indicatrix = cie_scattering_indicatrix(ksi, ksi_sun=ksi_sun, c=c, d=d, e=e)

    return gradation * indicatrix


def sky_luminance(grid, sky_type='soc', sky_irradiance=None):
    """Relative sky luminance map for different conditions, periods and sky types
       Luminance are scaled so that total sky horizontal irradiance equals one.

    Args:
        sky_type (str): sky type, one of ('soc', 'uoc', 'clear_sky', 'blended', 'all_weather')
        sky_irradiance: a datetime indexed dataframe specifying sky irradiances for the period, such as returned by
        astk.sky_irradiance.sky_irradiance. Needed for all sky_types except 'uoc' and 'soc'
    """

    azimuth, zenith, az_c, z_c, w_c = grid
    lum = numpy.zeros_like(az_c)
    if sky_irradiance is not None:
        irrad = sky_irradiance.copy()
        irrad['dates'] = irrad.index

    if sky_type in ('soc', 'uoc'):
        lum = w_c * cie_relative_luminance(grid=grid, type=sky_type)
    elif sky_type == 'clear_sky':
        for row in irrad.itertuples():
            _lum = w_c * cie_relative_luminance(grid=grid,
                                          sun_zenith=row.sun_zenith,
                                          sun_azimuth=row.sun_azimuth,
                                          type='clear_sky')
            _hi = sky_hi(grid, _lum)
            lum += (row.ghi / _hi * _lum)
    elif sky_type == 'all_weather':
        for row in irrad.itertuples():
            brightness = all_weather_sky_brightness(row.dates, row.dhi, row.sun_zenith)
            clearness = all_weather_sky_clearness(row.dni, row.dhi, row.sun_zenith)
            _lum = w_c * all_weather_relative_luminance(grid,
                                                  sun_zenith=row.sun_zenith,
                                                  sun_azimuth=row.sun_azimuth,
                                                  brightness=brightness,
                                                  clearness=clearness)
            _hi = sky_hi(grid, _lum)
            lum += (row.ghi / _hi * _lum)
    elif sky_type == 'blended':
        soc = w_c * cie_relative_luminance(grid=grid, type='soc')
        for row in irrad.itertuples():
            cs = w_c * cie_relative_luminance(grid=grid,
                                          sun_zenith=row.sun_zenith,
                                          sun_azimuth=row.sun_azimuth,
                                          type='clear_sky')
            epsilon = all_weather_sky_clearness(row.dni, row.dhi, row.sun_zenith)
            f_clear = f_clear_sky(epsilon)
            _lum = f_clear * cs + (1 - f_clear) * soc
            _hi = sky_hi(grid, _lum)
            lum += (row.ghi / _hi * _lum)
    else:
        raise ValueError('undefined sky type: ' + sky_type)

    # scale so that ghi = 1
    hi = sky_hi(grid, lum)
    return lum / hi


def scale_sky_sources(sky_sources, sky_irradiance, scale='Wm2', diffuse_only=False):
    """Scale relative luminance values to a given scale depending on horizontal irradiance time series

    Args:
        sky_sources: a list of (elevation, azimuth, luminance) tuples
        sky_irradiance: a datetime indexed dataframe specifying sky irradiances for the period, such as returned by
        astk.sky_irradiance.sky_irradiance.
    ky_irradiance: a datetime indexed dataframe specifying sky irradiances for the period, such as returned by
        astk.sky_irradiance.sky_irradiance
    """
    el, az, lum = zip(*sky_sources)
    # rescale to horizontal irradiance = 1
    hi = sum((horizontal_irradiance(l, e) for l, e in zip(lum, el)))
    lum = numpy.array(lum) / hi
    # Scale to new unit
    if scale == 'PPFD':
        lum *= sky_irradiance.ppfd.mean()
    elif scale == 'Wm2':
        lum *= sky_irradiance.ghi.mean()
    elif scale == 'MJ':
        lum *= sky_irradiance.ghi.sum() * 3600 / 1e6
    elif scale == 'molPAR':
        lum *= sky_irradiance.ppfd.sum() * 3600 / 1e6
    else:
        raise ValueError('undefined scale: ' + scale + '. Should be one of PPFD, Wm2, MJ, molPAR')
    if diffuse_only:
        lum *= sky_irradiance.dhi.sum() / sky_irradiance.ghi.sum()

    return list(zip(el, az, lum))


