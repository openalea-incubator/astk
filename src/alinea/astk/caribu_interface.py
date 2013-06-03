from openalea.plantgl import all as pgl
from alinea.caribu.CaribuScene import CaribuScene
import alinea.caribu.sky_tools.turtle as turtle
from math import radians, degrees, sin , cos



def vecteur_direction(elevation,azimuth):
    theta = radians(90 - elevation)
    phi = radians(azimuth)
    return sin(theta) * cos(phi),sin(theta) * sin(phi),  -cos(theta)


def emission_inv(elevation, energy):
    """ return energy of emmision for a source of a given direction and of a given energy received on a horizontal surface """
    theta = radians(90 - elevation)
    received_energy = energy * abs(cos(theta))
    return received_energy


def geom2shape(vid, mesh):
    """ Create a shape """
    shape = pgl.Shape(mesh)
    shape.id = vid
    return shape


def run_caribu(sources, scene_geometry, output_by_triangle = False):
    c_scene = CaribuScene()
    shapes=[geom2shape(k,v) for k,v in scene_geometry.iteritems()]
    idmap = c_scene.add_Shapes(shapes)    
    c_scene.addSources(sources)
    output = c_scene.runCaribu(infinity=False)
    out_moy = c_scene.output_by_id(output, idmap)
    if output_by_triangle:
        out_tri = c_scene.output_by_id(output, idmap, aggregate = False)
        return out_moy, out_tri
    else:
        return out_moy


def turtle_interception(sectors, scene_geometry, energy, output_by_triangle = False):
    """ 
    Calls Caribu for differents energy sources

    :Parameters:
    ------------
    - `sectors` (int)
    - `scene_geometry`
    - `energy` (float)
        e.g. Meteorological mean variables at the global scale. Could be:
            - 'PAR' : Quantum PAR (ppfd) in micromol.m-2.sec-1
            - 'Pluie' : Precipitation (mm)

    :Returns:
    ---------
    - 'id_out' (dict) - Meteorological variable at the leaf scale
    """
    energie, emission, direction, elevation, azimuth = turtle.turtle(sectors=sectors, energy=energy) 
    sources = zip(energie,direction)
    if output_by_triangle:
        out_moy, out_tri = run_caribu(sources, scene_geometry, output_by_triangle = True)
        return out_moy, out_tri
    else:
        id_out = run_caribu(sources, scene_geometry)
        return id_out
