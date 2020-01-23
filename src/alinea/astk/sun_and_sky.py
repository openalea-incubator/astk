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
""" A collection of equation for modelling sun position, sun irradiance and sky
irradiance
"""

from __future__ import division
import numpy
import pandas
from alinea.astk.meteorology.sky_irradiance import (
    sky_irradiances,
    clear_sky_irradiances,
    horizontal_irradiance)
from alinea.astk.meteorology.sun_position import sun_position

# default location and dates
_daydate = '2000-06-21'
_timezone = 'Europe/Paris'
_longitude = 3.52
_latitude = 43.36
_altitude = 56


# sky models / equations
def cie_luminance_gradation(sky_elevation, a, b):
    """ function giving the dependence of the luminance of a sky element
    to its elevation angle

    CIE, 2002, Spatial distribution of daylight CIE standard general sky,
    CIE standard, CIE Central Bureau, Vienna

    elevation : elevation angle of the sky element (rad)
    a, b : coefficient for the type of sky
    """
    z = numpy.pi / 2 - numpy.array(sky_elevation)
    phi_0 = 1 + a * numpy.exp(b)
    phi_z = numpy.where(sky_elevation == 0, 1,
                        1 + a * numpy.exp(b / numpy.cos(z)))
    return phi_z / phi_0


def cie_scattering_indicatrix(sun_azimuth, sun_elevation, sky_azimuth,
                              sky_elevation, c, d, e):
    """ function giving the dependence of the luminance
    to its azimuth distance to the sun

    CIE, 2002, Spatial distribution of daylight CIE standard general sky,
    CIE standard, CIE Central Bureau, Vienna

    elevation : elevation angle of the sky element (rad)
    d, e : coefficient for the type of sky
    """
    z = numpy.pi / 2 - numpy.array(sky_elevation)
    zs = numpy.pi / 2 - numpy.array(sun_elevation)
    alpha = numpy.array(sky_azimuth)
    alpha_s = numpy.array(sun_azimuth)
    ksi = numpy.arccos(
        numpy.cos(zs) * numpy.cos(z) + numpy.sin(zs) * numpy.sin(z) * numpy.cos(
            numpy.abs(alpha - alpha_s)))

    f_ksi = 1 + c * (
    numpy.exp(d * ksi) - numpy.exp(d * numpy.pi / 2)) + e * numpy.power(
        numpy.cos(ksi), 2)
    f_zs = 1 + c * (
    numpy.exp(d * zs) - numpy.exp(d * numpy.pi / 2)) + e * numpy.power(
        numpy.cos(zs), 2)

    return f_ksi / f_zs


def cie_relative_luminance(sky_elevation, sky_azimuth=None, sun_elevation=None,
                           sun_azimuth=None, type='soc'):
    """ cie relative luminance of a sky element relative to the luminance
    at zenith

    angle in radians
    type is one of 'soc' (standard overcast sky), 'uoc' (uniform radiance)
    or 'clear_sky' (standard clear sky low turbidity)
    """

    if type == 'clear_sky' and (
                sun_elevation is None or sun_azimuth is None or sky_azimuth is None):
        raise ValueError('Clear sky requires sun position')

    if type == 'soc':
        return cie_luminance_gradation(sky_elevation, 4, -0.7)
    elif type == 'uoc':
        return cie_luminance_gradation(sky_elevation, 0, -1)
    elif type == 'clear_sky':
        return cie_luminance_gradation(sky_elevation, -1,
                                       -0.32) * cie_scattering_indicatrix(
            sun_azimuth, sun_elevation, sky_azimuth, sky_elevation, 10, -3,
            0.45)
    else:
        raise ValueError('Unknown sky type')


