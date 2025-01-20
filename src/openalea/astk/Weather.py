# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 14:29:15 2013

@author: lepse
"""

from __future__ import division
from __future__ import print_function
import pandas
import pytz
from datetime import timedelta


from alinea.astk.TimeControl import *
from alinea.astk.meteorology.sun_position import sun_position
import alinea.astk.sun_and_sky as sunsky


def septo3d_reader(data_file, sep):
    """ reader for septo3D meteo files """

    data = pandas.read_csv(data_file, sep=sep)
    # ,
    # usecols=['An','Jour','hhmm','PAR','Tair','HR','Vent','Pluie'])

    data['date'] = pandas.to_datetime(data['An'] * 1000 + data['Jour'], format='%Y%j')+pandas.to_timedelta(data.hhmm/100, unit='H')
    data.index = data.date
    data = data.rename(columns={'PAR': 'PPFD', 'Tair': 'temperature_air',
                                'HR': 'relative_humidity', 'Vent': 'wind_speed',
                                'Pluie': 'rain'})
    return data

def PPFD_to_global(data):
    """ Convert the PAR (ppfd in micromol.m-2.sec-1)
    in global radiation (J.m-2.s-1, ie W/m2)
    1 WattsPAR.m-2 = 4.6 ppfd, 1 Wglobal = 0.48 WattsPAR)
    """
    PAR = data[['PPFD']].values
    return (PAR * 1. / 4.6) / 0.48


def global_to_PPFD(data):
    """ Convert the global radiation (J.m-2.s-1, ie W/m2)
    in PAR (ppfd in micromol.m-2.sec-1)
    1 WattsPAR.m-2 = 4.6 ppfd, 1 Wglobal = 0.48 WattsPAR)
    """
    Rg = data[['global_radiation']].values
    return Rg * 0.48 * 4.6


def Psat(T):
    """ Saturating water vapor pressure (kPa) at temperature T (Celcius) with Tetens formula
    """
    return 0.6108 * numpy.exp(17.27 * T / (237.3 + T))


def humidity_to_vapor_pressure(data):
    """ Convert the relative humidity (%) in water vapor pressure (kPa)
    """
    humidity = data[['relative_humidity']].values
    Tair = data[['temperature_air']].values
    return humidity / 100. * Psat(Tair)


def linear_degree_days(data, start_date=None, base_temp=0., max_temp=35.):
    df = data['temperature_air'].copy()
    if start_date is None:
        start_date = data.index[0]
    df[df < base_temp] = 0.
    df[df > max_temp] = 0.
    dd = numpy.cumsum((df - base_temp) / 24.)
    if isinstance(start_date, str):
        start_date = pandas.to_datetime(start_date, utc=True)
    return dd - dd[df.index.searchsorted(start_date)]


class Weather:
    """ Class compliying echap local_microclimate model protocol (meteo_reader).
        expected variables of the data_file are:
            - 'An'
            - 'Jour'
            - 'hhmm' : hour and minutes (universal time, UTC)
            - 'PAR' : Quantum PAR (ppfd) in micromol.m-2.sec-1
            - 'Pluie' : Precipitation (mm)
            - 'Tair' : Temperature of air (Celcius)
            - 'HR': Humidity of air (%)
            - 'Vent' : Wind speed (m.s-1)
        - localisation is a {'name':city, 'lontitude':lont, 'latitude':lat} dict
        - timezone indicates the standard timezone name (see pytz infos) to be used for interpreting the date (default 'UTC')
    """

    def __init__(self, data_file='', reader=septo3d_reader,sep='\t', wind_screen=2,
                 temperature_screen=2,
                 localisation={'city': 'Montpellier', 'latitude': 43.61,
                               'longitude': 3.87},
                 timezone='UTC'):
        self.data_path = data_file
        self.models = {'global_radiation': PPFD_to_global,
                       'vapor_pressure': humidity_to_vapor_pressure,
                       'PPFD': global_to_PPFD,
                       'degree_days': linear_degree_days}

        self.timezone = pytz.timezone(timezone)
        if data_file == '':
            self.data = None
        else:
            self.data = reader(data_file,sep)
            date = self.data['date']
            date = [self.timezone.localize(x) for x in date]
            utc = [x.astimezone(pytz.utc) for x in date]
            self.data.index = utc
            self.data.index.name = 'date_utc'

        self.wind_screen = wind_screen
        self.temperature_screen = temperature_screen
        self.localisation = localisation

    def date_range_index(self, start, end=None, by=24):
        """ return a (list of) time sequence that allow indexing one or several time intervals between start and end every 'by' hours
        if end is None, only one time interval of 'by' hours is returned
        
        start and end are expected in local time
        """
        if end is None:
            seq = pandas.date_range(start=start, periods=by, freq='H',
                                    tz=self.timezone.zone)
            return seq.tz_convert('UTC')
        else:
            seq = pandas.date_range(start=start, end=end, freq='H',
                                    tz=self.timezone.zone)
            seq = seq.tz_convert('UTC')
            bins = pandas.date_range(start=start, end=end, freq=str(by) + 'H',
                                     tz=self.timezone.zone)
            bins = bins.tz_convert('UTC')
            return [seq[(seq >= bins[i]) & (seq < bins[i + 1])] for i in
                    range(len(bins) - 1)]

    def get_weather(self, time_sequence):
        """ Return weather data for a given time sequence
        """
        return self.data.truncate(before=time_sequence[0],
                                  after=time_sequence[-1])

    def get_weather_start(self, time_sequence):
        """ Return weather data at start of timesequence
        """
        return self.data.truncate(before=time_sequence[0],
                                  after=time_sequence[0])

    def get_variable(self, what, time_sequence):
        """
        return values of what at date specified in time sequence
        """
        return self.data[what][time_sequence]

    def check(self, varnames=[], models={}, args={}):
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
                    values = models[v](self.data, **args.get(v, {}))
                    self.data[v] = values
                    check.append(True)
                else:
                    check.append(False)
        return check

    def split_weather(self, time_step, t_deb, n_steps):

        """ return a list of sub-part of the meteo data, each corresponding to one time-step"""
        tdeb = pandas.date_range(t_deb, periods=1, freq='H')[0]
        tstep = [tdeb + i * timedelta(hours=time_step) for i in range(n_steps)]
        return [self.data.truncate(before=t,
                                   after=t + timedelta(hours=time_step - 1)) for
                t in tstep]

    def sun_path(self, seq):
        """ Return position of the sun corresponing to a sequence of date
        """
        return sun_position(seq, timezone='utc')

    def light_sources(self, seq, what='global_radiation'):
        """ return direct and diffuse ligh sources representing the sky and the sun
         for a given time period indicated by seq
         Irradiance are accumulated over the whole time period and multiplied by the duration of the period (second) and by scale
        """

        # self.check([what, 'diffuse_fraction'], args={
        #     'diffuse_fraction': {'localisation': self.localisation}})
        latitude = self.localisation['latitude']
        longitude = self.localisation['longitude']
        # TO DO set actual sky
        data = self.data.loc[seq,:]
        sky_irradiance = data[what].sum()
        sky = sunsky.sky_sources(sky_type='soc', irradiance=sky_irradiance,
                                 dates=seq)
        sun = sunsky.sun_sources(irradiance=None, dates=seq, latitude=latitude,
                                 longitude=longitude)
        return sun, sky

    def daylength(self, seq):
        """
        """
        return sunsky.day_length(self.localisation['latitude'], seq.dayofyear)


def weather_node(weather_path):
    return Weather(weather_path)


def weather_check_node(weather, vars, models):
    ok = weather.check(vars, models)
    if not numpy.all(ok):
        print("weather_check: warning, missing  variables!!!")
    return weather


def weather_data_node(weather):
    return weather.data


def weather_start_node(timesequence, weather):
    return weather.get_weather_start(timesequence),


def date_range_node(start, end, periods, freq, tz, normalize,
                    name):  # nodemodule = pandas in wralea result in import errors
    return pandas.date_range(start, end, periods, freq, tz, normalize, name)


def sample_weather(periods=24):
    """ provides a sample weather instance for testing other modules
    """
    #from openalea.deploy.shared_data import shared_data
    #import alinea.septo3d
    import astk_data
    from path import Path

    meteo_path = Path(astk_data.__path__[0])/'meteo00-01.txt'
    #meteo_path = shared_data(alinea.septo3d, 'meteo00-01.txt')
    t_deb = "2000-10-01 01:00:00"
    seq = pandas.date_range(start="2000-10-02", periods=periods, freq='H')
    weather = Weather(data_file=meteo_path)
    weather.check(
        ['temperature_air', 'PPFD', 'relative_humidity', 'wind_speed', 'rain',
         'global_radiation', 'vapor_pressure'])
    return seq, weather


def sample_weather_with_rain():
    seq, weather = sample_weather()
    every_rain = rain_filter(seq, weather)
    rain_timing = IterWithDelays(*time_control(seq, every_rain, weather.data))
    return rain_timing.next().value


def climate_todict(x):
    if isinstance(x, pandas.DataFrame):
        return x.to_dict('list')
    elif isinstance(x, pandas.Series):
        return x.to_dict()
    else:
        return x



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
