""" Sun position using ephem lib
"""

from __future__ import division
import pandas
import numpy
import datetime
try:
    import ephem
except ImportError:
    print('ephem not found on your system, you may use sun_position_astk'
          'instead OR install pvlib and use sun_position OR install ephem')


# default location and dates
_day = '2000-06-21'
_timezone = 'Europe/Paris'
_longitude = 3.52
_latitude = 43.36
_altitude = 56


def ephem_sun_position(hUTC, dayofyear, year, latitude, longitude):
    observer = ephem.Observer()
    observer.date = datetime.datetime.strptime(
        '%d %d %d' % (year, dayofyear, hUTC), '%Y %j %H')
    observer.lat = numpy.radians(latitude)
    observer.lon = numpy.radians(longitude)
    sun = ephem.Sun(observer)
    sun.compute(observer)
    return numpy.degrees(sun.alt), numpy.degrees(sun.az)


def sun_position(dates=None, daydate=_day, latitude=_latitude, longitude=_longitude,
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
    fun = numpy.frompyfunc(ephem_sun_position, 5, 2)
    alt, az = fun(hUTC, dayofyear, year, latitude, longitude)
    sunpos = pandas.DataFrame(
        {'elevation': alt.astype(float), 'azimuth': az.astype(float)},
        index=times)
    sunpos['zenith'] = 90 - sunpos['elevation']

    if filter_night and sunpos is not None:
        sunpos = sunpos.loc[sunpos['elevation'] > 0, :]

    return sunpos
