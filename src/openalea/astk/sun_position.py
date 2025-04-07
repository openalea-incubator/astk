# -*- python -*-
#
#       Copyright 2016-2025 Inria - CIRAD - INRAe
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       WebSite : https://github.com/openalea-incubator/astk/meteorology
#
#       File author(s): Christian Fournier <Christian.Fournier@supagro.inra.fr>
#
# ==============================================================================


""" Sun position using pvlib lib
"""
import pandas

try:
    from pvlib.solarposition import get_solarposition
    try:
        from pvlib.irradiance import get_extra_radiation
    except ImportError:
        from pvlib.irradiance import extraradiation as get_extra_radiation
except ImportError as e:
    raise ImportError(
        '{0}\npvlib not found on your system, you may use sun_position_astk '
        'instead OR install ephem and use sun_position_ephem OR install pvlib '
        '(recommended)'.format(e))


# default location and dates
_day = '2000-06-21'
_timezone = 'Europe/Paris'
_longitude = 3.52
_latitude = 43.36
_altitude = 56


def sun_position(dates=None, daydate=_day, latitude=_latitude,
                 longitude=_longitude, altitude=_altitude, timezone=_timezone,
                 filter_night=True):
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
        localised dates. Sun azimuth is given from North, positive clockwise.
    """

    if dates is None:
        dates = pandas.date_range(daydate, periods=24, freq='h')

    if dates.tz is None:
        times = dates.tz_localize(timezone)
    else:
        times = dates

    df = get_solarposition(times, latitude, longitude, altitude)
    sunpos = pandas.DataFrame(
        {'elevation': df['apparent_elevation'], 'azimuth': df['azimuth'],
         'zenith': df['apparent_zenith']}, index=df.index)

    if filter_night and sunpos is not None:
        sunpos = sunpos.loc[sunpos['elevation'] > 0, :]

    return sunpos


def sun_extraradiation(dates=None, daydate=_day, solar_constant=1366.1,
                       method='spencer', timezone=_timezone):
    """ Extraterrestrial radiation (W.m2) at the top of the earth atmosphere

        Args:
            dates: a pandas.DatetimeIndex specifying the dates at which output
            is required.If None, daydate is used and one position per hour is generated
            daydate: (str) yyyy-mm-dd (not used if dates is not None).
            solar_constant: (float)
            method: one method provided by pvlib
            timezone: a string identifying the timezone to be associated to dates if
             dates is not already localised.
    """
    if dates is None:
        dates = pandas.date_range(daydate, periods=24, freq='h')

    if dates.tz is None:
        times = dates.tz_localize(timezone)
    else:
        times = dates

    return get_extra_radiation(times, solar_constant=solar_constant, method=method)
