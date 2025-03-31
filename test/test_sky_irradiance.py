import numpy
from openalea.astk.meteorology.sky_irradiance import (
    clear_sky_irradiances,
    actual_sky_irradiances,
    sky_irradiance,
    all_weather_sky_clearness,
    f_clear_sky)



def test_clear_sky_irradiances():
    df = clear_sky_irradiances()
    assert len(df) == 15
    df2 = clear_sky_irradiances(with_pvlib=False)
    assert len(df2) == 15
    numpy.testing.assert_allclose(df.ghi, df2.ghi, atol=55)


def test_actual_sky_irradiance():
    df = actual_sky_irradiances()
    assert len(df) == 15
    assert df.dhi.sum() / df.ghi.sum() < 0.25
    df2 = actual_sky_irradiances(with_pvlib=False)
    assert len(df2) == 15
    numpy.testing.assert_allclose(df.dhi, df2.dhi, atol=80)

    df = actual_sky_irradiances(attenuation=0.2)
    assert df.dhi.sum() / df.ghi.sum() > 0.99
    df2 = actual_sky_irradiances(attenuation=0.2, with_pvlib=False)
    numpy.testing.assert_allclose(df.ghi, df.dhi, rtol=.05)
    numpy.testing.assert_allclose(df2.ghi, df2.dhi, rtol=.05)


def test_sky_irradiances():
    df = sky_irradiance()
    assert len(df) == 15
    assert numpy.isclose((df.ghi/df.ppfd).mean(), 0.47, atol=0.01)
    assert df.dhi.sum() / df.ghi.sum() < 0.25
    df = sky_irradiance(attenuation=0.2)
    assert df.dhi.sum() / df.ghi.sum() > 0.99
    df2 = sky_irradiance(with_pvlib=False)
    assert len(df2) == 15


def test_fsun():
    df = sky_irradiance()
    epsilon = all_weather_sky_clearness(df.dni, df.dhi, df.zenith)
    f_clear = f_clear_sky(epsilon)
    assert f_clear.sum() == 14

    df = sky_irradiance(attenuation=0.2)
    epsilon = all_weather_sky_clearness(df.dni, df.dhi, df.zenith)
    f_clear = f_clear_sky(epsilon)
    assert f_clear.sum() < 1