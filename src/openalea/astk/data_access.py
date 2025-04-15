
""" Set of function to work with data resources
"""
try:
    from importlib.resources import files, as_file
except ImportError:
    from importlib_resources import files, as_file
import pandas


datadir = files('openalea.astk_data')


def get_data_dir():
    return datadir


def get(file_name):
    """ Retrieve the content of a given filename
    located in the data part of this package.

    args:
     - filename (str): name of the file to read

    return:
     - (str): content of the file
    """
    return (datadir / file_name).read_text()


def ls():
    """ List all files and directories .

    return:
     - (list of (str, bool)): list the content of dir_name
                       without any specific order, items are
                       (entity_name, is_directory)
    """
    return list(datadir.iterdir())

    
def read_meteo_mpt(fn):
    with as_file(datadir / fn) as p:
        df = pandas.read_csv(p)
        df.index = pandas.to_datetime(df.iloc[:, 0], utc=True)
        df.index = df.index.tz_convert('Europe/Paris')
    return df.loc[:, ['ghi']]


def montpellier_spring_2013():
    return read_meteo_mpt('incoming_radiation_ZB13.csv')


def montpellier_winter_2013():
    return read_meteo_mpt('incoming_radiation_ZA13.csv')


def septo3d_reader(data_file, sep='\t'):
    """ reader for septo3D meteo files """
    with as_file(datadir / data_file) as p:
        data = pandas.read_csv(p, sep=sep)
    # ,
    # usecols=['An','Jour','hhmm','PAR','Tair','HR','Vent','Pluie'])

    data['date'] = pandas.to_datetime(data['An'] * 1000 + data['Jour'], format='%Y%j')+pandas.to_timedelta(data.hhmm/100, unit='h')
    data.index = data.date
    data = data.rename(columns={'PAR': 'PPFD', 'Tair': 'temperature_air',
                                'HR': 'relative_humidity', 'Vent': 'wind_speed',
                                'Pluie': 'rain'})
    return data


def meteo00_01():
    return septo3d_reader("meteo00-01.txt")