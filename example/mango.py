""" Example script for reading / manipulating meteo data of mangosim
"""

import pandas

from alinea.astk.Weather import Weather
import openalea.plantgl.all as pgl

from math import radians, pi
from alinea.adel.astk_interface import AdelWheat



def reader(data_file='rayostpierre2002.csv'):
    """ reader for mango meteo files """
    


    data = pandas.read_csv(data_file, parse_dates=['Date'],
                               delimiter = ';',
                               usecols=['Date','Rayonnement','Temperature_Air','HR'], dayfirst=True)
    data = data.rename(columns={'Date':'date',
                                 'Rayonnement':'global_radiation',
                                 'Temperature_Air':'temperature_air',
                                 'HR':'relative_humidity'})
    # convert J.cm2.h-1 to W.m-2
    data['global_radiation'] *= (10000. / 3600)
    return data
  
# a strange mango tree
adel = AdelWheat()
mango = adel.setup_canopy(500)  
# meteo
weather = Weather('rayostpierre2002.csv', reader=reader, timezone='Indian/Reunion', localisation={'city':'Saint-Pierre', 'latitude':-21.32, 'longitude':55.5})
# sun/sky for one day
day = pandas.date_range(start = "2002-10-02", periods=24, freq='H')
#see also weather.split for generating a list of days
sun, sky, = weather.light_sources(day, 'PPFD', irradiance='normal', scale=1e-6)
# sun and sky irradiance are in mol.m-2 (PPFD in micromol.m-2.s-1 * dt (s) * scale)



# converter for azimuth elevation 
# az,el are expected in degrees, in the North-clocwise convention
# In the scene, positive rotations are counter-clockwise
#north is the angle (degrees, positive counter_clockwise) between X+ and North
def azel2vect(az, el, north=0):
  azimuth = radians(north - az)
  zenith = radians(90 - el)
  v = -pgl.Vector3(pgl.Vector3.Spherical( 1., azimuth, zenith ) )
  v.normalize()
  return v

scene = adel.scene(mango)
directions =zip(sun['azimuth'],sun['elevation'], sun['irradiance']) + zip(sky['azimuth'],sky['elevation'], sky['irradiance'])  

#res = directionalInterception(scene, directions, azel2vect = azel2vect)

