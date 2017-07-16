from alinea.astk.sun_and_sky import sun_path, sky_discretisation, \
    diffuse_light_irradiance, light_sources
import numpy


def test_diffuse_light_irradiance():
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
    assert azimuth[numpy.argmax(d)] >= 180
    # flip North to South
    d = diffuse_light_irradiance(elevation, azimuth, strd, sky_orientation=180,
                                 sky_type='clear_sky',
                                 irradiance='horizontal',
                                 sun_elevation=midday['elevation'],
                                 sun_azimuth=midday['azimuth'])
    assert azimuth[numpy.argmax(d)] <= 10


def test_light_sources():
    sun, sky = light_sources(type='soc')
    assert sun is None
    el, az, irr = sky
    assert len(az) == len(el) == len(irr) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    sun, sky = light_sources(type='clear_sky')
    az, el, irr = sun
    assert len(az) == len(el) == len(irr) == 9
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)
    el, az, irr = sky
    assert len(az) == len(el) == len(irr) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)




