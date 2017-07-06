from alinea.astk.sun_and_sky import sun_path, sky_discretisation, \
    diffuse_light_irradiance, light_sources
import numpy

def test_difuse_light_irradiance():
    elevation, azimuth, strd = sky_discretisation()

    d = diffuse_light_irradiance(elevation, azimuth, strd,
                             sky_type='soc',
                             irradiance='horizontal')
    assert len(d) == len(elevation)
    numpy.testing.assert_almost_equal(d.sum(), 1)
    sun = sun_path()
    midday = sun.loc[sun['hUTC'] == 12, ]

    d = diffuse_light_irradiance(elevation, azimuth, strd,
                                 sky_type='clear_sky',
                                 irradiance='horizontal',
                                 sun_elevation=midday['elevation'],
                                 sun_azimuth=midday['azimuth'])
    assert len(d) == len(elevation)
    numpy.testing.assert_almost_equal(d.sum(), 1)
    dd, d_sun = diffuse_light_irradiance(elevation, azimuth, strd,
                                        sky_type='clear_sky',
                                        irradiance='horizontal',
                                        sun_elevation=midday['elevation'],
                                        sun_azimuth=midday['azimuth'],
                                        add_sun=True)
    assert len(dd) == len(elevation)
    assert numpy.var(dd / d) < 1e-6
    numpy.testing.assert_almost_equal(dd.sum() + d_sun, 1)

def test_light_sources():
    az, el, irr = light_sources()
    assert len(az) == len(el) == len(irr) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    az, el, irr = light_sources(type='clear_sky')
    assert len(az) == len(el) == len(irr) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    az, el, irr = light_sources(type='clear_sky', add_sun=True)
    assert len(az) == len(el) == len(irr) == 55
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)