def sky_discretisation(turtle_sectors=46, nb_az=None, nb_el=None):
    """ return elevation, azimuth and fraction of sky represented of a turtle sky discretisation

    Parameters
    ----------
    turtle_sectors : the minimal number of sectors to be used for discretising the sky hemisphere. Turtle discretisation
    will be one of 1, 6, 16 or 46 sectors
    nb_az
    nb_el

    Returns
    -------
    elevation, azimuth and fraction of sky discretisation
    """
    # Hierarchical direction from tutle.xls file of J Dauzat
    elevations_h = [90] + [26.57] * 5 + [52.62] * 5 + [10.81] * 5 + [69.16] * 5 + [
        47.41] * 5 + [31.08] * 10 + [9.23] * 10
    az1 = [0, 72, 144, 216, 288]
    az2 = [36, 108, 180, 252, 324]
    azimuths_h = [180] + az1 + az2 * 2 + az1 * 2 + [
        23.27, 48.73, 95.27, 120.73, 167.27, 192.73, 239.27, 264.73, 311.27, 336.73] + [
        12.23, 59.77, 84.23, 131.77, 156.23, 203.77, 228.23, 275.77, 300.23, 347.77]
    nb_sect = [1, 6, 16, 46][numpy.searchsorted([1, 6, 16, 46], min(46, turtle_sectors))]
    # Vegestar vlues
    # elevations46 = [9.23] * 10 + [10.81] * 5 + [26.57] * 5 + [31.08] * 10 + [
    #                 47.41] * 5 + [52.62] * 5 + [69.16] * 5 + [90]
    # azimuths46 = [12.23, 59.77, 84.23, 131.77, 156.23, 203.77, 228.23, 275.77,
    #               300.23, 347.77, 36, 108, 180, 252, 324, 0, 72, 144, 216, 288,
    #               23.27, 48.73, 95.27, 120.73, 167.27, 192.73, 239.27, 264.73,
    #               311.27, 336.73, 0, 72, 144, 216, 288, 36, 108, 180, 252, 324,
    #               0, 72, 144, 216, 288, 180]
    # steradians46 = [0.1355] * 10 + [0.1476] * 5 + [0.1207] * 5 + [
    #                0.1375] * 10 + [0.1364] * 5 + [0.1442] * 5 + [0.1378] * 5 + [
    #                    0.1196]


    sky_fraction = [1. / nb_sect] * nb_sect

    return elevations_h[:nb_sect], azimuths_h[:nb_sect], sky_fraction


def sky_radiance_distribution(sky_elevation, sky_azimuth, sky_fraction,
                              sky_type='soc', sun_elevation=None,
                              sun_azimuth=None, avoid_sun=True):
    """Normalised sky radiance distribution as a function of sky type for a
    finite set of directions sampling the sky hemisphere.

    Args:
        sky_elevation: (float or list of float) elevation (degrees) of directions
            sampling the sky hemisphere
        sky_azimuth: (float or list of float) azimuth (degrees, from North,
            positive clockwise) of directions sampling the sky hemisphere
        sky_fraction: (float or list of float) fraction of sky associated to
            directions sampling the sky hemisphere
        sky_type: (str) one of  'soc' (standard overcast sky),
                                'uoc' (uniform luminance)
                                'clear_sky' (standard clear sky low turbidity)
        sun_elevation: sun elevation (degrees). Only needed for clear_sky
        sun_azimuth: sun azimuth (degrees, from North, positive clockwise).
            Only needed for clear_sky
        avoid_sun (bool): avoid sampling radiance distribution toward directions
        directly pointing to solar disc

    Returns:
        the relative radiance(s) associated to the sky directions
    """

    el = numpy.radians(sky_elevation)
    az = numpy.radians(sky_azimuth)
    sky_fraction = numpy.array(sky_fraction)

    if sun_elevation is not None:
        sun_elevation = numpy.radians(sun_elevation)
    if sun_azimuth is not None:
        sun_azimuth = numpy.radians(sun_azimuth)

    if avoid_sun and sky_type == 'clear_sky':
        delta_el = abs(el - sun_elevation)
        delta_az = abs(az - sun_azimuth)
        sun_disc = numpy.radians(0.553)
        az += numpy.where((delta_az < sun_disc) & (delta_el < sun_disc), sun_disc,
                          0)

    lum = cie_relative_luminance(el, az, sun_elevation, sun_azimuth,
                                 type=sky_type)
    rad_dist = lum * sky_fraction
    rad_dist /= sum(rad_dist)

    return rad_dist


