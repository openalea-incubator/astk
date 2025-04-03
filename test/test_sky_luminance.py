from openalea.astk.meteorology.sky_luminance import sky_luminance
from openalea.astk.meteorology.sky_irradiance import sky_irradiance
from openalea.astk.sky_map import sky_grid, sky_hi, sky_ni, sun_hi, sun_ni
import numpy


def test_soc_uoc():
    # default call is soc
    grid = sky_grid()
    sun, sky = sky_luminance(grid, sky_type='soc')
    assert sky.shape == grid[0].shape
    assert len(sun) == 0
    numpy.testing.assert_allclose(1, sky_hi(grid, sky).sum())
    numpy.testing.assert_allclose(1.666, sky_ni(grid, sky).sum(), atol=1e-3)
    # uoc
    sun, sky = sky_luminance(grid, sky_type='uoc')
    assert len(sun) == 0
    numpy.testing.assert_allclose(1, sky_hi(grid, sky).sum())

def test_clear_sky():
    grid = sky_grid()
    sky_irr = sky_irradiance()
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='clear_sky')
    assert len(sun) == 0
    numpy.testing.assert_allclose(1, sky_hi(grid, sky).sum())


def test_sun_soc():
    grid = sky_grid()
    sky_irr = sky_irradiance()
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='sun_soc')
    assert len(sun) == numpy.count_nonzero(sky_irr.dni)
    shi = sun_hi(sun).sum()
    numpy.testing.assert_allclose(1 - sky_irr.dhi.sum()/sky_irr.ghi.sum(), shi)
    numpy.testing.assert_allclose(1, shi + sky_hi(grid, sky).sum())
    #
    sky_irr = sky_irradiance(attenuation=0.2)
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='sun_soc')
    assert len(sun) == numpy.count_nonzero(sky_irr.dni)
    shi = sun_hi(sun).sum()
    numpy.testing.assert_allclose(1 - sky_irr.dhi.sum()/sky_irr.ghi.sum(), shi)
    numpy.testing.assert_allclose(1, shi + sky_hi(grid, sky).sum())


def test_blended():
    grid = sky_grid()
    sky_irr = sky_irradiance()
    _, soc = sky_luminance(grid, sky_type='soc')
    _, cs = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='clear_sky')
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='blended')
    assert len(sun) == numpy.count_nonzero(sky_irr.dni)
    shi = sun_hi(sun).sum()
    numpy.testing.assert_allclose(sky_hi(grid, cs) * (1 - shi), sky_hi(grid, sky), rtol=0.1)
    #
    sky_irr = sky_irradiance(attenuation=0.2)
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='blended')
    assert len(sun) == numpy.count_nonzero(sky_irr.dni)
    shi = sun_hi(sun).sum()
    numpy.testing.assert_allclose(sky_hi(grid, soc) * (1 - shi), sky_hi(grid, sky), rtol=0.05)


def test_all_weather():
    # All_weather may be buggy as rtol are quite high compared to CIE standards ?
    grid = sky_grid()
    sky_irr = sky_irradiance()
    _, soc = sky_luminance(grid, sky_type='soc')
    _, cs = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='clear_sky')
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='all_weather')
    assert len(sun) == numpy.count_nonzero(sky_irr.dni)
    shi = sun_hi(sun).sum()
    numpy.testing.assert_allclose(sky_hi(grid, cs) * (1 - shi), sky_hi(grid, sky), rtol=0.2)
    #
    sky_irr = sky_irradiance(attenuation=0.2)
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='all_weather')
    assert len(sun) == numpy.count_nonzero(sky_irr.dni)
    shi = sun_hi(sun).sum()
    numpy.testing.assert_allclose(sky_hi(grid, soc) * (1 - shi), sky_hi(grid, sky), rtol=0.4)


def test_sun_in_sky():
    grid = sky_grid()
    sky_irr = sky_irradiance()
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, sky_type='sun_soc', sun_in_sky=True)
    assert len(sun) == 0
    numpy.testing.assert_allclose(1, sky_hi(grid, sky).sum())
    #TODO check that removing sun yield soc and sun



def test_scaling():
    grid = sky_grid()
    sky_irr = sky_irradiance()
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, scale='ghi')
    numpy.testing.assert_allclose(sky_irr.ghi.mean(), sky_hi(grid, sky).sum())
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, scale='ppfd')
    numpy.testing.assert_allclose(sky_irr.ppfd.mean(), sky_hi(grid, sky).sum())
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, scale='global')
    numpy.testing.assert_allclose(sky_irr.ghi.sum() * 3600 / 1e6, sky_hi(grid, sky).sum())
    sun, sky = sky_luminance(grid, sky_irradiance=sky_irr, scale='par')
    numpy.testing.assert_allclose(sky_irr.ppfd.sum() * 3600 / 1e6, sky_hi(grid, sky).sum())
    #
    sun, sky = sky_luminance(grid, sky_type='sun_soc', sky_irradiance=sky_irr, scale='ghi')
    numpy.testing.assert_allclose(sky_irr.ghi.mean(), sun_hi(sun).sum() + sky_hi(grid, sky).sum())
