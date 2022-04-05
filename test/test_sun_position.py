import numpy

from alinea.astk.meteorology.sun_position import (
    sun_position, 
    sun_extraradiation)
from alinea.astk.meteorology.sun_position_astk import (
    sun_position as sun_position_astk, 
    sun_extraradiation as sun_extraradiation_astk)
from alinea.astk.meteorology.sun_position_ephem import (
    sun_position as sun_position_ephem)


def test_sun_position():
    sun = sun_position()
    assert len(sun) == 15


def test_alternative_sun_position():
    sun = sun_position()
    sune = sun_position_ephem()
    suna = sun_position_astk()
    # ephem is equivalent < 1%
    numpy.testing.assert_allclose(sune, sun, rtol=0.01)
    # astk is equivalent <5 %
    numpy.testing.assert_allclose(suna, sun, rtol=0.05)


def test_extra_radiation():
    df = sun_extraradiation()
    dfa = sun_extraradiation_astk()
    numpy.testing.assert_allclose(dfa, df, rtol=0.01)