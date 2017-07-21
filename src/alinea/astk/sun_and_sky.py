""" A collection of equation for modelling sun position, sun irradiance and sky irradiance

C. Fournier, 2015
"""

import numpy
import datetime
import pandas
from alinea.astk.meteorology.sun_position import sun_position
from alinea.astk.meteorology.sky_irradiance import clear_sky_irradiances

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


def horizontal_irradiance(normal_irradiance, elevation):
    """ irradiance measured on an horizontal surface from a source
    with known elevation (degrees) and known normal irradiance
    """
    return normal_irradiance * numpy.sin(numpy.radians(elevation))


def normal_irradiance(horizontal_irradiance, elevation):
    """ irradiance measured on an surface perpendicular
    to a source with known elevation (degrees) and horizontal irradiance
    """
    return horizontal_irradiance / numpy.sin(numpy.radians(elevation))


# sky models / equations


def cie_luminance_gradation(sky_elevation, a, b):
    """ function giving the dependance of the luminance of a sky element
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
    """ function giving the dependance of the luminance of a sky element
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
    type is one of 'soc' (standard overcast sky), 'uoc' (uniform luminance)
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

    return elevations46, azimuths46, steradians46


def diffuse_light_irradiance(sky_elevation, sky_azimuth, sky_fraction,
                             sky_orientation=0, sky_type='soc',
                             irradiance='horizontal', sun_elevation=None,
                             sun_azimuth=None):
    """Normalised diffuse light irradiances coming from a discretised sky

    Normalisation is for the sum of irradiance received on an horizontal surface.
    if irradiance == 'normal', the sum of irradiance will be greater than 1

    Args:
        sky_elevation: (float or list of float) elevation angle (degrees)
            of directions sampling the sky hemisphere
        sky_azimuth: (float or list of float) azimuth angle (degrees, from X+,
            positive clockwise) of directions sampling the sky hemisphere
        sky_fraction: (float or list of float) fraction of sky represented by
            the directions sampling the sky hemisphere
        sky_orientation (float): the angle (deg, positive clockwise) from X+ to
         North (default: 0)
        sky_type: (str) one of  'soc' (standard overcast sky),
                                'uoc' (uniform luminance)
                                'clear_sky' (standard clear sky low turbidity)
        irradiance: (str) convention for irradiance.
            'normal' returns irradiance normal to the direction of incidence,
            'horizontal' (default) return the irradiance measured
            on an horizontal surface
        sun_elevation: sun elevation (degrees). Only needed for clear_sky
        sun_azimuth: sun azimuth (degrees, from North, positive clockwise).
            Only needed for clear_sky

    Returns:
        the relative iradiance(s) associated to the sky directions
    """

    el = numpy.radians(sky_elevation)
    az = numpy.radians(sky_azimuth)
    sky_fraction = numpy.array(sky_fraction)
    sky_fraction /= sky_fraction.sum()

    if sun_elevation is not None:
        sun_elevation = numpy.radians(sun_elevation)
    if sun_azimuth is not None:
        sun_azimuth = numpy.radians(sun_azimuth + sky_orientation)

    lum = cie_relative_luminance(el, az, sun_elevation, sun_azimuth,
                                 type=sky_type)
    # use horizontal convention for normalisation
    # use sky fraction to model differences in solid angles integrals between
    # sectors
    lum = lum * numpy.sin(el) * sky_fraction
    lum /= sum(lum)

    if irradiance == 'normal':
        lum /= numpy.sin(el)

    return lum


def _dates(dayofyear, year, hUTC=range(24)):
    d = map(
        lambda x: datetime.datetime.strptime('%d %d %d' % (x[0], x[1], x[2]),
                                             '%Y %j %H'),
        zip([year] * 24, [dayofyear] * 24, hUTC))
    return pandas.to_datetime(d, utc=True)


def sun_path(dayofyear=1, year=2000, latitude=43.61, longitude=3.87,
             day_only=True):
    """ Return position of the sun corresponding to a sequence of date
    """
    hUTC = range(24)
    dates = _dates(dayofyear, year, hUTC)
    sun = sun_position(dates, latitude=latitude, longitude=longitude,
                       filter_night=False)
    elevation, azimuth = sun['elevation'].values, sun['azimuth'].values

    df = pandas.DataFrame(
        {'dayofyear': dayofyear, 'hUTC': hUTC, 'elevation': elevation,
         'azimuth': azimuth})
    if day_only:
        return df.loc[df['elevation'] > 0, :]
    else:
        return df


def light_sources(dayofyear=1, year=2000, latitude=43.61, longitude=3.87,
             type='soc', dicretisation='turtle_46', orientation=0):
    """ normalised light sources representing the sky and the sun for one day

    orientation (float): the angle (deg, positive clockwise) from X+ to
         North (default: 0)
         
    Return elevation (deg), azimuth (deg, positive clockwise from X+) and irradiance of sources
    """
    sky_elevation, sky_azimuth, strd = sky_discretisation(type=dicretisation)
    sky_fraction = numpy.array(strd) / sum(strd)
    sun = None

    if type == 'soc' or type == 'uoc':
        sky_irradiance = diffuse_light_irradiance(sky_elevation, sky_azimuth,
                                                  sky_fraction,
                                                  sky_type=type,
                                                  irradiance='horizontal')
    elif type == 'clear_sky':
        dates = _dates(dayofyear, year)
        c_sky = clear_sky_irradiances(dates, longitude=longitude,
                                      latitude=latitude)
        # temporal weigths : use dhi (diffuse horizontal irradiance) for sky
        # and ghi -dhi for sun
        sun_irradiance = (c_sky['ghi'] - c_sky['dhi']) / sum(
            c_sky['ghi'] - c_sky['dhi'])
        c_sky['wsky'] = c_sky['dhi'] / sum(c_sky['dhi'])

        sun = c_sky['elevation'].values, c_sky['azimuth'].values + orientation, sun_irradiance.values
        sky_irradiance = numpy.zeros_like(sky_fraction)

        for i, row in c_sky.iterrows():
            irr = diffuse_light_irradiance(sky_elevation, sky_azimuth, sky_fraction,
                                           sky_orientation=orientation,
                                           sky_type='clear_sky',
                                           irradiance='horizontal',
                                           sun_elevation=row['elevation'],
                                           sun_azimuth=row['azimuth'])
            sky_irradiance += (irr * row['wsky'])
    else:
        raise ValueError(
            'unknown type: ' + type + ' (should be one of uoc, soc, clear_sky')

    sky = (sky_elevation, sky_azimuth, sky_irradiance)

    return sun, sky

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
