""" Astronomical equation for determining sun position
"""

import pandas
import numpy

# default location and dates
_day = '2000-06-21'
_timezone = 'Europe/Paris'
_longitude = 3.52
_latitude = 43.36
_altitude = 56


def julian_date(hUTC, dayofyear, year):
    """ Julian calendar date

    Args:
        hUTC: fractional hour (UTC time)
        dayofyear (int):
        year (int):

    Returns:
        the julian date

    Details:
        World Meteorological Organization (2006).Guide to meteorological
        instruments and methods of observation. Geneva, Switzerland.
    """
    delta = year - 1949
    leap = numpy.floor(delta / 4.)
    return 2432916.5 + delta * 365 + leap + dayofyear + hUTC / 24.


def ecliptic_longitude(hUTC, dayofyear, year):
    """ Ecliptic longitude

    Args:
        hUTC: fractional hour (UTC time)
        dayofyear (int):
        year (int):

    Returns:
        (float) the ecliptic longitude (degrees)

    Details:
        World Meteorological Organization (2006).Guide to meteorological
        instruments and methods of observation. Geneva, Switzerland.
    """

    jd = julian_date(hUTC, dayofyear, year)
    n = jd - 2451545
    # mean longitude (deg)
    L = numpy.mod(280.46 + 0.9856474 * n, 360)
    # mean anomaly (deg)
    g = numpy.mod(357.528 + 0.9856003 * n, 360)

    return L + 1.915 * numpy.sin(numpy.radians(g)) + 0.02 * numpy.sin(
        numpy.radians(2 * g))


def declination(hUTC, dayofyear, year, method="default"):
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
        dec = 0.006918 - 0.399912 * numpy.cos(x) + 0.070257 * numpy.sin(
            x) - 0.006758 * numpy.cos(2 * x) + 0.000907 * numpy.sin(
            2 * x) - 0.002697 * numpy.cos(3 * x) + 0.001480 * numpy.sin(3 * x)
    else:
        jd = julian_date(hUTC, dayofyear, year)
        n = jd - 2451545
        obliquity = 23.439 - 0.0000004 *   n
        l = ecliptic_longitude(hUTC, dayofyear, year)
        sidec = numpy.sin(numpy.radians(obliquity)) * numpy.sin(numpy.radians(l))
        dec = numpy.arcsin(sidec)

    return dec


def right_ascension(hUTC, dayofyear, year):
    """ Sun right ascension

    Args:
        hUTC: fractional hour (UTC time)
        dayofyear (int):
        year (int):

    Returns:
        (float) the sun right ascencion (degrees)

    Details:
        World Meteorological Organization (2006).Guide to meteorological
        instruments and methods of observation. Geneva, Switzerland.
    """
    jd = julian_date(hUTC, dayofyear, year)
    n = jd - 2451545
    obliquity = numpy.radians(23.439 - 0.0000004 * n)
    l = ecliptic_longitude(hUTC, dayofyear, year)
    cosl = numpy.cos(numpy.radians(l))
    sinl = numpy.sin(numpy.radians(l))
    quadrant = numpy.where(cosl >= 0,
                           numpy.where(sinl >=0, 1, 4),
                           numpy.where(sinl >= 0, 2, 3))
    tanra = numpy.cos(obliquity) * sinl / cosl
    ra = numpy.degrees(numpy.arctan(tanra))
    return ra + numpy.where((quadrant == 1) | (quadrant == 4), 0, 180)


def hour_angle(hUTC, dayofyear, year, longitude):
    """ Sun hour angle

    Args:
        hUTC: fractional hour (UTC time)
        dayofyear (int):
        year (int):
        longitude (float): the location longitude (degrees, east positive)


    Returns:
        (float) the hour angle (hour)

    Details:
        World Meteorological Organization (2006).Guide to meteorological
        instruments and methods of observation. Geneva, Switzerland.
    """
    jd = julian_date(hUTC, dayofyear, year)
    n = jd - 2451545
    gmst = numpy.mod(6.697375 + 0.0657098242 * n + hUTC, 24)
    lmst = numpy.mod(gmst + longitude / 15., 24)
    ra = right_ascension(hUTC, dayofyear, year)
    ha = numpy.mod(lmst - ra / 15. + 12, 24) - 12
    return ha


def sun_elevation(hUTC, dayofyear, year, latitude, longitude):
    """ Sun elevation

    Args:
        hUTC: fractional hour (UTC time)
        dayofyear (int):
        year (int):
        latitude (float): the location latitude (degrees)
        longitude (float): the location longitude (degrees)

    Returns:
        (float) the sun elevation (degrees)

    Details:
        World Meteorological Organization (2006).Guide to meteorological
        instruments and methods of observation. Geneva, Switzerland.
    """
    dec = declination(hUTC, dayofyear, year)
    lat = numpy.radians(latitude)
    ha = numpy.radians(hour_angle(hUTC, dayofyear, year, longitude) * 15)
    sinel = numpy.sin(dec) * numpy.sin(lat) + numpy.cos(dec) * numpy.cos(
        lat) * numpy.cos(ha)

    return numpy.degrees(numpy.arcsin(sinel))


