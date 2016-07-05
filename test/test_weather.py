from alinea.astk.Weather import Weather
from alinea.astk.data_access import get_path


def test_instantiate():
    weather = Weather()
    assert weather.data is None
    path = get_path('meteo00-01.txt')
    weather = Weather(path)
    assert len(weather.data) == 7296


def test_date_range_index():
    path = get_path('meteo00-01.txt')
    weather = Weather(path)
    index = weather.date_range_index('2000-12-31')
    assert len(index) == 24
    index = weather.date_range_index('2000-12-31', by=3)
    assert len(index) == 3
    index = weather.date_range_index('2000-12-31', '2001-01-02', by=24)
    assert len(index) == 2
    assert len(index[0]) == 24
