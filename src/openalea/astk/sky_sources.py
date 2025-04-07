# -*- python -*-
#
#       Copyright 2016-2025 Inria - CIRAD - INRAe
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       WebSite : https://github.com/openalea-incubator/astk
#
#       File author(s): Christian Fournier <christian.fournier@inrae.fr>
#
# ==============================================================================
""" A collection of equation for modelling sun position, sun irradiance and sky
irradiance
"""
import numpy

from .icosphere import turtle_mesh, spherical_face_centers
from openalea.astk.sky_luminance import sky_luminance
from .sky_map import sky_grid, sky_map, sky_hi, sky_ni, sun_hi


def regular_sky(d_az=10, d_z=10, n_az=None, n_z=None):
    az, z, _ = sky_grid(d_az=d_az, d_z=d_z, n_az=n_az, n_z=n_z)
    return [*zip(90 - z.flatten(), az.flatten())]


def hierarchical_turtle(sectors=46):
    # Hierarchical direction from turtle.xls file of J Dauzat
    elevations_h = [90.] + [26.57] * 5 + [52.62] * 5 + [10.81] * 5 + [69.16] * 5 + [
        47.41] * 5 + [31.08] * 10 + [9.23] * 10
    az1 = [0, 72, 144, 216, 288]
    az2 = [36, 108, 180, 252, 324]
    azimuths_h = [180.] + az1 + az2 * 2 + az1 * 2 + [
        23.27, 48.73, 95.27, 120.73, 167.27, 192.73, 239.27, 264.73, 311.27, 336.73] + [
        12.23, 59.77, 84.23, 131.77, 156.23, 203.77, 228.23, 275.77, 300.23, 347.77]
    nb_sect = [1, 6, 16, 46][numpy.searchsorted([1, 6, 16, 46], min(46, sectors))]
    return [*zip(elevations_h[:nb_sect], azimuths_h[:nb_sect])]


def icospherical_turtle(sectors=46):
    sky_mesh = turtle_mesh(sectors)
    return spherical_face_centers(sky_mesh)


def sky_turtle(sectors=46):
    if sectors <= 46:
        return hierarchical_turtle(sectors)
    else:
        return icospherical_turtle(sectors)


