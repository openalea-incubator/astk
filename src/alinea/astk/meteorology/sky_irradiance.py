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

""" Equation for determining global horizontal irradiance (GHI),
direct normal irradiance (DNI) and diffuse horizontal irradiance under clearsky
condition or estimate them from meteorological data

This module is mainly a collection of syntactic sugar to pvlib clearsky and
irradiances packages, together with other model found in the litterature.
"""
import numpy
import pandas
from alinea.astk.meteorology.sun_position import sun_position, sinel_integral
pvlib_installed = True
try:
    import pvlib
except ImportError:
    pvlib_installed = False

# default location and dates
_day = '2000-06-21'
_dates = pandas.date_range(_day, periods=24, freq='H')
_timezone = 'Europe/Paris'
_longitude = 3.52
_latitude = 43.36
_altitude = 56


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


def sun_extraradiation(dates=_dates, solar_constant=1366.1, method='spencer', timezone=_timezone,no_pvlib =False):
    """ Extraterrestrial radiation (W.m2) at the top of the earth atmosphere

        Args:
            dates: a Pandas dateTime index
            If pvlib is installed all valid inputs of pvlib extraradiation
            solar_constant (floa)
            method : one methode prvided by pvlib or 'spencer' or 'asce' if not installed
    """
    if dates.tz is None:
        times = dates.tz_localize(timezone)
    else:
        times = dates

    if pvlib_installed and not no_pvlib:
        return pvlib.irradiance.extraradiation(times, solar_constant=solar_constant, method=method)
    else:
        Io = None
        dayofyear = times.tz_convert('UTC').dayofyear
        B = 2 * numpy.pi * (dayofyear - 1) / 365.
        if method == 'asce':
            # R. G. Allen, Environmental, and E. Water Resources institute .
            # Task Committee on Standardization of Reference,
            # The ASCE standardized reference evapotranspiration equation.
            # Reston, Va.: American Society of Civil Engineers, 2005.
            Io = solar_constant * (1 + 0.033 * numpy.cos(B))
        elif method == 'spencer':
            # Approx Spencer 1971
            # J. W. Spencer, Fourier series representation of the sun,
            # Search, vol. 2, p. 172, 1971
            Io = solar_constant * (1.00011 + 0.034221 * numpy.cos(B) + 0.00128 * numpy.sin(
                B) - 0.000719 * numpy.cos(2 * B) + 0.000077 * numpy.sin(2 * B))
        else:
            raise ValueError('unrecognised method: ' + method)
        return Io


def air_mass(zenith, altitude=0):
    """Estimate the pressure-corrected air mass
    (optical path length relative to zenital path at a location)

    Args:
        zenith : an array-like object of zenital directions (degrees)
        altitude : (float)
    """
    if pvlib_installed:
        airmass = pvlib.atmosphere.relativeairmass(zenith)
        pressure = pvlib.atmosphere.alt2pres(altitude)
        am = pvlib.atmosphere.absoluteairmass(airmass, pressure)
    else:
        am = 1.0 / numpy.cos(numpy.radians(zenith))
    return am


def clearness(dni, dhi, sun_zenith):
    """Perez formula for clearness index

    Args:
        dni:
        dhi:
        sun_zenith:

    Returns:

    """
    z = numpy.radians(sun_zenith)
    return ((dhi + dni) / dhi + 1.041 * z**3) / (1 + 1.041 * z**3)


def brightness(air_mass, dhi, dni_extra):
    """perez formula for brightness index

    Args:
        air_mass:
        dhi:
        dni_extra:

    Returns:

    """
    return air_mass * dhi / dni_extra


def f_clear(clearness_index):
    """The clear-sky / overcast sky mixing ratio proposed by Mardaljevic, p193,
    eq. 5-10

    ref :  J. Mardaljevic. Daylight Simulation: Validation, Sky Models and
    Daylight Coefficients. PhD thesis, De Montfort University,
    Leicester, UK, 2000.
    """
    return min(1, (clearness_index - 1) / (1.41 - 1))



def clear_sky_irradiances(dates=_dates, longitude=_longitude, latitude=_latitude, altitude=_altitude, timezone=_timezone, method = 'ineichen'):
    """ Estimate components of  sky irradiance for clear sy conditions at a given location

    Args:
        dates:
        longitude:
        latitude:
        altitude:
        timezone:

    Returns:
        a pandas dataframe with DNI, GHI and DHI.
    Details:
        the Perez / Ineichen model (2002) is used, except if pvlib is not available.
        In the later case, GHI is computed after Haurwitz (1945) and DNI after Meinel (1976)

        P. Ineichen and R. Perez, "A New airmass independent formulation for
        the Linke turbidity coefficient", Solar Energy, vol 73, pp. 151-157, 2002
        B. Haurwitz, "Insolation in Relation to Cloudiness and Cloud
     Density," Journal of Meteorology, vol. 2, pp. 154-166, 1945.
        A. B. Meinel and M. P. Meinel, Applied solar energy.
        Reading, MA: Addison-Wesley Publishing Co., 1976
    """
    df = sun_position(dates=dates, latitude=latitude, longitude=longitude, altitude=altitude, timezone=timezone)
    df['am'] = air_mass(df['zenith'], altitude)
    df['dni_extra'] = sun_extraradiation(df.index)
    if method == 'ineichen' and pvlib_installed:
        tl = pvlib.clearsky.lookup_linke_turbidity(df.index, latitude, longitude)
        clearsky = pvlib.clearsky.ineichen(df['zenith'], df['am'], tl, dni_extra = df['dni_extra'], altitude = altitude)
        clearsky = pandas.concat([df, clearsky], axis=1)
    else:
        clearsky = df
        z = numpy.radians(df['zenith'])
        clearsky['ghi'] = 1098 * numpy.cos(z) * numpy.exp(-0.057 / numpy.cos(z))
        clearsky['dni'] = df['dni_extra'] * numpy.power(0.7, numpy.power(df['am'], 0.678))
        clearsky['dhi'] = clearsky['ghi'] - horizontal_irradiance(clearsky['dni'], df['elevation'])

    clearsky['brightness'] = brightness(clearsky['am'], clearsky['dhi'], clearsky['dni_extra'])
    clearsky['clearness'] = clearness(clearsky['dni'], clearsky['dhi'], clearsky['zenith'])

    return clearsky.loc[:,['azimuth', 'zenith', 'elevation', 'am', 'dni_extra', 'clearness', 'brightness', 'ghi', 'dni', 'dhi' ]]


