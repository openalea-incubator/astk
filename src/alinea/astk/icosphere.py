# -*- python -*-
#
#       Copyright 2016 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       WebSite : https://github.com/openalea-incubator/astk
#
#       File author(s): Christian Fournier <Christian.Fournier@supagro.inra.fr>
#
#       Credits:
#       Starting point for developing this module the C code found here:
#   http://blog.andreaskahler.com/2009/06/creating-icosphere-mesh-in-code.html.
#
# ==============================================================================
"""
Generation of regular spherical polyhedrons: icospheres and their
hexagonal/pentagonal duals.
"""

import math
import numpy
import warnings

display_enable = True
try:
    import openalea.plantgl.all as pgl
except ImportError:
    warnings.warn('PlantGL not installed: display is not enable!')
    display_enable = False


def display(vertices, faces, color=None, view=True):
    """3D display of a polyhedron with PlantGL

    Args:
        vertices (list of tuples): list of 3D coordinates of polyhedron vertices
        faces (list of tuple): list of vertex indices defining the faces
        color: a (r,g,b) tuple defining color.
        If None (default), default PlantGL material is used.
        view (bool): should the shape be displayed ?

    Returns:
        a pgl shape
    """
    global display_enable
    if display_enable:
        if color is None:
            shape = pgl.Shape(pgl.FaceSet(pointList=vertices, indexList=faces))
        else:
            m = pgl.Material(pgl.Color3(*color))
            shape = pgl.Shape(pgl.FaceSet(pointList=vertices, indexList=faces),
                              m)
        if view:
            pgl.Viewer.display(shape)
    else:
        warnings.warn('PlantGL not installed: display is not enable!')
        shape = None
    return shape


def normed(point):
    """ normalised coordinates of (0,point) vector
    """
    x, y, z = point
    radius = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    return x / radius, y / radius, z / radius


def norm(vector):
    """ norm of a vector
    """
    x, y, z = vector
    return math.sqrt(x ** 2 + y ** 2 + z ** 2)


def spherical(points):
    """ zenital and azimutal coordinate of a list of points"""
    x, y, z = zip(*points)
    return numpy.arccos(z), numpy.arctan2(y, x)


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = numpy.asarray(axis)
    axis = axis / norm(axis)
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return numpy.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def rotate(points, rotation_matrix):
    return [numpy.dot(rotation_matrix, p) for p in points]


def inverse_rotation(points, theta, phi):
    """rotate points -phi around z, then -theta around y"""

    rotz = rotation_matrix([0, 0, 1], -phi)
    roty = rotation_matrix([0, 1, 0], - theta)
    return rotate(rotate(points, rotz), roty)


def middle_point(p1, p2):
    """ coordinates of the middle point between p1 and p2
    """
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return (x1 + x2) / 2., (y1 + y2) / 2., (z1 + z2) / 2.,


def centroid(points):
    x, y, z = zip(*points)
    return numpy.mean(x), numpy.mean(y), numpy.mean(z)



def icosahedron():
    """ Creates the vertices and faces of an icosahedron inscribed in the
    unit_sphere and with one vertex aligned on Z+ axis

    Returns:
        a list of vertices and a list of faces
    """

    t = (1.0 + math.sqrt(5.0)) / 2.0

    vertices = []
    vertices.append(normed((-1, t, 0)))
    vertices.append(normed((1, t, 0)))
    vertices.append(normed((-1, -t, 0)))
    vertices.append(normed((1, -t, 0)))

    vertices.append(normed((0, -1, t)))
    vertices.append(normed((0, 1, t)))
    vertices.append(normed((0, -1, -t)))
    vertices.append(normed((0, 1, -t)))

    vertices.append(normed((t, 0, -1)))
    vertices.append(normed((t, 0, 1)))
    vertices.append(normed((-t, 0, -1)))
    vertices.append(normed((-t, 0, 1)))

    # align to get second point on Z+
    theta, phi = zip(*spherical(vertices))[1]
    vertices = inverse_rotation(vertices, theta, phi)

    # create 20 triangles of the icosahedron
    faces = []

    # 5 faces around point 0
    faces.append((0, 11, 5))
    faces.append((0, 5, 1))
    faces.append((0, 1, 7))
    faces.append((0, 7, 10))
    faces.append((0, 10, 11))

    # 5 adjacent faces
    faces.append((1, 5, 9))
    faces.append((5, 11, 4))
    faces.append((11, 10, 2))
    faces.append((10, 7, 6))
    faces.append((7, 1, 8))

    # 5 faces around point 3
    faces.append((3, 9, 4))
    faces.append((3, 4, 2))
    faces.append((3, 2, 6))
    faces.append((3, 6, 8))
    faces.append((3, 8, 9))

    # 5 adjacent faces
    faces.append((4, 9, 5))
    faces.append((2, 4, 11))
    faces.append((6, 2, 10))
    faces.append((8, 6, 7))
    faces.append((9, 8, 1))

    return vertices, faces


