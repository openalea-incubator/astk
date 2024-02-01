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

""" Equation for determining global horizontal irradiance (GHI), PPFD,
direct normal irradiance (DNI) and diffuse horizontal irradiance (DHI) under clearsky
condition or estimate them from meteorological data

This module is mainly a collection of syntactic sugar to pvlib clearsky and
irradiances packages.
"""

from __future__ import division
import numpy
import pandas
import warnings

try:
    import pvlib
except ImportError:
    warnings.warn('pvlib not installed: using pure python, but less accurate, functions')

if pvlib:
    from alinea.astk.meteorology.sun_position import sun_position, \
        sun_extraradiation
    from alinea.astk.meteorology.sun_position_astk import sinel_integral
else:
    from alinea.astk.meteorology.sun_position_astk import sun_position, \
        sun_extraradiation, sinel_integral

# default location and dates
_daydate = '2000-06-21'
_timezone = 'Europe/Paris'
_longitude = 3.52
_latitude = 43.36
_altitude = 56


def horizontal_irradiance(normal_irradiance, elevation):
    """ irradiance measured on a horizontal surface from a source
    with known elevation (degrees) and known normal irradiance
    """
    return normal_irradiance * numpy.sin(numpy.radians(elevation))


def normal_irradiance(horizontal_irradiance, elevation):
    """ irradiance measured on a surface perpendicular
    to a source with known elevation (degrees) and horizontal irradiance
    """
    return horizontal_irradiance / numpy.sin(numpy.radians(elevation))


def air_mass(zenith, altitude=0, with_pvlib=True):
    """Estimate the pressure-corrected air mass
    (optical path length relative to zenital path at a location)

    Args:
        zenith : an array-like object of zenital directions (degrees)
        altitude : (float)
        with_pvlib : Should we use pvlib library to estimate air mass ?
    """
    if pvlib and with_pvlib:
        airmass = pvlib.atmosphere.get_relative_airmass(zenith)
        pressure = pvlib.atmosphere.alt2pres(altitude)
        am = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
    else:
        am = 1.0 / numpy.cos(numpy.radians(zenith))
    return am


def all_weather_sky_clearness(dni, dhi, sun_zenith):
    """Sky clearness as defined in all_weather sky model (Perez et al. 1993)

    Args:
        dni: direct normal irradiance
        dhi:diffuse horizontal irradiance
        sun_zenith: zenith angle of the sun (deg)

    Returns:
        sky clearness
    Details:
        R. Perez, R. Seals, J. Michalsky, "All-weather model for sky luminance distribution—Preliminary configuration and
        validation", Solar Energy, Volume 50, Issue 3, 1993, Pages 235-245,

    """
    z = numpy.radians(sun_zenith)
    return ((dhi + dni) / dhi + 1.041 * z**3) / (1 + 1.041 * z**3)


def all_weather_sky_brightness(dates, dhi, sun_zenith, altitude=0, with_pvlib=True):
    """Sky brightness as defined in all_weather sky model (Perez et al. 1993)

    Args:
        dates: A pandas datetime index (as generated by pandas.date_range)
        dhi: diffuse horizontal irradiance
        sun_zenith: zenith angle of the sun (deg)
        altitude: altitude of the location
        with_pvlib : Should we use pvlib library to estimate air mass ?

    Returns:
        sky brightness
    Details:
        R. Perez, R. Seals, J. Michalsky, "All-weather model for sky luminance distribution—Preliminary configuration and
        validation", Solar Energy, Volume 50, Issue 3, 1993, Pages 235-245.
    """
    am = air_mass(sun_zenith, altitude, with_pvlib=with_pvlib)
    dni_extra = sun_extraradiation(dates)
    return am * dhi / dni_extra


def f_clear_sky(epsilon):
    """ Clear-sky / overcast mixing fractions for blended sky irradiance model

    ref :  J. Mardaljevic. Daylight Simulation: Validation, Sky Models and
    Daylight Coefficients. PhD thesis, De Montfort University,
    Leicester, UK, 2000.
    p193,eq. 5-10

    Args:
        epsilon: all weather sky clearness
    """
    return numpy.minimum(1, (epsilon - 1) / (1.41 - 1))


