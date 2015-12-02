""" Example script for reading / manipulating meteo data of mangosim
"""

import pandas
from alinea.astk.Weather import Weather


def reader(data_file='rayostpierre2002.csv'):
    """ reader for mango meteo files """
    


    data = pandas.read_csv(data_file, parse_dates=['Date'],
                               delimiter = ';',
                               usecols=['Date','Rayonnement','Temperature_Air','HR'], dayfirst=True)
    data = data.rename(columns={'Date':'date',
                                 'Rayonnement':'global_radiation',
                                 'Temperature_Air':'temperature_air',
                                 'HR':'relative_humidity'})
    # convert J.cm2.h-1
    data['global_radiation'] *= (10000. / 3600)
    return data
  

# init + calcul diffus/direct  
weather = Weather('rayostpierre2002.csv', reader=reader, timezone='Indian/Reunion', localisation={'city':'Saint-Pierre', 'latitude':-21.32, 'longitude':55.5})
weather.check(['PPFD'])
weather.add_RdRs()
# meteo for one day
day = pandas.date_range(start = "2002-10-02", periods=24, freq='H')
meteo = weather.get_weather(day)
# for diffuse fractalysis return surface projete moyenne ponderee par les directions
# elevation/azimuth du soleil
sun = weather.sun_course(day)