def split_triangles(vertices, faces, tags=None):
    """ Iterate an icosphere by sub-dividing each triangle into 4.

    Args:
        vertices (list of tuples): list of 3D coordinates of icosphere vertices
        faces (list of tuple): list of vertex indices defining the faces
        tags (list of int): list of integer identifying a face. if None (default)
        no tags are returned
    Returns:
        a list of vertices and a list of faces and, if tags is not None, a list
        of tags referencing the tag of the parent face

    This is a python implementation of the C code found here:
    http://blog.andreaskahler.com/2009/06/creating-icosphere-mesh-in-code.html
"""
    # cache is a (index_p1, index_p2): middle_point_index dict refering
    # to vertices
    cache = {}
    for i in range(len(faces)):
        face = faces.pop(0)
        v1, v2, v3 = face
        p1 = vertices[v1]
        p2 = vertices[v2]
        p3 = vertices[v3]
        ka = tuple(sorted((v1, v2)))
        kb = tuple(sorted((v2, v3)))
        kc = tuple(sorted((v1, v3)))
        if ka in cache:
            va = cache[ka]
        else:
            vertices.append(normed(middle_point(p1, p2)))
            va = len(vertices) - 1
            cache.update({ka: va})
        if kb in cache:
            vb = cache[kb]
        else:
            vertices.append(normed(middle_point(p2, p3)))
            vb = len(vertices) - 1
            cache.update({kb: vb})
        if kc in cache:
            vc = cache[kc]
        else:
            vertices.append(normed(middle_point(p1, p3)))
            vc = len(vertices) - 1
            cache.update({kc: vc})

        faces.append((v1, va, vc))
        faces.append((v2, vb, va))
        faces.append((v3, vc, vb))
        faces.append((va, vb, vc))

        if tags is not None:
            tag = tags.pop(0)
            tags.extend([tag] * 4)

    if tags is None:
        return vertices, faces
    else:
        return vertices, faces, tags


def sorted_faces(center, face_indices, faces):
    """ return face indices sorted to form a counter clockwise rotation
     around its centroid"""
    indices = [i for i in face_indices]
    sorted_indices = [indices.pop(0)]
    while len(indices) > 0:
        last = faces[sorted_indices[-1]]
        next_pt = last[((numpy.where(numpy.array(last) == center)[0] + 2) % 3)[0]]
        next_index = [i for i, f in enumerate(indices) if next_pt in faces[f]][0]
        sorted_indices.append(indices.pop(next_index))
    return sorted_indices


def dual(vertices, faces):
    """Generate the dual polyhedron associated to an icosphere.

    Args:
        vertices (list of tuples): list of 3D coordinates of icosphere vertices
        faces (list of tuple): list of vertex indices defining the faces
    Returns:
        a list of vertices and a list of faces
    """

    # centers = []
    dual_vertices = []
    dual_faces = []
    cache = {}
    for icenter, center in enumerate(vertices):
        new_face = []
        # centers.append(center)
        ifaces = [i for i, f in enumerate(faces) if icenter in f]
        for iface in sorted_faces(icenter, ifaces, faces):
            if iface in cache:
                new_face.append(cache[iface])
            else:
                cache[iface] = len(dual_vertices)
                new_face.append(len(dual_vertices))
                points = [vertices[i] for i in faces[iface]]
                dual_vertices.append(normed(centroid(points)))
        dual_faces.append(new_face)

    return dual_vertices, dual_faces


def star_split(vertices, faces, tags=None):
    """ star-split the faces of a polyhedron

    Args:
        vertices (list of tuples): list of 3D coordinates of polyhedron vertices
        faces (list of tuple): list of vertex indices defining the faces
        tags (list of int): list of integer identifying a face. if None (default)
        no tags are returned
    Returns:
        a list of vertices and a list of faces and, if tags is not None, a list
        of tags referencing the tag of the parent face
    """

    for i in range(len(faces)):
        face = faces.pop(0)
        center = normed(centroid([vertices[p] for p in face]))
        icenter = len(vertices)
        vertices.append(center)
        for j in range(len(face) - 1):
            faces.append((face[j], face[j + 1], icenter))
        faces.append((face[-1], face[0], icenter))
        if tags is not None:
            tag = tags.pop(0)
            tags.extend([tag] * len(face))
    if tags is None:
        return vertices, faces
    else:
        return vertices, faces, tags


