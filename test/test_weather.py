from openalea.astk.Weather import Weather
from openalea.astk.data_access import meteo00_01


def test_instantiate():
    weather = Weather()
    assert weather.data is None
    data = meteo00_01()
    weather = Weather(data)
    assert len(weather.data) == 7296


def test_date_range_index():
    data = meteo00_01()
    weather = Weather(data)
    index = weather.date_range_index('2000-12-31')
    assert len(index) == 24
    index = weather.date_range_index('2000-12-31', by=3)
    assert len(index) == 3
    index = weather.date_range_index('2000-12-31', '2001-01-02', by=24)
    assert len(index) == 2
    assert len(index[0]) == 24
