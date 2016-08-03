""" A collection of equation for modelling sun position, sun irradiance and sky irradiance

C. Fournier, 2015
"""

import numpy
import datetime
import pandas


# Sun models and equations

def ecliptic_longitude(dayofyear):
    """ Approximate the ecliptic longitude using formula of Grebet 1993
      (Crop structure and light microclimate, INRA editions)

    Args:
        dayofyear: (int) the day of year

    Returns:
        (float) the ecliptic longitude (radians) of the day
    """
    """
    """
    omega = 0.017202 * (dayofyear - 3.244)
    return omega + 0.03344 * numpy.sin(omega) * (
        1 + 0.021 * numpy.cos(omega)) - 1.3526


def declination(dayofyear, method="default"):
    """ sun declination angle

    Args:
        dayofyear: (int) the day of year
        method: (str) the method to be used (either 'spencer' or 'default')

    Returns:
        (float) sun declination (radians)

    Details:
        - 'spencer' method is taken from J. W. Spencer, Fourier series
            representation of the sun, Search, vol. 2, p. 172, 1971
        - 'default' method is for 'true' declination (provided that the
        obliquity of the ecliptic and the ecliptic longitude are exact)
         Michalsky, J. J. "The Astronomical Almanac's Algorithm for Approximate
         Solar Position (1950-2050)". Solar Energy. Vol. 40, No. 3, 1988;
         pp. 227-235, USA

    """

    if method == "spencer":  # usefull for checking time equation
        x = 2 * numpy.pi * (dayofyear - 1) / 365.
        dec = 0.006918 \
              - 0.399912 * numpy.cos(x) + 0.070257 * numpy.sin(x) \
              - 0.006758 * numpy.cos(2 * x) + 0.000907 * numpy.sin(2 * x) \
              - 0.002697 * numpy.cos(3 * x) + 0.001480 * numpy.sin(3 * x)
    elif method == 'SunAlign':
        obliquity = -23.44 # constant approximation
        cst = 360 / 365.24
        sidec = numpy.sin(numpy.radians(obliquity)) * numpy.cos(numpy.radians( cst*(dayofyear+10)) + 2*0.0167*numpy.sin(cst*(dayofyear-2))  )
        dec = numpy.arcsin(sidec)
    else:
        obliquity = 23.44  # constant approximation
        sidec = numpy.sin(numpy.radians(obliquity)) * numpy.sin(
            ecliptic_longitude(dayofyear))
        dec = numpy.arcsin(sidec)
    return dec


def eot(dayofyear):
    """equation of time, ie the discrepancy between true solar time and
    local solar time
    Approximation formula by Grebet (1993),
    in Crop structure and light microclimate
    
    Seems buggy at least for south hemisphere

    Args:
        dayofyear: (int) the day of year

    Returns:
        (float) the eot value
    """
    """
    """
    omega = 0.017202 * (dayofyear - 3.244)
    eclong = ecliptic_longitude(dayofyear)
    tanphi = 0.91747 * numpy.sin(eclong) / numpy.cos(eclong)
    phi = numpy.arctan(tanphi) - omega + 1.3526
    phi = numpy.where((phi + 1) <= 0,
                      numpy.mod(phi + 1 + 1000 * numpy.pi, numpy.pi) - 1, phi)
    return phi * 229.2 / 60


def solar_time(hUTC, dayofyear, longitude):
    """ Local solar time(hour)

    Args:
        hUTC: (float) universal time (hour)
        dayofyear: (int) the day of year
        longitude: (float) a terrestrial longitude (degrees)

    Returns:
        (float) the solar time
    """

    return numpy.mod(hUTC + longitude / 15. - eot(dayofyear), 24)


def hour_angle(hUTC, dayofyear, longitude):
    """ Local solar hour angle (radians)   
    """
    return 2 * numpy.pi / 24. * (solar_time(hUTC, dayofyear, longitude) - 12)


def day_length(latitude, dayofyear):
    """ daylength (hours)"""
    lat = numpy.radians(latitude)
    decli = declination(dayofyear)
    d = numpy.arccos(-numpy.tan(decli) * numpy.tan(lat))
    d = numpy.where(d < 0, d + numpy.pi, d)
    return 2 * d / numpy.pi * 12


