from alinea.astk.Weather import Weather
from alinea.astk.data_access import get_path



def test_instantiate():
    path = get_path('meteo00-01.txt')
    weather = Weather(path)
    assert len(weather.data) == 7296
    
