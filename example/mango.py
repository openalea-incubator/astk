""" Example script for reading / manipulating meteo data of mangosim
"""

import pandas

from openalea.astk.Weather import Weather
import openalea.plantgl.all as pgl

from math import radians, pi
#from alinea.adel.astk_interface import AdelWheat
from vplants.mangosim.util_path import data

from vplants.fractalysis.light.directLight import directionalInterception

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
mango = pgl.Scene(data('generated_mtg/fruitstructure.bgeom'))  
# meteo
weather = Weather(data('environment/rayostpierre2002.csv'), reader=reader, timezone='Indian/Reunion', localisation={'city':'Saint-Pierre', 'latitude':-21.32, 'longitude':55.5})



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

for one_day in weather.date_range_index('2002-12-02','2002-12-15'):
  # sun/sky for one day
  #see weather.date_range_index for generating a list of days
  sun, sky, = weather.light_sources(one_day, 'PPFD', irradiance='normal', scale=1e-6)
  # sun and sky irradiance are in mol.m-2 (PPFD in micromol.m-2.s-1 * dt (s) * scale)
  print one_day[0],
  print len(sun['irradiance'])
  #print sun
  directions =zip(sun['azimuth'],sun['elevation'], sun['irradiance']) #+ zip(sky['azimuth'],sky['elevation'], sky['irradiance'])  

  res = directionalInterception(mango, directions, azel2vect = azel2vect)

  #print res