def sky_sources(sky_type='soc', sky_irradiance=None, sky_dirs=None, scale=None, source_irradiance='normal', north=90, sun_in_sky=False, force_hi=True):
    """ Light sources representing the sun and the sky in a scene

    Args:
        sky_type (str): sky type (see details below), one of ('soc', 'uoc', 'clear_sky', 'sun_soc', 'blended', 'all_weather').
        sky_irradiance: a datetime indexed dataframe specifying sky irradiances for the period, such as returned by
            astk.meteorology.sky_irradiance.sky_irradiance. Needed for all sky_types except 'uoc' and 'soc'
        sky_dirs (list): a [(elevation,azimuth),...] list of directions sampling the sky hemisphere. If None (default)
            a hierarchical turtle discretisation of 46 directions is used. Azimuths are relative to North, positive
            clockwise
        scale (str): How should sun/sky luminance be scaled ? If None (default) luminance are scaled so that sun+sky
            horizontal irradiance equals one. Other options are:
            - 'ghi': sun+sky horizontal flux equals mean ghi (W.m-2.s-1)
            - 'ppfd' : sun+sky horizontal flux equals mean PPFD (micromolPAR.m-2.s-1)
            - 'global': sun+sky horizontal flux equals time-integrated global irradiance (MJ.m-2)
            - 'par': sun+sky horizontal flux equals time-integrated PPFD (molPAR.m-2)
        source_irradiance (str): How should source irradiance be given ? Should one of:
            - 'normal' : irradiance are given as normal irradiances (perpendicular to source direction)
            - 'horizontal': irradiance are given as horizontal irradiances
        north: the angle between X+ and North (deg, positive counter-clockwise)
        sun_in_sky: Should the sun be added to the sky ? If True, sky luminance is set to sun luminance in the sun region,
            and sun luminance list is emptied. Ignored for sky types 'uoc' and 'soc'.
        force_hi: if True (default), sky sources are rescaled to ensure that global horizontal irradiance of discretised
            sources is the same as the original sky luminance distrisbution. If False , no rescaling append, ensuring that global direct irradiance of sky is preserved

    Returns:
        sun, sky tuple
        sun and sky are lists of (elevation (degrees), azimuth (degrees, from X+ positive counter-clockwise),
        luminance) tuples of sources representing the sun or the sky

    Details:
        sky_type refer to different sky models:
            - 'clear_sky', 'uoc' and 'soc' are CIE sky types defined in [1]. For all these types, only relative sky luminance
                are returned (sun source list is empty), and total sky horizontal irradiance equals one.
            - 'sun_soc' refers to the approach defined in [2] where direct normal irradiance comes from the sun, and
                 diffuse horizontal irradiance comes from an CIE soc sky luminance distribution
            - 'blended' refers to the sky blending approach defined in [3], where direct normal irradiance comes from
                the sun, and diffuse horizontal irradiance comes from a blending of CIE clear-sky and CIE soc sky luminance
                distribution, that depends on sky clearness index
            - 'all_weather' refers to the approach defined in [4], where direct normal irradiance comes from
                the sun, and diffuse horizontal irradiance comes from a luminance distribution that depends on sky
                clearness and sky brightness


        [1] CIE, 2002, Spatial distribution of daylight CIE standard general sky,
            CIE standard, CIE Central Bureau, Vienna
        [2] Sinoquet H. & Bonhomme R. (1992) Modeling radiative transfer in mixed and row intercropping
            systems. Agricultural and Forest Meteorology 62, 219–240
        [3] J. Mardaljevic. Daylight Simulation: Validation, Sky Models and Daylight Coefficients. PhD thesis, De Montfort University,
            Leicester, UK, 2000. p193,eq. 5-10
        [4] R. Perez, R. Seals, J. Michalsky, "All-weather model for sky luminance distribution—Preliminary configuration and
            validation", Solar Energy, Volume 50, Issue 3, 1993, Pages 235-245
  """
    def _normalise_angle(angle, north):
        """normalise an angle to the [0, 360] range"""
        angle = numpy.array(angle, dtype=float)
        angle = north - angle
        modulo = 360
        angle %= modulo
        # force to [0, modulo] range
        angle = (angle + modulo) % modulo
        return angle

    grid = sky_grid()
    sun, sky = sky_luminance(grid, sky_type=sky_type, sky_irradiance=sky_irradiance, scale=scale, sun_in_sky=sun_in_sky)
    if sky_dirs is None:
        sky_dirs = sky_turtle()

    sky_agg, grid_agg, _ = sky_map(grid, sky, sky_dirs, force_hi=force_hi)
    if source_irradiance == 'horizontal':
        sky_irr = sky_hi(grid_agg, sky_agg)
    elif source_irradiance == 'normal':
        sky_irr = sky_ni(grid_agg, sky_agg)
    else:
        raise ValueError('Unvalid option for source_irradiance: ' + source_irradiance)
    sky_elevation, sky_azimuth = zip(*sky_dirs)
    sky_azimuth = _normalise_angle(sky_azimuth, north)
    sky_sources = list(zip(sky_elevation, sky_azimuth, sky_irr))

    if len(sun) > 0:
        sun_elevation, sun_azimuth, sun_irr = zip(*sun)
        if source_irradiance == 'horizontal':
            sun_irr = sun_hi(sun)
        sun_azimuth = _normalise_angle(sun_azimuth, north)
        sun_sources = list(zip(sun_elevation, sun_azimuth, sun_irr))
    else:
        sun_sources = sun

    return sun_sources, sky_sources


def caribu_light_sources(sun, sky):
    def _vecteur_direction(elevation, azimuth):
        """ coordinate of look_at source vector from elevation and azimuth (deg, f
        rom X+ positive counter-clockwise)"""
        theta = numpy.radians(90 - numpy.array(elevation))
        phi = numpy.radians(azimuth)
        return -numpy.sin(theta) * numpy.cos(phi), -numpy.sin(theta) * numpy.sin(phi), -numpy.cos(theta)

    el, az, irrad = zip(*(sun + sky))
    x, y, z = _vecteur_direction(el, az)
    return [(irr, (xx, yy, zz)) for irr, xx, yy, zz in
            zip(irrad, x, y, z)]