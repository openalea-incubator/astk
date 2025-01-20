import numpy

from openalea.astk.meteorology.sun_position import (
    sun_position, 
    sun_extraradiation)
from openalea.astk.meteorology.sun_position_astk import (
    sun_position as sun_position_astk, 
    sun_extraradiation as sun_extraradiation_astk)



def test_sun_position():
    sun = sun_position()
    assert len(sun) == 15


def test_alternative_sun_position():
    sun = sun_position()
    suna = sun_position_astk()
    # astk is equivalent <5 %
    numpy.testing.assert_allclose(suna, sun, rtol=0.05)


def test_extra_radiation():
    df = sun_extraradiation()
    dfa = sun_extraradiation_astk()
    numpy.testing.assert_allclose(dfa, df, rtol=0.01)