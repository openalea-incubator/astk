from alinea.astk.sun_and_sky import sky_discretisation, \
    sky_radiance_distribution, sky_sources, sun_sources
import numpy


def test_sky_radiance_distribution():
    elevation, azimuth, strd = sky_discretisation()
    fraction = numpy.array(strd) / sum(strd)

    d = sky_radiance_distribution(elevation, azimuth, fraction,
                                  sky_type='soc')
    assert len(d) == len(elevation)
    numpy.testing.assert_almost_equal(d.sum(), 1)

    # chek max radiance is toward sun direction for clear skies
    sun_elevation = elevation[20]
    sun_azimuth = azimuth[20]
    d = sky_radiance_distribution(elevation, azimuth, strd,
                                  sky_type='clear_sky',
                                  sun_elevation=sun_elevation,
                                  sun_azimuth=sun_azimuth)
    assert len(d) == len(elevation)
    numpy.testing.assert_almost_equal(d.sum(), 1)
    assert numpy.argmax(d) == 20


def test_sky_sources():
    el, az, irr, frac = sky_sources(type='soc')
    assert len(az) == len(el) == len(irr) == len(frac) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)
    numpy.testing.assert_almost_equal(numpy.sum(frac), 1)

    el, az, irr, frac = sky_sources(type='clear_sky')
    assert len(az) == len(el) == len(irr) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    el, az, irr, frac = sky_sources(type='clear_sky', irradiance=None)
    assert irr.max() > 60


def test_sun_source():
    el, az, irr = sun_sources()
    assert len(az) == len(el) == len(irr)
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    el, az, irr = sun_sources(irradiance=None)
    assert irr.max() > 800