def clearness_index(dates, ghi):
    """Clearness index (Liu and Jordan 1960)

    Args:
        dates: A pandas datetime index (as generated by pandas.date_range)
        ghi: global horizontal irradiance

    Returns:
        clearness index

    Details:
        Benjamin Y.H. Liu, Richard C. Jordan, "The interrelationship and characteristic distribution of direct, diffuse
        and total solar radiation", Solar Energy, Volume 4, Issue 3, 1960, Pages 1-19.
    """
    dni_extra = sun_extraradiation(dates)
    return ghi / dni_extra


def spitters_daily_diffuse_fraction(ghi, daydate=_daydate):
    """ estimate the diffuse fraction using daily averages of global horizontal irradiance"""

    So = sun_extraradiation(daydate=daydate).mean()
    RsRso = ghi / So

    return numpy.where(RsRso <= 0.07, 1,
                   numpy.where(RsRso <= 0.35, 1 - 2.3 * (RsRso - 0.07) ** 2,
                               numpy.where(RsRso <= 0.75, 1.33 - 1.46 * RsRso,
                                           0.23)))


def micromol_per_joule(dates, ghi, sun_elevation, temp_dew=None):
    """Conversion factor between micromol of PAR and Joule of broadband shortwave solar radiation (Alados et al. 1996)

    Args:
        dates: A pandas datetime index (as generated by pandas.date_range)
        ghi: global horizontal irradiance (W.m-2)
        sun_elevation: the elevation angle of the sun (deg)
        temp_dew: the dew point temperature (°C) (optional, yields better estimates)

    Details:
        I. Alados, I. Foyo-Moreno, L. Alados-Arboledas, "Photosynthetically active radiation: measurements and modelling",
        Agricultural and Forest Meteorology, Volume 78, Issues 1–2, 1996, Pages 121-131,
    """
    beta = numpy.radians(sun_elevation)
    kt = clearness_index(dates, ghi)
    if temp_dew is None:
        return 1.832 - 0.191 * numpy.log(kt) + 0.099 * numpy.sin(beta)
    else:
        return 1.791 - 0.190 * numpy.log(kt) + 0.005 * temp_dew + 0.049 * numpy.sin(beta)


def clear_sky_irradiances(dates=None, daydate=_daydate, longitude=_longitude,
                          latitude=_latitude, altitude=_altitude,
                          timezone=_timezone, with_pvlib=True):
    """ Estimate component of sky irradiance for clear sky conditions

    Args:
        dates: A pandas datetime index (as generated by pandas.date_range). If
            None, daydate is used.
        daydate: (str) yyyy-mm-dd (not used if dates is not None).
        longitude: (float) in degrees
        latitude: (float) in degrees
        altitude: (float) in meter
        timezone:(str) the time zone (not used if dates are already localised)
        with_pvlib : Should we use pvlib library to estimate clearsky ?

    Returns:
        a pandas dataframe with global horizontal irradiance, direct normal
        irradiance and diffuse horizontal irradiance.

    Details:
        if with_pvlib is True, the Ineichen (2002) model is used, otherwise GHI is computed after Haurwitz (1945) and DNI
        after Meinel (1976).

        P. Ineichen and R. Perez, "A New airmass independent formulation for the Linke turbidity coefficient",
         Solar Energy, vol 73, pp. 151-157, 2002
        B. Haurwitz, "Insolation in Relation to Cloudiness and Cloud Density", Journal of Meteorology, vol. 2,
         pp. 154-166, 1945.
        A. B. Meinel and M. P. Meinel, Applied solar energy. Reading, MA: Addison-Wesley Publishing Co., 1976

    """

    location = dict(latitude=latitude,
                    longitude=longitude,
                    altitude=altitude,
                    timezone=timezone)
    df = sun_position(dates=dates, daydate=daydate, **location)
    am = air_mass(df['zenith'], altitude, with_pvlib=with_pvlib)
    dni_extra = sun_extraradiation(df.index)

    if pvlib and with_pvlib:
        tl = pvlib.clearsky.lookup_linke_turbidity(df.index, latitude,
                                                   longitude)

        clearsky = pvlib.clearsky.ineichen(df['zenith'], am, tl,
                                           dni_extra=dni_extra,
                                           altitude=altitude)
        clearsky = pandas.concat([df, clearsky], axis=1)
    else:
        clearsky = df
        z = numpy.radians(df['zenith'])
        clearsky['ghi'] = 1098 * numpy.cos(z) * numpy.exp(-0.057 / numpy.cos(z))
        clearsky['dni'] = dni_extra * numpy.power(0.7, numpy.power(am, 0.678))
        clearsky['dhi'] = clearsky['ghi'] - horizontal_irradiance(clearsky['dni'], df['elevation'])

    return clearsky.loc[:, ['ghi', 'dni', 'dhi']]


