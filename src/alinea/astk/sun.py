""" A collection of equation for modelling sun position and sun irradiance
"""

import numpy

def ecliptic_longitude(dayofyear):
    """ Ecliptic longitude (radians)
      Approximation formula by Grebet (1993), in Crop structure and light microclimate
    """
    omega = 0.017202 * (dayofyear - 3.244)
    return omega + 0.03344 * numpy.sin(omega) * (1 + 0.021 * numpy.cos(omega)) - 1.3526
        
def declination(dayofyear, method = "default"):
    """ Sun declination angle(rad) as a function of day of year
    
    Parameters:
        - method: a string indicating the method for computing (either 'Spencer' or 'default')
    """  
    if method == "Spencer": # usefull for checking time equation
        # Approx Spencer 1971
        # J. W. Spencer, Fourier series representation of the sun, Search, vol. 2, p. 172, 1971
        x = 2 * numpy.pi * (dayofyear - 1) / 365.
        dec = 0.006918\
                - 0.399912 * numpy.cos(x) + 0.070257 * numpy.sin(x)\
                - 0.006758 * numpy.cos(2 * x) + 0.000907 * numpy.sin(2 * x)\
                - 0.002697 * numpy.cos(3 * x) + 0.001480 * numpy.sin(3 * x)
    else:
        #  'true' declination (provided that the obliquity of the ecliptic and the ecliptic longitude are exact)
        # Michalsky, J. J. “The Astronomical Almanac’s Algorithm for Approximate Solar Position (1950-2050)”. Solar Energy. Vol. 40, No. 3, 1988; pp. 227-235, USA
        obliquity = 23.44 # constant approximation
        sidec = numpy.sin(numpy.radians(obliquity)) * numpy.sin(ecliptic_longitude(dayofyear))
        dec = numpy.arcsin(sidec)
    return dec

def eot(dayofyear):
    """ equation of time (hours) :discrepancy between true solar time and local solar time
        Approximation formula by Grebet (1993), in Crop structure and light microclimate
    """
    omega = 0.017202 * (dayofyear - 3.244)
    eclong = ecliptic_longitude(dayofyear)
    tanphi = 0.91747 * numpy.sin(eclong) / numpy.cos(eclong)
    phi = numpy.arctan(tanphi) - omega + 1.3526
    phi = numpy.where((phi + 1) <= 0, numpy.mod(phi + 1 + 1000 * numpy.pi, numpy.pi) - 1, phi)
    return phi * 229.2 / 60
    
    
def solar_time(hUTC, dayofyear, longitude):
    """ Local solar time(hour)
    
        hUTC : universal time (hour)
        longitude is in degrees
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
    if d < 0:
        d = d + numpy.pi    
    return 2 * d / numpy.pi * 12

def sun_elevation(hUTC, dayofyear, longitude, latitude):
    """ sun elevation angle (degrees, from soil to sun) and its sine (= cosine of the zenith angle)
    """
    lat = numpy.radians(latitude)
    decli = declination(dayofyear)
    omega = hour_angle(hUTC, dayofyear, longitude)
    
    sinh = numpy.cos(lat) * numpy.cos(decli) * numpy.cos(omega) + numpy.sin(lat) * numpy.sin(decli)
    h = numpy.degrees(numpy.arcsin(sinh))
    
    return h, sinh
    
def sun_azimuth(hUTC, dayofyear, longitude, latitude):
    """ sun azimuth angle
    
        two value are return : azN, that is the sun azimuth (degrees) in the North-clockwise convention, 
                               and azS, that is the sun azimuth (radians) in the South-clockwise convention
    """
    lat = numpy.radians(latitude)
    decli = declination(dayofyear)
    omega = hour_angle(hUTC, dayofyear, longitude)
    
    azN = numpy.pi + numpy.arctan2(numpy.sin(omega), numpy.cos(omega) * numpy.sin(lat) - numpy.tan(decli) * numpy.cos(lat))
    azN = numpy.mod(azN, 2 * numpy.pi)
    azS = azN - numpy.pi
    
    return numpy.degrees(azN), azS
    
def extraterrestrial_radiation(dayofyear, method='Spencer'):
    """ Extraterrestrial radiation (W.m2) at the top of the atmosphere
    """
    
    if method == 'Asce':
        #R. G. Allen, Environmental, and E. Water Resources institute . Task Committee on Standardization of Reference, 
        #The ASCE standardized reference evapotranspiration equation. Reston, Va.: American Society of Civil Engineers, 2005.
        Io = 1367.7 * (1 + 0.033 * numpy.cos(2 * numpy.pi * dayofyear / 365.))
    else:
        # Approx Spencer 1971
        # J. W. Spencer, Fourier series representation of the sun, Search, vol. 2, p. 172, 1971
        x = 2 * numpy.pi * (dayofyear - 1) / 365.
        Io = 1366.1 * (1.00011 \
                       + 0.034221 * numpy.cos(x) + 0.00128 * numpy.sin(x)\
                       - 0.000719 * numpy.cos(2* x) + 0.000077 * numpy.sin(2 * x))
                       
    return Io

  
def sun_irradiance(hUTC, dayofyear, longitude, latitude):
    """ sun irradiance (W.m2) through a plane perpendicular to sun direction at the top of the atmosphere 
        for a given day, hour and location
    """
    Io = extraterrestrial_radiation(dayofyear)
    _, sinh = sun_elevation(hUTC, dayofyear, longitude, latitude)
    return Io * sinh
    
def direct_normal_irradiance(hUTC, dayofyear, longitude, latitude):
    """ sun irradiance (W.m2) through a plane perpendicular to sun direction at ground level for clear sky days
    
        Simple geometric approximation of optical attenuation through the atmospherer after
        A. B. Meinel and M. P. Meinel, Applied solar energy. Reading, MA: Addison-Wesley Publishing Co., 1976
    """
    Io = extraterrestrial_radiation(dayofyear)
    _, sinh = sun_elevation(hUTC, dayofyear, longitude, latitude)
    AM = 1 / sinh
    return Io * sinh * numpy.power(0.7, numpy.power(AM, 0.678))
  

    

