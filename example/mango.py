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
sun, sky, = weather.light_sources(day, 'PPFD', irradiance='normal')
# sun and sky irradiance are in micromol.m-2



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
res = directionalInterception(scene, directions, azel2vect = azel2vect)
# calcul direct :
# on utilise sun : elevation, azimuth et direct_radiation (W.m2).
# TODO : convention x/Nord => convention azimuth
# TO do : add step in sun_path to choose more sun positions
# call fractalysis
# => resulat en W, pour passage en MJ, multiplier par le delta time = le vrai daylength (to do : more smart/flexible output)
# or : on choisit un jour et on renvoie les position de soileil + la duree qu'il faut pour obtenir les MJ
#
# proto:
# sun_sources, duration = weather.sun_sources(date (day))
# directMJ = fractalysis.run(mtg, sun_sources) * duration (seconds)
#
# diffus
#
# sky = turtle.sky(46)
# sky_sources, duraction = weather.sky_sources(date (day), sky)
# diffuseMJ = fractalysis.run(mtg, sun_sources) * duration (seconds)
#
# PAR = directMJ  + diffuseMJ (* conversion to PPFD)
