from openalea.plantgl import all as pgl


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
    for vid,shape in scene_geometry.iteritems():
        shape.apply(tesselator)
        mesh = tesselator.triangulation
        itri = range(mesh.indexListSize())
        pts = mesh.pointList
        S = [_surf(mesh.indexAt(i),pts) for i in itri]
        norm = [_normal(mesh.indexAt(i),pts) for i in itri]
        areas.update({vid:S})
        normals.update({vid:norm})
    return areas, normals