def diffuse_horizontal_irradiance(ghi, sun_elevation, times, pressure=101325, temp_dew=None, method='dirint'):
    """ Estimate the diffuse horizontal irradiance from measured global
    horizontal irradiance and sun_elevation

    Args:
        ghi: (arry_like) : global horizontal irradiance (W. m-2)
        sun_elevation: the elevation angle of the sun (degrees)
        times: a localised pandas DateTime index
        pressure: the site pressure (Pa) (for dirint model)
        t_dew: the dew point temperature (dirint model)
        method: a string indicating the method (either 'dirint' or 'spitters'

    Returns:
        the diffuse horizontal irradiance (W. m-2)

    Details:
        spitters refers to the hourly estimate of dhi used in Spitters (1986)
        dirint refers to pvlib dirint method, refering Perez model (1992)

        Perez, R., P. Ineichen, E. Maxwell, R. Seals and A. Zelenka, (1992).
        Dynamic Global-to-Direct Irradiance Conversion Models.
        ASHRAE Transactions-Research Series, pp. 354-369
        Spitters CJT, Toussaint HAJM, Goudriaan J (1986) Separating the diffuse
        and direct component of global radiation and its implications for
        modeling canopy photosynthesis.Part I.
        Components of incoming radiation.
        Agricultural and Forest Meteorology 38: 217-229.

    """

    if method == 'dirint' and pvlib_installed:
        dni = pvlib.irradiance.dirint(ghi, 90 - sun_elevation, times,
                                pressure=pressure, temp_dew=temp_dew)
        return ghi - horizontal_irradiance(dni, sun_elevation)
    else:
        Io = sun_extraradiation(times)
        costheta = numpy.sin(sun_elevation)
        So = Io * costheta
        RsRso = ghi / So
        R = 0.847 - 1.61 * costheta + 1.04 * costheta * costheta
        K = (1.47 - R) / 1.66
        RdRs = numpy.where(RsRso <= 0.22, 1, numpy.where(RsRso <= 0.35,
                                                         1 - 6.4 * (
                                                         RsRso - 0.22) ** 2,
                                                         numpy.where(RsRso <= K,
                                                                     1.47 - 1.66 * RsRso,
                                                                     R)))
        return ghi * RdRs



def daily_diffuse_fraction(ghi, times, latitude):
    """ estimate the diffuse fraction using daily averages of global horizontal irradiance"""

    Io = sun_extraradiation(times)
    dayofyear = times.tz_convert('UTC').dayofyear
    year = times.tz_convert('UTC').year
    So = Io * sinel_integral(dayofyear, year, latitude)
    RsRso = ghi / So

    return numpy.where(RsRso <= 0.07, 1,
                   numpy.where(RsRso <= 0.35, 1 - 2.3 * (RsRso - 0.07) ** 2,
                               numpy.where(RsRso <= 0.75, 1.33 - 1.46 * RsRso,
                                           0.23)))


def actual_sky_irradiances(dates, ghi, dhi=None, Tdew=None, longitude=_longitude, latitude=_latitude, altitude=_altitude, method='dirint'):
    """ derive a sky irradiance dataframe from actual weather data"""

    df = sun_position(dates=dates, latitude=latitude, longitude=longitude, altitude=altitude, filter_night=False)
    df['am'] = air_mass(df['zenith'], altitude)
    df['dni_extra'] = sun_extraradiation(df.index)
    if dhi is None:
        pressure = pvlib.atmosphere.alt2pres(altitude)
        dhi = diffuse_horizontal_irradiance(ghi, df['elevation'], dates, pressure=pressure, temp_dew=Tdew, method=method)
    df['ghi'] = ghi
    df['dhi'] = dhi
    el = numpy.radians(df['elevation'])
    df['dni'] = (df['ghi'] - df['dhi']) / numpy.sin(el)

    df['brightness'] = brightness(df['am'], df['dhi'], df['dni_extra'])
    df['clearness'] = clearness(df['dni'], df['dhi'], df['zenith'])

    return df.loc[(df['elevation'] > 0) & (df['ghi'] > 0) , ['azimuth', 'zenith', 'elevation', 'am', 'dni_extra', 'clearness', 'brightness', 'ghi', 'dni', 'dhi' ]]