def sinh(hUTC, dayofyear, longitude, latitude):
    """ Sine of sun elevation angle (= cosine of the zenith angle)
    """
    lat = numpy.radians(latitude)
    decli = declination(dayofyear)
    omega = hour_angle(hUTC, dayofyear, longitude)

    return numpy.sin(latitude) * numpy.sin(decli) + numpy.cos(
        latitude) * numpy.cos(decli) * numpy.cos(omega)


def sun_elevation(hUTC, dayofyear, longitude, latitude):
    """ sun elevation angle (degrees)
    """
    sinel = sinh(hUTC, dayofyear, longitude, latitude)
    return numpy.degrees(numpy.arcsin(sinel))
        
        



def sun_azimuth(hUTC, dayofyear, longitude, latitude, origin='North'):
    """ sun azimuth angle (degrees)
    
        sun azimuth is positive clockwise, starting at origin (North or South)
    """
    lat = numpy.radians(latitude)
    decli = declination(dayofyear)
    omega = hour_angle(hUTC, dayofyear, longitude)

    D = numpy.sin(lat) * numpy.cos(omega) - numpy.cos(lat) * numpy.sin(
        decli) / numpy.cos(decli)
    # azimuth counted from south, same sign as hour angle
    az = numpy.where(omega < 0, -1, 1) * numpy.where(D == 0, numpy.pi / 2,
                                                     numpy.abs(numpy.arctan(
                                                         numpy.sin(omega) / D)))

    if origin == 'North':
        az = az + numpy.pi

    return numpy.degrees(az)

def ephem_sun_position(hUTC, dayofyear, year, longitude, latitude):
    import ephem
    observer = ephem.Observer()
    observer.date = datetime.datetime.strptime('%d %d %d' % (year, dayofyear, hUTC), '%Y %j %H')
    observer.lat = numpy.radians(latitude)
    observer.lon = numpy.radians(longitude)
    sun = ephem.Sun(observer)
    sun.compute(observer)
    return numpy.degrees(sun.alt), numpy.degrees(sun.az) 
    
def sun_position(hUTC, dayofyear, year, longitude, latitude):
    """ compute sun position (sun elevation(degree) and sun azimuth( degree, Noth clockwise convention using ephem
    """
    try:
        import ephem
    except ImportError:
        return(sun_elevation(hUTC, dayofyear, longitude, latitude), sun_azimuth(hUTC, dayofyear, longitude, latitude, origin='North'))
    fun = numpy.frompyfunc(ephem_sun_position, 5, 2)
    alt, az = fun(hUTC, dayofyear, year, longitude, latitude)
    return alt.astype(float), az.astype(float)
    
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


def sun_irradiance(dayofyear, sun_elevation):
    """ sun irradiance (W.m2) at the top of the atmosphere through a plane perpendicular
    
        to sun direction at a given time and location
    """
    Io = sun_extraterrestrial_radiation(dayofyear)
    return Io * numpy.sin(numpy.radians(sun_elevation))


def sun_clear_sky_direct_normal_irradiance(sun_elevation, dayofyear,
                                           irradiance='horizontal'):
    """ Direct normal irradiance (W.m2) of the sun
        reaching the soil on a clear day
        
        Direct normal irradiance means through a plane
        perpendicular to sun direction
        Atmospheric attenuation is computed using the simple
        geometric approximation of Meinel (1976)
        
        A. B. Meinel and M. P. Meinel, Applied solar energy.
        Reading, MA: Addison-Wesley Publishing Co., 1976
    """
    Io = sun_extraterrestrial_radiation(dayofyear)
    sinel = numpy.sin(sun_elevation)
    AM = numpy.where(sinel == 0, 1. / numpy.sin(0.01), 1. / sinel)
    if irradiance == 'normal':
        return Io * sinel * numpy.power(0.7, numpy.power(AM, 0.678))
    else:
        return Io * numpy.power(0.7, numpy.power(AM, 0.678))


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


