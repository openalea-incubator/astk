import numpy
import pandas

from openalea.astk.sky_sources import (
    sky_discretisation, 
    sky_radiance_distribution, 
    sky_sources, 
    sun_sources, 
    sun_sky_sources)


def test_sky_discretisation():
    elevation, azimuth, frac = sky_discretisation()
    assert len(elevation) == len(azimuth) == len(frac) == 46
    numpy.testing.assert_almost_equal(numpy.sum(frac), 1)
    elevation, azimuth, frac = sky_discretisation(1)
    assert len(elevation) == len(azimuth) == len(frac) == 1
    numpy.testing.assert_almost_equal(numpy.sum(frac), 1)
    elevation, azimuth, frac = sky_discretisation(2)
    assert len(elevation) == len(azimuth) == len(frac) == 6
    numpy.testing.assert_almost_equal(numpy.sum(frac), 1)
    elevation, azimuth, frac = sky_discretisation(6)
    assert len(elevation) == len(azimuth) == len(frac) == 6
    elevation, azimuth, frac = sky_discretisation(16)
    assert len(elevation) == len(azimuth) == len(frac) == 16
    numpy.testing.assert_almost_equal(numpy.sum(frac), 1)
    elevation, azimuth, frac = sky_discretisation(100)
    assert len(elevation) == len(azimuth) == len(frac) == 46

def test_sky_radiance_distribution():
    elevation, azimuth, strd = sky_discretisation()
    fraction = numpy.array(strd) / sum(strd)

    d = sky_radiance_distribution(elevation, azimuth,
                                  sky_type='soc')
    assert len(d) == len(elevation)
    numpy.testing.assert_almost_equal(d.sum(), 1, decimal=2)



def test_sky_sources():
    el, az, irr = sky_sources(sky_type='soc')
    assert len(az) == len(el) == len(irr) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    el, az, irr = sky_sources(sky_type='clear_sky')
    assert len(az) == len(el) == len(irr) == 46
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    el, az, irr = sky_sources(sky_type='clear_sky', irradiance=None)
    assert irr.max() > 40


def test_sun_source():
    el, az, irr = sun_sources()
    assert len(az) == len(el) == len(irr)
    numpy.testing.assert_almost_equal(numpy.sum(irr), 1)

    el, az, irr = sun_sources(irradiance=None)
    assert irr.max() > 800


def test_sun_sky_sources():
    _, sun, sky = sun_sky_sources(model='sun_soc')
    _, sun, sky = sun_sky_sources(model='blended')
    numpy.testing.assert_almost_equal(sun[2].sum() + sky[2].sum(), 1, decimal=2)
    assert sun[2].sum() > 0.75
    _, sun, sky = sun_sky_sources(model='blended', attenuation=0.2)
    assert sky[2].sum() > 0.99


def test_twilight():
    _, sun, sky = sun_sky_sources(ghi=1.0, dates=pandas.Timestamp('2017-08-17 19:00:00+0400', tz='Indian/Reunion'), latitude=-21.32,
                    longitude=55.5, timezone='Indian/Reunion')
    el, az, irr = sun
    assert len(irr) == 0
    el, az, irr = sky
    numpy.testing.assert_almost_equal(1, irr.sum())

