""" Interfaces for PlantGL scene / PlantGL display"""

import numpy

pgl_imported = False
try:
    import openalea.plantgl.all as pgl
    pgl_imported = True
except ImportError:
    pgl = None


def bbox(pgl_scene, scene_unit='m'):
    """ Bounding box of a pgl scene"""
    tesselator = pgl.Tesselator()
    bbc = pgl.BBoxComputer(tesselator)
    bbc.process(pgl_scene)
    box = bbc.result
    xmin, ymin, zmin = box.getXMin(), box.getYMin(), box.getZMin()
    xmax, ymax, zmax = box.getXMax(), box.getYMax(), box.getZMax()
    if scene_unit != 'm':
        units = {'mm': 0.001, 'cm': 0.01, 'dm': 0.1, 'm': 1, 'dam': 10,
                 'hm': 100,
                 'km': 1000}
        convert = units.get(scene_unit, 1)
        xmin, ymin, zmin = numpy.array((xmin, ymin, zmin)) * convert
        xmax, ymax, zmax = numpy.array((xmax, ymax, zmax)) * convert

    return (xmin, ymin, zmin), (xmax, ymax, zmax)


def shape_mesh(pgl_shape, tesselator=None):
    if tesselator is None:
        tesselator = pgl.Tesselator()
    tesselator.process(pgl_shape)
    tset = tesselator.result
    return numpy.array(tset.pointList), numpy.array(tset.indexList)


def as_scene_mesh(pgl_scene):
    """ Transform a PlantGL scene / PlantGL shape dict to a scene_mesh"""
    tesselator = pgl.Tesselator()

    if isinstance(pgl_scene, pgl.Scene):
        sm = {}

        def _concat_mesh(mesh1,mesh2):
            v1, f1 = mesh1
            v2, f2 = mesh2
            v = numpy.array(v1.tolist() + v2.tolist())
            offset = len(v1)
            f = numpy.array(f1.tolist() + [[i + offset, j + offset, k + offset] for i, j, k
                               in f2.tolist()])
            return v, f

        for pid, pgl_objects in pgl_scene.todict().iteritems():
            sm[pid] = reduce(_concat_mesh, [shape_mesh(pgl_object, tesselator) for pgl_object in
                           pgl_objects])
        return sm
    elif isinstance(pgl_scene, dict):
        return {sh_id: shape_mesh(sh,tesselator) for sh_id, sh in
                pgl_scene.iteritems()}
    else:
        return pgl_scene


def from_scene_mesh(scene_mesh, colors=None):
    plant_color = (0, 180, 0)

    if colors is None:
        colors = {k: plant_color for k in scene_mesh}

    scene = pgl.Scene()
    for sh_id, mesh in scene_mesh.iteritems():
        vertices, faces = mesh
        if isinstance(colors[sh_id], tuple):
            r, g, b = colors[sh_id]
            color_list = [pgl.Color4(r, g, b, 0)] * len(faces)
        else:
            color_list = [pgl.Color4(r, g, b, 0) for r, g, b in colors[sh_id]]
        shape = pgl.TriangleSet(vertices, faces)
        shape.colorList = color_list
        shape.colorPerVertex = False
        shape.id = sh_id
        scene += shape

    return scene


def display(scene):
    """ display a scene"""
    pgl.Viewer.display(scene)
    return scene


def unit_sphere_scene():
    return pgl.Scene([pgl.Sphere()])


def is_pgl_scene(scene):
    if not pgl_imported:
        return False
    else:
        return isinstance(scene, pgl.Scene)