def actual_sky_irradiances(dates=None, daydate=_daydate, ghi=None,
                           attenuation=None,
                           pressure=101325, temp_dew=None, longitude=_longitude,
                           latitude=_latitude, altitude=_altitude,
                           timezone=_timezone, with_pvlib=True):
    """ Estimate component of sky irradiances from measured actual global
    horizontal irradiance or attenuated clearsky conditions.

    Args:
        dates: A pandas datetime index (as generated by pandas.date_range). If
            None, daydate is used.
        daydate: (str) yyyy-mm-dd (not used if dates is not None).
        ghi: (array_like) : global horizontal irradiance (W. m-2).If None
         (default) clear_sky irradiance are used
        attenuation: (float) a attenuation factor for ghi (actual_ghi =
         attenuation * ghi). If None (default), no attenuation is applied
        pressure: the site pressure (Pa) (for dirint model)
        temp_dew: the dew point temperature (dirint model)
        longitude: (float) in degrees
        latitude: (float) in degrees
        altitude: (float) in meter
        timezone:(str) the time zone (not used if dates are already localised)
        with_pvlib : Should we use pvlib library to estimate sky irradiances ?

    Returns:
        a pandas dataframe with global horizontal irradiance, direct normal
        irradiance and diffuse horizontal irradiance.

    Details:
        if with_pvlib is True, the 'dirint' model of Perez (1992) is used, otherwise the model of Spitters (1986) is used

        Perez, R., P. Ineichen, E. Maxwell, R. Seals and A. Zelenka, (1992). "Dynamic Global-to-Direct Irradiance
         Conversion Models", ASHRAE Transactions-Research Series, pp. 354-369
        Spitters CJT, Toussaint HAJM, Goudriaan J (1986) "Separating the diffuse and direct component of global
         radiation and its implications for modeling canopy photosynthesis.Part I.Components of incoming radiation",
         Agricultural and Forest Meteorology 38: 217-229.
    """

    location = dict(latitude=latitude,
                    longitude=longitude,
                    altitude=altitude,
                    timezone=timezone)
    df = sun_position(dates=dates, daydate=daydate, **location)

    if ghi is None:
        cs = clear_sky_irradiances(dates=df.index, **location, with_pvlib=with_pvlib)
        ghi = cs['ghi']

    df['ghi'] = ghi

    if attenuation is not None:
        df.ghi *= attenuation

    if pvlib and with_pvlib:
        df['dni'] = pvlib.irradiance.dirint(df.ghi, 90 - df.elevation, df.index,
                                            pressure=pressure, temp_dew=temp_dew)
        df['dhi'] = df.ghi - horizontal_irradiance(df.dni, df.elevation)
    else:
        Io = sun_extraradiation(df.index)
        costheta = numpy.sin(numpy.radians(df.elevation))
        So = Io * costheta
        RsRso = df.ghi / So
        R = 0.847 - 1.61 * costheta + 1.04 * costheta * costheta
        K = (1.47 - R) / 1.66
        RdRs = numpy.where(RsRso <= 0.22, 1,
                           numpy.where(RsRso <= 0.35,
                                       1 - 6.4 * (RsRso - 0.22) ** 2,
                                       numpy.where(RsRso <= K,
                                                   1.47 - 1.66 * RsRso,
                                                   R)))
        df['dhi'] = df.ghi * RdRs
        df['dni'] = normal_irradiance(df['ghi'] - df['dhi'], df['elevation'])

    return df.loc[:, ('ghi', 'dhi', 'dni')]


