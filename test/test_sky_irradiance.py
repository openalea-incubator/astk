import numpy
from alinea.astk.meteorology.sky_irradiance import clear_sky_irradiances, \
    actual_sky_irradiances, sky_irradiances
from alinea.astk.meteorology.sky_irradiance_astk import \
    clear_sky_irradiances as clear_sky_irradiances_astk, \
    actual_sky_irradiances as actual_sky_irradiances_astk, \
    sky_irradiances as sky_irradiances_astk


def test_clear_sky_irradiances():
    df = clear_sky_irradiances()
    assert len(df) == 15
    df2 = clear_sky_irradiances_astk()
    assert len(df2) == 15
    numpy.testing.assert_allclose(df.ghi, df2.ghi, atol=55)


def test_actual_sky_irradiance():
    df = actual_sky_irradiances()
    assert len(df) == 15
    assert df.dhi.sum() / df.ghi.sum() < 0.25
    df2 = actual_sky_irradiances_astk()
    assert len(df2) == 15
    numpy.testing.assert_allclose(df.dhi, df2.dhi, atol=80)

    df = actual_sky_irradiances(attenuation=0.2)
    assert df.dhi.sum() / df.ghi.sum() > 0.99
    df2 = actual_sky_irradiances_astk(attenuation=0.2)
    numpy.testing.assert_allclose(df.ghi, df.dhi, rtol=.05)
    numpy.testing.assert_allclose(df2.ghi, df2.dhi, rtol=.05)


def test_sky_irradiances():
    df = sky_irradiances()
    assert len(df) == 15
    assert df.dhi.sum() / df.ghi.sum() < 0.25
    df = sky_irradiances(attenuation=0.2)
    assert df.dhi.sum() / df.ghi.sum() > 0.99
    df2 = sky_irradiances_astk()
    assert len(df2) == 15