""" A collection of equation for modelling sun position, sun irradiance and sky irradiance

C. Fournier, 2015
"""

import numpy
import datetime
import pandas
from alinea.astk.meteorology.sky_irradiance import clear_sky_irradiances, \
    horizontal_irradiance

# Sun models and equations


def sun_extraterrestrial_radiation(dayofyear, method='Spencer'):
    """ Extraterrestrial radiation (W.m2) at the top of the earth atmosphere
    """

    if method == 'asce':
        # R. G. Allen, Environmental, and E. Water Resources institute .
        # Task Committee on Standardization of Reference,
        # The ASCE standardized reference evapotranspiration equation.
        # Reston, Va.: American Society of Civil Engineers, 2005.
        Io = 1367.7 * (1 + 0.033 * numpy.cos(2 * numpy.pi * dayofyear / 365.))
    else:
        # Approx Spencer 1971
        # J. W. Spencer, Fourier series representation of the sun,
        # Search, vol. 2, p. 172, 1971
        x = 2 * numpy.pi * (dayofyear - 1) / 365.
        Io = 1366.1 * (1.00011 + 0.034221 * numpy.cos(x) + 0.00128 * numpy.sin(
            x) - 0.000719 * numpy.cos(2 * x) + 0.000077 * numpy.sin(2 * x))
    return Io


def diffuse_fraction(Ghi, dayofyear, elevation,
                     model='Spitters'):
    """ Estimate the diffuse fraction of the global horizontal irradiance (GHI)
        measured at ground level

        Estimated after Spitters (1986)
    """
    Io = sun_extraterrestrial_radiation(dayofyear)
    costheta = numpy.sin(elevation)
    So = Io * costheta
    RsRso = Ghi / So
    R = 0.847 - 1.61 * costheta + 1.04 * costheta * costheta
    K = (1.47 - R) / 1.66
    RdRs = numpy.where(RsRso <= 0.22, 1,
                       numpy.where(RsRso <= 0.35, 1 - 6.4 * (RsRso - 0.22) ** 2,
                                   numpy.where(RsRso <= K, 1.47 - 1.66 * RsRso,
                                               R)))
    return RdRs


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
        raise ValueError, 'Clear sky requires sun position'

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
        raise ValueError, 'Unknown sky type'


def sky_discretisation(type='turtle46', nb_az=None, nb_el=None):
    elevations46 = [9.23] * 10 + [10.81] * 5 + [26.57] * 5 + [31.08] * 10 + [
                    47.41] * 5 + [52.62] * 5 + [69.16] * 5 + [90]
    azimuths46 = [12.23, 59.77, 84.23, 131.77, 156.23, 203.77, 228.23, 275.77,
                  300.23, 347.77, 36, 108, 180, 252, 324, 0, 72, 144, 216, 288,
                  23.27, 48.73, 95.27, 120.73, 167.27, 192.73, 239.27, 264.73,
                  311.27, 336.73, 0, 72, 144, 216, 288, 36, 108, 180, 252, 324,
                  0, 72, 144, 216, 288, 180]
    steradians46 = [0.1355] * 10 + [0.1476] * 5 + [0.1207] * 5 + [
                   0.1375] * 10 + [0.1364] * 5 + [0.1442] * 5 + [0.1378] * 5 + [
                       0.1196]
    sky_fraction = numpy.array(steradians46) / sum(steradians46)

    return elevations46, azimuths46, sky_fraction


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


def _dates(dayofyear, year, hUTC=range(24)):
    d = map(
        lambda x: datetime.datetime.strptime('%d %d %d' % (x[0], x[1], x[2]),
                                             '%Y %j %H'),
        zip([year] * 24, [dayofyear] * 24, hUTC))
    return pandas.to_datetime(d, utc=True)


