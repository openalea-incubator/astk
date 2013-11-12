# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 14:29:15 2013

@author: lepse
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from math import exp

    
    
def septo3d_reader(data_file):
    """ reader for septo3D meteo files """
    
    def parse(yr, doy, hr):
        """ Convert the 'An', 'Jour' and 'hhmm' variables of the meteo dataframe in a datetime object (%Y-%m-%d %H:%M:%S format)
        """
        an, jour, heure = [int(x) for x in [yr, doy, hr/100]]
        dt = datetime(an - 1, 12, 31)
        delta = timedelta(days=jour, hours=heure)
        return dt + delta

    data = pd.read_csv(data_file, parse_dates={'datetime':['An','Jour','hhmm']},
                               date_parser=parse, sep = '\t',
                               usecols=['An','Jour','hhmm','PAR','Tair','HR','Vent','Pluie'])

    data.index = data.datetime
    data = data.rename(columns={'PAR':'PPFD',
                                 'Tair':'temperature_air',
                                 'HR':'relative_humidity',
                                 'Vent':'wind_speed',
                                 'Pluie':'rain'})
    return data

def PPFD_to_global(data):
    """ Convert the PAR (ppfd in micromol.m-2.sec-1) in global radiation (J.m-2.s-1, ie W/m2)
    1 WattsPAR.m-2 = 4.6 ppfd, 1 Wglobal = 0.48 WattsPAR)
    """
    PAR = data[['PPFD']].values
    return (PAR * 1./4.6) / 0.48


def Psat(T):
    """ Saturating water vapor pressure (kPa) at temperature T (Celcius) with Tetens formula
    """
    return 0.6108 * np.exp(17.27 * T / (237.3 + T))

def humidity_to_vapor_pressure(data):
    """ Convert the relative humidity (%) in water vapor pressure (kPa)
    """
    humidity = data[['relative_humidity']].values
    Tair = data[['temperature_air']].values
    return humidity / 100. * Psat(Tair)

            
class Weather(object):
    """ Class compliying echap local_microclimate model protocol (meteo_reader).
        expected variables of the data_file are:
            - 'An'
            - 'Jour'
            - 'hhmm' : hour and minutes (universal time, UTC)
            - 'PAR' : Quantum PAR (ppfd) in micromol.m-2.sec-1
            - 'Pluie' : Precipitation (mm)
            - 'Tair' : Temperature of air (Celcius)
            - 'HR': Humidity of air (kPa)
            - 'Vent' : Wind speed (m.s-1)
    """
    def __init__(self, data_file='', reader = septo3d_reader):
        self.data_path = data_file
        self.models = {'global_radiation': PPFD_to_global, 
                        'vapor_pressure': humidity_to_vapor_pressure}
        if data_file is '':
            self.data = None
        else:
            self.data = reader(data_file)

    def get_weather(self, time_sequence):
        """ Return weather data for a given time sequence
        """
        return self.data.truncate(before = time_sequence[0], after = time_sequence[-1])
      
    def get_variable(self, what, time_sequence):
        """
        return values of what at date specified in time sequence
        """
        return self.data[what][time_sequence]

    def check_var(self, varnames = [], models = {}):
        """ Check if varnames are in data and try to create them if absent using defaults models or models provided in arg.
        Return a bool list with True if the variable is present or has been succesfully created, False otherwise.
        
        Parameters: 
        
        - varnames : a list of name of variable to check
        - models a dict (name: model) of models to use to generate the data. models receive data as argument
        """
        
        models.update(self.models)
        
        check = []
 
        for v in varnames:
            if v in self.data.columns:
                check.append(True)
            else:
                if v in models.keys():
                    values = models[v](self.data)
                    self.data[v] = values
                    check.append(True)
                else:
                    check.append(False)
        return check
        
    # def add_global_radiation(self):
        # """ Add the column 'global_radiation' to the data frame.
        # """
        # data = self.data
        # global_radiation = self.PPFD_to_global(data['PPFD'])
        # data = data.join(global_radiation)
        
    # def add_vapor_pressure(self, globalclimate):
        # """ Add the column 'global_radiation' to the data frame.
        # """
        # vapor_pressure = self.humidity_to_vapor_pressure(globalclimate['relative_humidity'], globalclimate['temperature_air'])
        # globalclimate = globalclimate.join(vapor_pressure)
        # mean_vapor_pressure = globalclimate['vapor_pressure'].mean()
        # return mean_vapor_pressure, globalclimate

    # def fill_data_frame(self):
        # """ Add all possible variables.

        # For instance, call the method 'add_global_radiation'.
        # """
        # self.add_global_radiation()

    # def next_date(self, timestep, t_deb):
        # """ Return the new t_deb after the timestep 
        # """
        # return t_deb + timedelta(hours=timestep)

                
#
# To do /add (pour ratp): 
# file meteo exemples
# add RdRs (ratio diffus /global)
# add NIR = RG - PAR
# add Ratmos = epsilon sigma Tair^4, epsilon = 0.7 clear sky, eps = 1 overcast sky
# add CO2
#
# peut etre aussi conversion hUTC -> time zone 'euroopean' 

##
# sinon faire des generateur pour tous les fichiers ratp
#
