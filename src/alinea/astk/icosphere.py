# -*- python -*-
#
#       Copyright 2015 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       WebSite : https://github.com/openalea-incubator/astk
#
# ==============================================================================
"""
generation of icosphere

this is a python implementation of the C code found here:
http://blog.andreaskahler.com/2009/06/creating-icosphere-mesh-in-code.html
"""
import math
import numpy
import openalea.plantgl.all as pgl


def display(vertices, faces):
    """ Visualisation of a mesh with PlantGl"""

    shape = pgl.Shape(pgl.FaceSet(pointList=vertices, indexList=faces))
    pgl.Viewer.display(shape)


def norm(point):
    """ normalised coordinate of (0,point) vector
    """
    x, y, z = point
    radius = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    return x / radius, y / radius, z / radius


def roty(pt, theta):
    """ rotated coordinate of pt arround z-axis"""
    x, y, z = pt
    return x * math.cos(theta) + z * math.sin(theta), \
           y, \
           -x * math.sin(theta) + z * math.cos(theta)

def middle_point(p1, p2):
    """ coordinates of the middle point between p1 and p2
    """
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return (x1 + x2) / 2., (y1 + y2) / 2., (z1 + z2) / 2.,


def icosahedron():
    """ Creates the vertices and faces of an icosahedron incribed in a 
    unit_sphere"""

    t = (1.0 + math.sqrt(5.0)) / 2.0
    # align one point with z
    rot = math.atan2(t,1)
    vertices = []
    vertices.append(norm(roty((-1, t, 0), rot)))
    vertices.append(norm(roty((1, t, 0), rot)))
    vertices.append(norm(roty((-1, -t, 0), rot)))
    vertices.append(norm(roty((1, -t, 0), rot)))

    vertices.append(norm(roty((0, -1, t), rot)))
    vertices.append(norm(roty((0, 1, t), rot)))
    vertices.append(norm(roty((0, -1, -t), rot)))
    vertices.append(norm(roty((0, 1, -t), rot)))

    vertices.append(norm(roty((t, 0, -1), rot)))
    vertices.append(norm(roty((t, 0, 1), rot)))
    vertices.append(norm(roty((-t, 0, -1), rot)))
    vertices.append(norm(roty((-t, 0, 1), rot)))

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


def icosphere(recursion=1):
    """ Create the vertex and faces of the icosphere obtained after n recursions
     of the icosahedron face spliting

     The number of faces obtained after n recursion is 20*(n + 1)"""

    vertices, faces = icosahedron()

    for i in range(recursion):
        # cache is a (index_p1, index_p2): middle_point_index dict refering
        # to vertices
        cache = {}
        for j in range(len(faces)):
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
                vertices.append(norm(middle_point(p1, p2)))
                va = len(vertices) - 1
                cache.update({ka: va})
            if kb in cache:
                vb = cache[kb]
            else:
                vertices.append(norm(middle_point(p2, p3)))
                vb = len(vertices) - 1
                cache.update({kb: vb})
            if kc in cache:
                vc = cache[kc]
            else:
                vertices.append(norm(middle_point(p1, p3)))
                vc = len(vertices) - 1
                cache.update({kc: vc})

            faces.append((v1, va, vc))
            faces.append((v2, vb, va))
            faces.append((v3, vc, vb))
            faces.append((va, vb, vc))

    return vertices, faces


def mass_center(face, points):
    x, y, z = zip([points[i] for i in face])
    return numpy.mean(x), numpy.mean(y), numpy.mean(z)

def dual(vertices, faces):
    """ generate the dual polyhedron of the input spherical mesh"""

    centers = []
    dual_vertices = []
    dual_faces = []
    cache = {}
    for icenter, center in enumerate(vertices):
        new_face = []
        centers.append(center)
        ifaces = [i for i,f in enumerate(faces) if icenter in f]
        next_face = 0
        for j in range(len(ifaces)):
            iface = ifaces.pop(next_face)
            face = faces[iface]
            if len(ifaces) > 1:
                next_pt = face[((numpy.where(numpy.array(face) == icenter)[0] + 2) % 3)[0]]
                next_face = [i for i,f in enumerate(ifaces) if next_pt in faces[f]][0]
            else:
                next_face = 0
            if iface in cache:
                new_face.append(cache[iface])
            else:
                cache[iface] = len(dual_vertices)
                new_face.append(len(dual_vertices))
                dual_vertices.append(mass_center(faces[iface], vertices))
        dual_faces.append(new_face)



        face_centers = [mass_center(faces[i], vertices) for i in ifaces]

        origin = numpy.array(center)
        vect = [numpy.array(c) - origin for c in face_centers]
        order = numpy.argsort([numpy.arctan2(
            numpy.linalg.norm(numpy.cross(vect[0], v)), numpy.dot(vect[0], v))
                               for v in vect])
        new_face = []
        for o in order:
            if ifaces[o] in cache:
                new_face.append(cache[ifaces[o]])
            else:
                cache[ifaces[o]] = len(dual_vertices)
                new_face.append(len(dual_vertices))
                dual_vertices.append(face_centers[o])
        dual_faces.append(new_face)
    return dual_vertices, dual_faces, centers



def hemi_icosphere(recursion=1):
    """ generate a Z+ hemi-icosphere"""
    vertices, faces = icosphere(recursion)
    mapping = {}
    filtered = []
    for i, v in enumerate(vertices):
        if v[2] >= -1e-6:
            mapping[i] = len(filtered)
            filtered.append(v)
    faces = [tuple([mapping.get(iv) for iv in f]) for f in faces if all([index in mapping for index in f])]
    return filtered, faces


def turtle_direction(recursion=1):
    """ generate the turtle directions at a given level of recursion"""

    vertices, faces = icosphere(recursion)
    theta = [math.pi / 2 - math.acos(v[2]) for v in vertices]
    phi = [math.atan2(v[1], v[0]) for v in vertices]
    return [(t, p) for t, p in zip(theta, phi) if t > 0]

