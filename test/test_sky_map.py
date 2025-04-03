import numpy
from openalea.astk.sky_map import (sky_grid, cell_boundaries, scale_sky,
                                   sky_map, sky_hi, sky_ni, uniform_sky,
                                   surfacic_irradiance)
from openalea.astk.sky_sources import regular_sky, sky_turtle


def test_sky_grid():
    az_c, z_c, sr_c = sky_grid()
    assert az_c.shape == z_c.shape == sr_c.shape == (90, 360)
    numpy.testing.assert_almost_equal(sr_c.sum(), 2 * numpy.pi, decimal=2)

    az_c, z_c, sr_c = sky_grid(10, 10)
    assert az_c.shape == z_c.shape == sr_c.shape == (9, 36)
    numpy.testing.assert_almost_equal(sr_c.sum(), 2 * numpy.pi, decimal=2)

    az_c, z_c, sr_c = sky_grid(n_az=10, n_z=5)
    assert az_c.shape == z_c.shape == sr_c.shape == (5, 10)
    numpy.testing.assert_almost_equal(sr_c.sum(), 2 * numpy.pi, decimal=2)


def test_cell_boundaries():
    grid = sky_grid()
    az, z = cell_boundaries(grid)
    assert len(az) == 361
    assert len(z) == 91
    assert min(z) == 0
    assert max(z) == 90
    assert min(az) == 0
    assert max(az) == 360


def test_sky_irradiance():
    grid, lum = uniform_sky()
    hi = sky_hi(grid, lum)
    ni = sky_ni(grid, lum)
    numpy.testing.assert_almost_equal(ni.sum(), 2 * numpy.pi, decimal=2)
    numpy.testing.assert_almost_equal(hi.sum(), numpy.pi, decimal=2)


def test_scale_sky():
    grid, lum = uniform_sky()
    scaled = scale_sky(grid, lum)
    hi = sky_hi(grid, scaled)
    ni = sky_ni(grid, scaled)
    numpy.testing.assert_almost_equal(ni.sum(), 2, decimal=2)
    numpy.testing.assert_almost_equal(hi.sum(), 1, decimal=2)


def test_sky_map():
    grid, lum = uniform_sky()
    hi_ref = sky_hi(grid, lum).sum()
    ni_ref = sky_ni(grid, lum).sum()
    #
    dirs = regular_sky(90, 30)
    # without rescale
    lum_agg, grid_agg, new_lum = sky_map(grid, lum, dirs)
    hi_agg = sky_hi(grid_agg, lum_agg)
    ni_agg = sky_ni(grid_agg, lum_agg)
    hi_newlum = sky_hi(grid, new_lum)
    ni_newlum = sky_ni(grid, new_lum)
    assert (lum_agg == 1).all()
    assert (new_lum == 1).all()
    # ni is conserved...
    numpy.testing.assert_almost_equal(ni_agg.sum(), ni_ref, decimal=2)
    # ...hi isn't
    numpy.testing.assert_almost_equal(hi_agg.sum() / hi_ref, 1.15, decimal=1)
    numpy.testing.assert_almost_equal(ni_newlum.sum(), ni_ref, decimal=2)
    numpy.testing.assert_almost_equal(hi_newlum.sum(), hi_ref, decimal=2)
    # alternative solution with rescale
    lum_agg, grid_agg, new_lum = sky_map(grid, lum, dirs, rescale=True)
    hi_agg = sky_hi(grid_agg, lum_agg)
    # luminance is not conserved : has been rescaled to accomodate hi conservation
    assert (lum_agg != 1).all()
    assert (new_lum != 1).all()
    numpy.testing.assert_almost_equal(hi_agg.sum(), hi_ref, decimal=2)
    #
    # Test extreme case with one light source
    dirs = sky_turtle(1)
    lum_agg, grid_agg, new_lum = sky_map(grid, lum, dirs)
    hi_agg = sky_hi(grid_agg, lum_agg)
    ni_agg = sky_ni(grid_agg, lum_agg)
    hi_newlum = sky_hi(grid, new_lum)
    ni_newlum = sky_ni(grid, new_lum)
    assert (lum_agg == 1).all()
    assert (new_lum == 1).all()
    # ni is conserved...
    numpy.testing.assert_almost_equal(ni_agg.sum(), ni_ref, decimal=2)
    # ...hi isn't
    numpy.testing.assert_almost_equal(hi_agg.sum() / hi_ref, 2, decimal=1)
    numpy.testing.assert_almost_equal(ni_newlum.sum(), ni_ref, decimal=2)
    numpy.testing.assert_almost_equal(hi_newlum.sum(), hi_ref, decimal=2)


def test_surfacic_irradiance():
    grid, lum = uniform_sky()
    hi_ref = sky_hi(grid, lum).sum()
    his = surfacic_irradiance(grid, lum)
    numpy.testing.assert_almost_equal(his, hi_ref, decimal=2)
    # test surfacic irradiance is insensitive to surface orientation in uniform sky condition
    his = surfacic_irradiance(grid, lum, 45)
    numpy.testing.assert_almost_equal(his, hi_ref, decimal=2)
    his = surfacic_irradiance(grid, lum, 90)
    numpy.testing.assert_almost_equal(his, hi_ref, decimal=2)
