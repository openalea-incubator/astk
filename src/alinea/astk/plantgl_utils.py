from openalea.plantgl import all as pgl

def _is_iterable(x):
    try:
        x = iter(x)
    except TypeError: 
        return False
    return True


def get_area_and_normal(scene_geometry):

    def _surf(ind,pts):
        A,B,C = [pts[i] for i in ind]
        return pgl.norm(pgl.cross(B-A, C-A)) / 2.0

    def _normal(ind,pts):
        A,B,C = [pts[i] for i in ind]
        n = pgl.cross(B-A, C-A)
        return n.normed()

    tesselator = pgl.Tesselator()
    areas={}
    normals={}
    for vid,shapes in scene_geometry.iteritems():
        S = []
        norm = []
        if not _is_iterable(shapes):
            shapes = [shapes]
        for shape in shapes:
            shape.apply(tesselator)
            mesh = tesselator.triangulation
            itri = range(mesh.indexListSize())
            pts = mesh.pointList
            S +=[_surf(mesh.indexAt(i),pts) for i in itri]
            norm += [_normal(mesh.indexAt(i),pts) for i in itri]
        areas.update({vid:S})
        normals.update({vid:norm})
    return areas, normals

def get_height(scene_geometry):
    """ Calculate the height of objects in the scene
    
    Find the coordinates of the points that compose the object and 
    compute the mean of the height coordinates, for each object
    in the scene.
    
    Parameters
    ----------
    scene_geometry: dict([id, geometry])
        Dictionnary of geometries of objects in the scene.
    """
    heights = {}
    tesselator = pgl.Tesselator()
    for vid,shapes in scene_geometry.iteritems():
        S = []
        H = []
        if not _is_iterable(shapes):
            shapes = [shapes]
        for shape in shapes:
            shape.apply(tesselator)
            mesh = tesselator.triangulation
            itri = range(mesh.indexListSize())
            H += [mesh.faceCenter(i)[2] for i in itri]
        heights.update({vid:H})
    return heights
        