def diffuse_light_irradiance(sky_elevation, sky_azimuth, sky_fraction,
                             sky_type='soc', irradiance='horizontal',
                             sun_elevation=None, sun_azimuth=None):
    """Normalised diffuse light irradiances coming from a discretised sky

    Normalisation is for the sum of irradiance received on an horizontal surface.
    if irradiance == 'normal', the sum of irradiance will be greater than 1

    Args:
        sky_elevation: (float or list of float) elevation angle (degrees)
        of directions sampling the sky hemisphere
        sky_azimuth: (float or list of float) azimuth angle (degrees)
        of directions sampling the sky hemisphere
        sky_fraction: (float or list of float) fraction of sky represented by
        the directions sampling the sky hemisphere
        sky_type: (str) one of  'soc' (standard overcast sky),
                                'uoc' (uniform luminance)
                                'clear_sky' (standard clear sky low turbidity)
        irradiance: (str) convention for irradiance.
            'normal' returns irradiance normal to the direction of incidence,
            'horizontal' (default) return the irradiance measured
            on an horizontal surface
        sun_elevation: sun elevation (degrees). Only needed for clear_sky
        sun_azimuth: sun azimuth (degrees). Only needed for clear_sky

    Returns:
        the relative iradiance(s) associated to the sky directions
    """

    el = numpy.radians(sky_elevation)
    az = numpy.radians(sky_azimuth)
    sky_fraction = numpy.array(sky_fraction) / numpy.sum(sky_fraction)

    if sun_elevation is not None:
        sun_elevation = numpy.radians(sun_elevation)
    if sun_azimuth is not None:
        sun_azimuth = numpy.radians(sun_azimuth)

    lum = cie_relative_luminance(el, az, sun_elevation, sun_azimuth,
                                 type=sky_type)
    # use horizontal convention for normalisation
    lum = lum * numpy.sin(el) * sky_fraction
    lum /= sum(lum)

    if irradiance == 'normal':
        lum /= numpy.sin(el)

    return lum


def sun_path(dayofyear=1, year=2000, latitude=43.61, longitude=3.87,
             azimuth_origin='North', day_only=True):
    """ Return position of the sun corresponding to a sequence of date
    """
    hUTC = range(24)
    elevation, azimuth = sun_position(hUTC, dayofyear, year, longitude,
                                      latitude)

    toa_irradiance = sun_irradiance(dayofyear, elevation)
    # ground_irradiance = sun_clear_sky_direct_normal_irradiance(
    #    elevation, dayofyear, 'horizontal')
    df = pandas.DataFrame(
        {'dayofyear': dayofyear, 'hUTC': hUTC, 'elevation': elevation,
         'azimuth': azimuth, 'DNI': toa_irradiance})
    if day_only:
        return df.loc[df['elevation'] > 0, :]
    else:
        return df


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


def light_sources(dayofyear=1, year=2000, latitude=43.61, longitude=3.87,
             type='soc', dicretisation='turtle_46'):
    """ normalised light sources for one day
    """
    elevation, azimuth, strd = sky_discretisation(type=dicretisation)
    fraction = numpy.array(strd) / sum(strd)

    if type == 'soc' or type == 'uoc':
        irradiance = diffuse_light_irradiance(elevation, azimuth, fraction,
                                              sky_type=type,
                                              irradiance='horizontal')
    elif type == 'clear_sky':
        sun = sun_path(dayofyear, year, latitude, longitude)
        sun['weight'] = sun['DNI'] / sum(sun['DNI'])
        irradiance = numpy.zeros_like(fraction)
        for i, row in sun.iterrows():
            irr = diffuse_light_irradiance(elevation, azimuth, fraction,
                             sky_type='clear_sky', irradiance='horizontal',
                             sun_elevation=row['elevation'], sun_azimuth=row['azimuth'])
            irradiance += (irr * row['weight'])
    else:
        raise ValueError(
            'unknown type: ' + type + ' (should be one of uoc, soc, clear_sky')

    return elevation, azimuth, strd, irradiance

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
