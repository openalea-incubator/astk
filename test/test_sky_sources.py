import numpy

from openalea.astk.sky_irradiance import sky_irradiance
from openalea.astk.sky_sources import (
    regular_sky,
    sky_turtle,
    sky_sources,
    source_ni)


def test_sky_turtle():
    sky_dirs = sky_turtle()
    assert len(sky_dirs) == 46
    sky_dirs = sky_turtle(1)
    assert len(sky_dirs) == 1
    sky_dirs = sky_turtle(2)
    assert len(sky_dirs) == 6
    sky_dirs = sky_turtle(6)
    assert len(sky_dirs) == 6
    sky_dirs = sky_turtle(16)
    assert len(sky_dirs) == 16
    sky_dirs = sky_turtle(100)
    assert len(sky_dirs) == 136
    sky_dirs = sky_turtle(500)
    assert len(sky_dirs) == 556
    sky_dirs = sky_turtle(1000)
    assert len(sky_dirs) == 976


def test_regular_sky():
    sky_dirs = regular_sky()
    assert len(sky_dirs) == 9 * 36
    sky_dirs = regular_sky(5,5)
    assert len(sky_dirs) == 18 * 72
    sky_dirs = regular_sky(n_az=5, n_z=5)
    assert len(sky_dirs) == 25


def test_sky_sources():
    sky_irr = sky_irradiance()

    sun, sky = sky_sources('soc')
    assert len(sun) == 0
    assert len(sky) == 46
    el, az, irr = map(numpy.array, zip(*sky))
    lum = source_ni(sky)
    north = numpy.where(az <= 180)
    south = numpy.where(az > 180)
    numpy.testing.assert_almost_equal(lum[north].sum(),
                                      lum[south].sum(),
                                      decimal=1)

    sun, sky = sky_sources('sun_soc', sky_irradiance=sky_irr)
    assert len(sun) == 14
    assert len(sky) == 46
    el, az, irr = map(numpy.array, zip(*sky))
    lum = source_ni(sky)
    north = numpy.where(az <= 180)
    south = numpy.where(az > 180)
    numpy.testing.assert_almost_equal(lum[north].sum(),
                                      lum[south].sum(),
                                      decimal=1)

    sun, sky = sky_sources('sun_soc', sky_irradiance=sky_irr, sun_in_sky=True)
    assert len(sun) == 0
    assert len(sky) == 46
    el, az, irr = map(numpy.array, zip(*sky))
    lum = source_ni(sky)
    north = numpy.where(az <= 180)
    south = numpy.where(az > 180)
    numpy.testing.assert_almost_equal(lum[south].sum() - lum[north].sum(), 0.76, decimal=2)

    sun, sky = sky_sources('sun_soc', sky_irradiance=sky_irr, sun_in_sky=True, north=-90)
    el, az, irr = map(numpy.array, zip(*sky))
    lum = source_ni(sky)
    north = numpy.where(az > 180)
    south = numpy.where(az <= 180)
    numpy.testing.assert_almost_equal(lum[south].sum() - lum[north].sum(), 0.76, decimal=2)

    sun, sky = sky_sources('blended', sky_irradiance=sky_irr)
    el, az, irr = map(numpy.array, zip(*sky))
    lum = source_ni(sky)
    north = numpy.where((az <= 180) & (el > 45))
    south = numpy.where((az > 180) & (el > 45))
    delta_cs = lum[south].sum() - lum[north].sum()
    sun, sky = sky_sources('blended', sky_irradiance=sky_irradiance(attenuation=0.2))
    el, az, irr = map(numpy.array, zip(*sky))
    lum = source_ni(sky)
    north = numpy.where((az <= 180) & (el > 45))
    south = numpy.where((az > 180) & (el > 45))
    delta_soc = lum[south].sum() - lum[north].sum()
    numpy.testing.assert_almost_equal(delta_cs / delta_soc, 14.6, decimal=1)