def sky_irradiance(dates=None, daydate=_daydate, ghi=None, dhi=None, ppfd=None,
                   attenuation=None,
                   pressure=101325, temp_dew=None, longitude=_longitude,
                   latitude=_latitude, altitude=_altitude,
                   timezone=_timezone, with_pvlib=True):
    """ Estimate variables related to sky irradiance.

    Args:
        dates: A pandas datetime index (as generated by pandas.date_range). If
            None, daydate is used.
        daydate: (str) yyyy-mm-dd (not used if dates is not None).
        ghi: (array_like) : global horizontal irradiance (W. m-2).If None
         (default) clear_sky irradiance are used
        dhi: (array-like): diffuse horizontal irradiance
        attenuation: (float) a attenuation factor for ghi (actual_ghi =
         attenuation * ghi). If None (default), no attenuation is applied. If
         dhi is not None, this parameter is not taken into account.
        ppfd: (array-like) photosynthetically active photon flux density (micromol.m-2.s-1) component of ghi. If None
         (default), ppfd will be estimated as a function of meteoroligcal conditions and ghi
        pressure: the site pressure (Pa) (for dirint model)
        temp_dew: the dew point temperature (dirint model)
        longitude: (float) in degrees
        latitude: (float) in degrees
        altitude: (float) in meter
        timezone:(str) the time zone (not used if dates are already localised)
        with_pvlib : Should we use pvlib library to estimate sky irradiances ?

    Returns:
        a pandas dataframe with azimuth, zenital and elevation angle of the sun, global horizontal irradiance, direct
        normal irradiance and diffuse horizontal irradiance of the sky.
    """

    location = dict(latitude=latitude,
                    longitude=longitude,
                    altitude=altitude,
                    timezone=timezone)
    df = sun_position(dates=dates, daydate=daydate, **location)
    if len(df) < 1:  # night
        if ghi is not None:  # twilight conditions (sun_el < 0, ghi > 0)
            df = sun_position(dates=dates, daydate=daydate, filter_night=False, **location)
            df['ghi'] = ghi
            df['dhi'] = ghi
            df['dni'] = 0
            df = df.loc[df.ghi > 0, :]
        else:
            df['ghi'] = 0
            df['dhi'] = 0
            df['dni'] = 0
    else:   # day
        if ghi is None or dhi is None:
            irr = actual_sky_irradiances(dates=df.index, ghi=ghi,
                                         attenuation=attenuation, pressure=pressure,
                                         temp_dew=temp_dew, with_pvlib=with_pvlib, **location)
            df = pandas.concat([df, irr], axis=1)
        else:
            df['ghi'] = ghi
            df['dhi'] = dhi
            df['dni'] = normal_irradiance(numpy.array(ghi) - numpy.array(dhi),
                                          df.elevation)
    if ppfd is None:
        ppfd = df.ghi * micromol_per_joule(df.index, df.ghi, df.elevation, temp_dew=temp_dew)
    df['ppfd'] = ppfd

    df = df.rename(columns={'azimuth': 'sun_azimuth', 'elevation': 'sun_elevation', 'zenith': 'sun_zenith'})

    return df.loc[:,
           ['sun_azimuth', 'sun_zenith', 'sun_elevation', 'ghi', 'dni', 'dhi', 'ppfd']]




def mean_shortwave_irradiance(sky_irradiance, relative_global_irradiances, areas):
    df = sky_irradiance
    return df.ghi.mean() * relative_global_irradiances * areas / areas.sum()


def mean_ppfd(sky_irradiance, relative_global_irradiances, areas, temp_dew=None):
    df = sky_irradiance
    par = df.ghi * micromol_per_joule(df.index, df.ghi, df.sun_elevation, temp_dew=temp_dew)
    return par.mean() * relative_global_irradiances * areas / areas.sum()


def ipar(sky_irradiance, relative_global_irradiances, areas):
    return mean_ppfd(sky_irradiance, relative_global_irradiances, areas) * areas.sum() * 3600 * 4.57 / 1e6


def ppfd_h(sky_irradiance, relative_direct_irradiance_h, relative_diffuse_irradiance_h, areas):
    pass


def short_wave_h(sky_irradiance, relative_direct_irradiance_h, relative_diffuse_irradiance_h):
    pass