def sun_azimuth(hUTC, dayofyear, year, latitude, longitude):
    """ Sun azimuth (from North, positive clockwise)

    Args:
        hUTC: fractional hour (UTC time)
        dayofyear (int):
        year (int):
        latitude (float): the location latitude (degrees)
        longitude (float): the location longitude (degrees)

    Returns:
        (float) the sun elevation (degrees)

    Details:
         Michalsky, J. J. "The Astronomical Almanac's Algorithm for Approximate
         Solar Position (1950-2050)". Solar Energy. Vol. 40, No. 3, 1988;
         pp. 227-235, USA
    """
    dec = declination(hUTC, dayofyear, year)
    lat = numpy.radians(latitude)
    ha = numpy.radians(hour_angle(hUTC, dayofyear, year, longitude) * 15)
    el = numpy.radians(sun_elevation(hUTC, dayofyear, year, latitude, longitude))
    sinaz = -numpy.cos(dec) * numpy.sin(ha) / numpy.cos(el)
    # use method of Michalsky to get az from sinaz
    elc = numpy.arcsin(numpy.sin(dec) / numpy.sin(lat))
    az = numpy.degrees(numpy.arcsin(sinaz))
    az = numpy.where(el >= elc, 180 - az, numpy.where(ha > 0, 360 + az, az))

    return az


def eot(hUTC, dayofyear, year):
    """equation of time, ie the discrepancy between true solar time and
    local solar time

    Args:
        dayofyear: (int) the day of year

    Returns:
        (float) the eot disccrepancy (in hour)

    Details:
         Michalsky, J. J. "The Astronomical Almanac's Algorithm for Approximate
         Solar Position (1950-2050)". Solar Energy. Vol. 40, No. 3, 1988;
         pp. 227-235, USA

    """
    jd = julian_date(hUTC, dayofyear, year)
    n = jd - 2451545
    # mean longitude (deg)
    L = numpy.mod(280.46 + 0.9856474 * n, 360)
    ra = right_ascension(hUTC, dayofyear, year)

    return (L - ra) / 15.


def daylength(dayofyear, year, latitude):
    """ estimate of daylength"""

    lat = numpy.radians(latitude)
    dec = declination(12, dayofyear, year)
    return 12 + 24 / numpy.pi * numpy.arcsin(numpy.tan(lat) - numpy.tan(dec))


def sinel_integral(dayofyear, year, latitude):
    """ estimate the daily integral of elevation sine"""

    lat = numpy.radians(latitude)
    dec = declination(12, dayofyear, year)
    d = daylength(dayofyear, year, latitude)
    return 3600 * (d * numpy.sin(lat) * numpy.sin(dec) + 24. /
                   numpy.pi * numpy.cos(lat) * numpy.cos(dec) * numpy.sqrt(
                       1 - numpy.tan(lat) ** 2 * numpy.tan(dec) ** 2))


def sun_position(dates=None, daydate=_day, latitude=_latitude,
                 longitude=_longitude,
                 altitude=_altitude, timezone=_timezone, filter_night=True):
    """ Sun position

    Args:
        dates: a pandas.DatetimeIndex specifying the dates at which sun position
        is required.If None, daydate is used and one position per hour is generated
        daydate: (str) yyyy-mm-dd (not used if dates is not None).
        latitude: float
        longitude: float
        altitude: (float) altitude in m
        timezone: a string identifying the timezone to be associated to dates if
        dates is not already localised.
        This args is not used if dates are already localised
        filter_night (bool) : Should positions of sun during night be filtered ?

    Returns:
        a pandas dataframe with sun position at requested dates indexed by
        localised dates. Sun azimtuth is given from North, positive clockwise.
    """

    if dates is None:
        dates = pandas.date_range(daydate, periods=24, freq='H')

    if dates.tz is None:
        times = dates.tz_localize(timezone)
    else:
        times = dates

    d = times.tz_convert('UTC')
    hUTC = d.hour + d.minute / 60.
    dayofyear = d.dayofyear
    year = d.year
    el = sun_elevation(hUTC, dayofyear, year, latitude, longitude)
    az = sun_azimuth(hUTC, dayofyear, year, latitude, longitude)
    sunpos = pandas.DataFrame(
        {'elevation': el, 'zenith': 90 - el, 'azimuth': az}, index=times)

    if filter_night and sunpos is not None:
        sunpos = sunpos.loc[sunpos['elevation'] > 0, :]

    return sunpos