def sky_sources(sky_elevation=None, sky_azimuth=None, sky_fraction=None,
                type='soc', irradiance=1, dates=None, daydate='2000-06-21',
                timezone='Europe/Paris', latitude=43.61, longitude=3.87,
                altitude=56):
    """ Light sources representing the sky in 46 directions

    Args:
        type:(str) one of  'soc' (standard overcast sky),
                           'uoc' (uniform)
                           'clear_sky' (standard clear sky)
        irradiance: (float) total horizontal irradiance of sources for the period.
            Using irradiance=1 (default) yields relative contribution of sources.
            If None, clear sky diffuse horizontal irradiance predicted by
            Perez/Ineichen model is used for clear_sky type, and 20% of clear
            sky global horizontal irradiance is used for soc and uoc types
        dates: A pandas datetime index (as generated by pandas.date_range). If
            None, daydate is used.
        daydate: (str) yyyy-mm-dd (not used if dates is not None).
        timezone: (str) the time zone (not used if dates are already localised)
        latitude: (float)
        longitude: (float)
        altitude: (float) in meter

    Returns:
        elevation (degrees), azimuth (degrees, from North positive clockwise),
        and horizontal irradiance of sources
    """

    if dates is None:
        dates = pandas.date_range(daydate, periods=24, freq='H')
    if dates.tz is None:
        dates = dates.tz_localize(timezone)

    if sky_elevation is None:
        sky_elevation, sky_azimuth, sky_fraction = sky_discretisation()
    if sky_fraction is None:
        sky_fraction = [1./len(sky_elevation)] * len(sky_elevation)

    if type == 'soc' or type == 'uoc':
        radiance = sky_radiance_distribution(sky_elevation, sky_azimuth,
                                                   sky_fraction,
                                                   sky_type=type)
        sky_irradiance = horizontal_irradiance(radiance, sky_elevation)
        if irradiance is None:
            c_sky = clear_sky_irradiances(dates, longitude=longitude,
                                          latitude=latitude, altitude=altitude)
            irradiance = sum(c_sky['ghi']) * 0.2

    elif type == 'clear_sky':
        c_sky = clear_sky_irradiances(dates, longitude=longitude,
                                      latitude=latitude, altitude=altitude)
        if irradiance is None:
            irradiance = sum(c_sky['dhi'])

        # temporal weigths : use dhi (diffuse horizontal irradiance)
        c_sky['wsky'] = c_sky['dhi'] / sum(c_sky['dhi'])
        sky_irradiance = numpy.zeros_like(sky_fraction)
        for i, row in c_sky.iterrows():
            rad = sky_radiance_distribution(sky_elevation, sky_azimuth,
                                            sky_fraction,
                                            sky_type='clear_sky',
                                            sun_elevation=row['elevation'],
                                            sun_azimuth=row['azimuth'],
                                            avoid_sun=True)
            sky_irradiance += (
            horizontal_irradiance(rad, sky_elevation) * row['wsky'])
    else:
        raise ValueError(
            'unknown type: ' + type + ' (should be one of uoc, soc, clear_sky')

    sky_irradiance /= sum(sky_irradiance)
    sky_irradiance *= irradiance
    return sky_elevation, sky_azimuth, sky_irradiance


def sun_sources(irradiance=1, dates=None, daydate='2000-06-21',
                timezone='Europe/Paris', latitude=43.61, longitude=3.87,
                altitude=56):
    """ Light sources representing the sun under clear sky conditions

    Args:
        irradiance: (float) total horizontal irradiance of sources for the period.
            Using irradiance=1 (default) yields relative contribution of sources.
            If None, clear sky sun horizontal irradiance predicted by
            Perez/Ineichen model is used.
        dates: A pandas datetime index (as generated by pandas.date_range)
            specifying times at which a source is needed.
            If None, daydate is used and one source per hour is generated.
        daydate: (str) yyyy-mm-dd (not used if dates is not None).
        timezone: (str) the time zone (not used if dates are already localised)
        latitude: (float)
        longitude: (float)
        altitude: (float) in meter

    Returns:
        elevation (degrees), azimuth (degrees, from North positive clockwise)
        and horizontal irradiance of sources
    """

    if dates is None:
        dates = pandas.date_range(daydate, periods=24, freq='H')
    if dates.tz is None:
        dates = dates.tz_localize(timezone)

    c_sky = clear_sky_irradiances(dates, longitude=longitude,
                          latitude=latitude, altitude=altitude)

    sun_irradiance = c_sky['ghi'] - c_sky['dhi']

    if irradiance is not None:
        sun_irradiance /= sum(sun_irradiance)
        sun_irradiance *= irradiance

    # Sr = (1 -cos(cone half angle)) * 2 * pi, frac = Sr / 2 / pi
    # fsun = 1 - numpy.cos(numpy.radians(.53 / 2))
    return c_sky['elevation'].values, c_sky[
        'azimuth'].values, sun_irradiance.values


# def RgH (Rg,hTU,DOY,latitude) :
# """ compute hourly value of Rg at hour hTU for a given day at a given latitude
# Rg is in J.m-2.day-1
# latidude in degrees
# output is J.m-2.h-1
# """

# dec = DecliSun(DOY)
# lat = radians(latitude)
# pi = 3.14116
# a = sin(lat) * sin(dec)
# b = cos(lat) * cos(dec)
# Psi = numpy.pi * Rg / 86400 / (a * acos(-a / b) + b * sqrt(1 - (a / b)^2))
# A = -b * Psi
# B = a * Psi
# RgH = A * cos (2 * pi * hTU / 24) + B
# Note that this formula works for h beteween hsunset eand hsunrise
# hsunrise = 12 - 12/pi * acos(-a / b)
# hsunset = 12 + 12/pi * acos (-a / b)
# return RgH
