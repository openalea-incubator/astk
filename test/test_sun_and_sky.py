from alinea.astk.sun_and_sky import sky_discretisation, \
    sky_radiance_distribution, sky_sources, sun_sources, sun_sky_sources
import numpy
import pandas


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
    el, az, irr = sky_sources(sky_type='soc')
    assert len(az) == len(el) == len(irr) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    el, az, irr = sky_sources(sky_type='clear_sky')
    assert len(az) == len(el) == len(irr) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    el, az, irr = sky_sources(sky_type='clear_sky', irradiance=None)
    assert irr.max() > 60


def test_sun_source():
    el, az, irr = sun_sources()
    assert len(az) == len(el) == len(irr)
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    el, az, irr = sun_sources(irradiance=None)
    assert irr.max() > 800


def test_sun_sky_sources():
    sun, sky = sun_sky_sources(model='blended')
    sun, sky = sun_sky_sources(model='sun_soc')
    sun, sky = sun_sky_sources(model='blended', normalisation=1)
    numpy.testing.assert_almost_equal(sun[2].sum() + sky[2].sum(), 1)
    assert sun[2].sum() > 0.75
    sun, sky = sun_sky_sources(model='blended', normalisation=1, attenuation=0.2)
    assert sky[2].sum() > 0.99


def test_twilight():
    sun, sky = sun_sky_sources(ghi=1.0, dates=pandas.Timestamp('2017-08-17 19:00:00+0400', tz='Indian/Reunion'), latitude=-21.32,
                    longitude=55.5, timezone='Indian/Reunion')
    el, az, irr = sun
    assert len(irr) == 0
    el, az, irr = sky
    numpy.testing.assert_almost_equal(1, irr.sum())

