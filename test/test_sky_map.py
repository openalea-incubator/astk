import numpy
from openalea.astk.sky_map import sky_grid, sky_map
from openalea.astk.sky_sources import regular_sky, sky_turtle


def test_sky_grid():
    azimuth, zenith, az_c, z_c, w_c = sky_grid()
    assert len(azimuth) == 361
    assert len(zenith) == 91
    assert az_c.shape == z_c.shape == w_c.shape == (90, 360)
    numpy.testing.assert_almost_equal(w_c.sum(), 2 * numpy.pi, decimal=2)

    azimuth, zenith, az_c, z_c, w_c = sky_grid(10, 10)
    assert len(azimuth) == 37
    assert len(zenith) == 10
    assert az_c.shape == z_c.shape == w_c.shape == (9, 36)
    numpy.testing.assert_almost_equal(w_c.sum(), 2 * numpy.pi, decimal=2)

    azimuth, zenith, az_c, z_c, w_c = sky_grid(n_az=10, n_z=5)
    assert len(azimuth) == 11
    assert len(zenith) == 6
    assert az_c.shape == z_c.shape == w_c.shape == (5, 10)
    numpy.testing.assert_almost_equal(w_c.sum(), 2 * numpy.pi, decimal=2)


def test_sky_map():
    grid = sky_grid()
    azimuth, zenith, az_c, z_c, w_c = grid
    uniform = numpy.ones_like(az_c)
    uniform /= uniform.sum()
    dirs = regular_sky(90,30)
    slum, smap = sky_map(grid, uniform, dirs)
    dirs = sky_turtle(1)
    slum, smap = sky_map(grid, uniform, dirs)
