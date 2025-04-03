
import warnings
from openalea.astk.colormap import jet_colors

display_enable = True
try:
    import openalea.plantgl.all as pgl
except ImportError:
    warnings.warn('PlantGL not installed: display is not enable!')
    display_enable = False

def sky_dome(turtle_mesh, sky_sources):
    vertices, faces = turtle_mesh
    colors = jet_colors((lum for _,_,lum in sky_sources))
    scene = pgl.Scene()
    for i, face in enumerate(faces):
        vtx = [vertices[v] for v in face]
        idx = range(len(face))
        mat = pgl.Material(pgl.Color3(*colors[i]))
        shape = pgl.Shape(pgl.FaceSet(pointList=vtx, indexList=[idx]), mat)
        scene += shape
    return scene


def display(vertices, faces, colors=None, view=True):
    """3D display of a polyhedron with PlantGL

    Args:
        vertices (list of tuples): list of 3D coordinates of polyhedron vertices
        faces (list of tuple): list of vertex indices defining the faces
        color: a list of (r,g,b) tuple defining color.
        If None (default), default PlantGL material is used.
        view (bool): should the shape be displayed ?

    Returns:
        a pgl shape
    """
    global display_enable
    if display_enable:
        scene = pgl.Scene()
        if colors is None:
            shape = pgl.Shape(pgl.FaceSet(pointList=vertices, indexList=faces))
            scene += shape
        else:
            for i,face in enumerate(faces):
                vtx = [vertices[v] for v in face]
                idx = range(len(face))
                mat = pgl.Material(pgl.Color3(*colors[i]))
                shape = pgl.Shape(pgl.FaceSet(pointList=vtx, indexList=[idx]), mat)
                scene += shape
        if view:
            pgl.Viewer.display(scene)
    else:
        warnings.warn('PlantGL not installed: display is not enable!')
        shape = None
    return scene