def icosphere(iter_triangle=0, iter_star=0):
    """Generate an icosphere from a icosahedron by iterating n times the
    triangle-split of its faces and m time the star-split of the faces of
    its dual.

    Args:
        iter_triangle (int): the number of iteration of the triangle split
        iter_star (int): the number of iteration of the star-split

    Returns:
        a list of vertices and a list of faces
    """

    vertices, faces = icosahedron()
    for i in range(iter_star):
        vertices, faces = star_split(*dual(vertices, faces))
    for i in range(iter_triangle):
        vertices, faces = split_triangles(vertices, faces)

    return vertices, faces


def refine(level=0):
    """Compute the number of triangle- and star- iterations needed to achieve an
     icosphere with a given level of refinement among the polyhedron family
     these two algorithm can produce.

     Args:
         level (int): the level of refinement
     """
    # Let imagine a matrix of icopsphere with row index the number of star split
    #  and column index the number the number of triangle splits
    # the refinement level (number of faces) of the i,j icosphere is increasing
    # with the index of a 'triangular' traversal of this matrix
    # (0,0 = 0, 1,0 = 1, 0,1 = 2, 2,0 = 3, 1,1 = 4, 0,2 = 5, ...

    # k is the smallest integer that ensure refinement index to be in a (K + 1,
    #  K + 1) icosphere matrix
    # tips : at the (0,K) position, there has been 1 + 2 + 3 +... + K
    # refinements along the triangular traversal, ie K (K + 1) / 2
    # refinements
    k = math.floor((math.sqrt(8 * level + 1) - 1) / 2.)
    n = k + 1
    r_index = n * (n + 1) / 2. - (level + 1)

    iter_triangle = int(k - r_index)
    iter_star = int(r_index)

    return iter_triangle, iter_star


def turtle_dome(refine_level=3):
    """Generate faces of a dual icosphere polyhedron mapping the Z+ hemisphere

    Args:
        refine_level (int): the level of refinement of the dual icosphere. By
        default 46 ^polygons are returned (refine_level=3).

        For information, here are the number of faces obtained for the first ten
        refinement level: 0: 6, 1: 16, 2: 26, 3: 46, 4: 66, 5: 91, 6: 136,
        7: 196, 8: 251, 9: 341, 10: 406

    Returns:
        a list of vertices and a list of faces
    """

    vertices, faces = dual(*icosphere(*refine(refine_level)))
    # filter faces with centroids below horizontal plane
    centers = [centroid([vertices[p] for p in face]) for face in faces]
    median_height = numpy.median([c[2] for c in centers])
    edge = [vertices[v] for v in faces[0]]
    t = norm(numpy.array(edge[1]) - numpy.array(edge[0]))
    median_height -= (t / 4.)
    new_faces = [f for c, f in zip(centers, faces) if c[2] > median_height]
    filtered = sum(new_faces, [])
    mapping = {}
    new_vertices = []
    for v, pt in enumerate(vertices):
        if v in filtered:
            mapping[v] = len(new_vertices)
            new_vertices.append(pt)
    new_faces = [[mapping.get(v) for v in face] for face in new_faces]

    return new_vertices, new_faces


def sample_faces(vertices, faces, iter=2, spheric=False):
    """Generate a set of points that regularly sample the faces of a polyhedron
    the number of sampling points is 6 * 4**iter or 5 * 4**iter

    Args:
        vertices (list of tuples): list of 3D coordinates of polyhedron vertices
        faces (list of tuple): list of vertex indices defining the faces
        iter: the number of triangular interation to apply on the satr-split
        of the polyhedron. If None, face centers are returned
        speric (bool): if True, zenital and azimuth are returnd
        instead of points

    Returns:
        a {face_index: [points]} dict
    """

    if iter is None:
        points = {i: [centroid([vertices[p] for p in face])] for i, face in
                enumerate(faces)}
    else:
        tags = range(len(faces))
        vertices, faces, tags = star_split(vertices, faces, tags)
        for i in range(iter):
            vertices, faces, tags = split_triangles(vertices, faces, tags)

        points = {tag: [] for tag in set(tags)}
        for i, face in enumerate(faces):
            points[tags[i]].append(centroid([vertices[p] for p in face]))

    if spheric:
        points = {k:spherical(v) for k, v in points.iteritems()}

    return points