def sun_sources(irradiance=1, dates=None, daydate=_daydate,
                longitude=_longitude, latitude=_latitude, altitude=_altitude,
                timezone=_timezone):
    """ Light sources representing the sun under clear sky conditions

    Args:
        irradiance: (float) sum of horizontal irradiance of sources.
            Using irradiance=1 (default) yields relative contribution of sources.
            If None, clear sky sun horizontal irradiance predicted by
            Perez/Ineichen model is used.
        dates: A pandas datetime index (as generated by pandas.date_range). If
            None, hourly values for daydate are used.
        daydate: (str) yyyy-mm-dd (not used if dates is not None).
        longitude: (float) in degrees
        latitude: (float) in degrees
        altitude: (float) in meter
        timezone:(str) the time zone (not used if dates are already localised)

    Returns:
        elevation (degrees), azimuth (degrees, from North positive clockwise)
        and horizontal irradiance of sources
    """

    c_sky = clear_sky_irradiances(dates=dates, daydate=daydate,
                                  longitude=longitude, latitude=latitude,
                                  altitude=altitude, timezone=timezone)

    sun_irradiance = c_sky['ghi'] - c_sky['dhi']

    if irradiance is not None:
        sun_irradiance /= sum(sun_irradiance)
        sun_irradiance *= irradiance

    # Sr = (1 -cos(cone half angle)) * 2 * pi, frac = Sr / 2 / pi
    # fsun = 1 - numpy.cos(numpy.radians(.53 / 2))
    sun = sun_position(dates=dates, daydate=daydate, latitude=latitude,
                       longitude=longitude, altitude=altitude,
                       timezone=timezone)
    return sun['elevation'].values, sun['azimuth'].values, sun_irradiance.values


def sky_sources(sky_type='soc', irradiance=1, turtle_sectors=46, dates=None, daydate=_daydate,
                longitude=_longitude, latitude=_latitude,
                altitude=_altitude, timezone=_timezone):
    """ Light sources representing standard cie sky types in 46 directions
    Args:
        sky_type:(str) type of sky luminance model. One of :
                           'soc' (standard overcast sky),
                           'uoc' (uniform overcast sky)
                           'clear_sky' (standard clear sky)
        irradiance: (float) sum of horizontal irradiance of all sources. If None
         diffuse horizontal clear_sky irradiance are used for clear_sky type and
          20% attenuated clear_sky global horizontal irradiances are used for
          soc and uoc types.
        turtle_sectors: (int) the minimal number of sectors to be used for sky discretisation
        dates: A pandas datetime index (as generated by pandas.date_range). If
            None, hourly values for daydate are used.
        daydate: (str) yyyy-mm-dd (not used if dates is not None).
        longitude: (float) in degrees
        latitude: (float) in degrees
        altitude: (float) in meter
        timezone:(str) the time zone (not used if dates are already localised)

    Returns:
        elevation (degrees), azimuth (degrees, from North positive clockwise),
        and horizontal irradiance of sources
    """

    source_elevation, source_azimuth, source_fraction = sky_discretisation(turtle_sectors)

    if sky_type == 'soc' or sky_type == 'uoc':
        radiance = sky_radiance_distribution(source_elevation, source_azimuth,
                                             source_fraction,
                                             sky_type=sky_type)
        source_irradiance = horizontal_irradiance(radiance, source_elevation)
        if irradiance is None:
            sky_irradiance = clear_sky_irradiances(dates=dates, daydate=daydate,
                                               longitude=longitude,
                                               latitude=latitude,
                                               altitude=altitude,
                                               timezone=timezone)
            irradiance = sum(sky_irradiance['ghi']) * 0.2

    elif sky_type == 'clear_sky':
        sun = sun_position(dates=dates, daydate=daydate, latitude=latitude,
                           longitude=longitude, altitude=altitude,
                           timezone=timezone)
        c_sky = clear_sky_irradiances(dates=dates, daydate=daydate,
                                      longitude=longitude, latitude=latitude,
                                      altitude=altitude, timezone=timezone)
        c_sky = pandas.concat([sun, c_sky], axis=1)
        if irradiance is None:
            irradiance = sum(c_sky['dhi'])

        # temporal weigths : use dhi (diffuse horizontal irradiance)
        c_sky['wsky'] = c_sky['dhi'] / sum(c_sky['dhi'])
        source_irradiance = numpy.zeros_like(source_fraction)
        for i, row in c_sky.iterrows():
            rad = sky_radiance_distribution(source_elevation, source_azimuth,
                                            source_fraction,
                                            sky_type='clear_sky',
                                            sun_elevation=row['elevation'],
                                            sun_azimuth=row['azimuth'],
                                            avoid_sun=True)
            source_irradiance += (
            horizontal_irradiance(rad, source_elevation) * row['wsky'])
    else:
        raise ValueError(
            'unknown type: ' + sky_type +
            ' (should be one of uoc, soc, clear_sky')

    source_irradiance /= sum(source_irradiance)
    source_irradiance *= irradiance
    return source_elevation, source_azimuth, source_irradiance


def sun_fraction(sky):
    """Sun fraction of sky irradiance

    Args:
        sky: (pandas DataFrame) sky irradiances as computed by sky_irradiances
        function

    Returns:
        integrated sun fraction
    """
    if sky['dni'].sum() == 0 : return 0
    return (sky['ghi'] - sky['dhi']).sum() / sky['ghi'].sum()


def sky_blend(sky, f_sun=0.):
    """ Clear-sky / overcast mixing fractions for blended sky irradiance model

    ref :  J. Mardaljevic. Daylight Simulation: Validation, Sky Models and
    Daylight Coefficients. PhD thesis, De Montfort University,
    Leicester, UK, 2000.
    p193,eq. 5-10

    Args:
        sky: (pandas DataFrame): sky irradiances as computed by sky_irradiances
        function
        f_sun: (float) sun mixing fraction for the sun (default 0)
    """
    def _f_clear(clearness_index):
        return min(1, (clearness_index - 1) / (1.41 - 1))

    f_clear = numpy.array(map(_f_clear, sky['clearness']))
    # temporal integration
    fclear = (f_clear * sky['ghi']).sum() / sky['ghi'].sum()
    f_clear_sky = fclear * (1 - f_sun)
    f_soc = (1 - fclear) * (1 - f_sun)

    return f_clear_sky, f_soc


def sun_sky_sources(ghi=None, dhi=None, attenuation=None, model='blended',
                    dates=None, daydate=_daydate, pressure=101325,
                    temp_dew=None, longitude=_longitude, latitude=_latitude,
                    altitude=_altitude, timezone=_timezone, normalisation=None):
    """ Light sources representing the sun and the sky for actual irradiances

    Args:
        ghi: (array_like): global horizontal irradiance (W. m-2). If None(
         default) clear sky irradiances are used
        dhi: (array-like, optional): actual diffuse horizontal irradiance.
        attenuation: (float) attenuation factor for ghi (actual_ghi =
         attenuation * ghi). If None (default), no attenuation is applied.
        model:(str) sky luminance model. One of :
                'sun_soc' sun/soc mix as a function of dni / dhi
                'blended' sun/soc/clear_sky blend after Mardaljevic, 2000
        dates: A pandas datetime index (as generated by pandas.date_range). If
            None, hourly values for daydate are used.
        daydate: (str) yyyy-mm-dd (not used if dates is not None).
        pressure: the site pressure (Pa)
        temp_dew: the dew point temperature
        longitude: (float) in degrees
        latitude: (float) in degrees
        altitude: (float) in meter
        timezone:(str) the time zone (not used if dates are already localised)
        normalisation: (float) If not None, sun and sky sources are normalised
         so that sum of sun + sky irradiance equals this value.

    Returns:
        elevation (degrees), azimuth (degrees, from North positive clockwise),
        and horizontal irradiance of sources representing the sun and same
        quantities for sources representing the sky

    Details:
        J. Mardaljevic. Daylight Simulation: Validation, Sky Models and
        Daylight Coefficients. PhD thesis, De Montfort University,
        Leicester, UK, 2000.
    """

    sky_irr = sky_irradiances(dates=dates, daydate=daydate, ghi=ghi, dhi=dhi,
                              attenuation=attenuation, pressure=pressure,
                              temp_dew=temp_dew, longitude=longitude,
                              latitude=latitude, altitude=altitude,
                              timezone=timezone)
    if normalisation is None:
        normalisation = sky_irr['ghi'].sum()

    f_sun = sun_fraction(sky_irr)
    irradiance = f_sun * normalisation
    sun = sun_sources(irradiance=irradiance, dates=dates,
                      daydate=daydate, latitude=latitude, longitude=longitude,
                      altitude=altitude, timezone=timezone)

    if model == 'blended' and f_sun > 0:
        f_clear_sky, f_soc = sky_blend(sky_irr, f_sun)
        irradiance = f_soc * normalisation
        sky_el, sky_az, soc = sky_sources(sky_type='soc', irradiance=irradiance)
        irradiance = f_clear_sky * normalisation
        _, _, csky = sky_sources(sky_type='clear_sky',
                                 irradiance=irradiance, dates=dates,
                                 daydate=daydate, latitude=latitude,
                                 longitude=longitude, altitude=altitude,
                                 timezone=timezone)
        sky = sky_el, sky_az, soc + csky
    elif model == 'sun_soc' or f_sun == 0:
        irradiance = (1 - f_sun) * normalisation
        sky = sky_sources(sky_type='soc', irradiance=irradiance)
    elif f_sun == 0:
        irradiance = (1 - f_sun) * ghi
        sky = sky_sources(sky_type='soc', irradiance=irradiance)
    else:
        raise ValueError(
            'unknown model: ' + model +
            ' (should be one of: soc_sun, blended)')
    return sun, sky




