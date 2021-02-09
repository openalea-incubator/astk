import numpy
import pandas
from alinea.astk.scene.tagged_mesh import spherical, surface, normal, \
    centroid, random_normals, equilateral, move_points


class SurfacicPointCloud(object):
    """A data structure for handling discrete spatial distribution of surface"""

    units = {'mm': 0.001, 'cm': 0.01, 'dm': 0.1, 'm': 1, 'dam': 10, 'hm': 100,
             'km': 1000}

    def __init__(self, x, y, z, area, normals=None, shape_id=None,
                 properties=None, scene_unit='m'):
        """Instantiate a SurfacicPointCloud canopy from a list of points

        Args:
            x: (array-like) x-coordinate of surfacic elements
            y: (array-like) y-coordinate of surfacic elements
            z: (array-like) z-coordinate of surfacic elements
            area: (array-like) areas of surfacic elements
            normals: (array of 3-tuples): coordinates of vector normal to
             surfacic point. If None, normals are randomly sampled.
            shape_id: (array-like) vector of identifiers that allow tagging
             points as elements of the same scene object. If None (default),
            shape_id is set to its index in input arrays.
            properties: (name: {sh_id: value}) optional additional data that
             allow associating scalar property to points via their shape_id.
            scene_unit: (string) the length unit used for inputs.

        Returns:
            a surfacic point cloud instance with all data converted to meter
            (m)
        """

        x, y, z, area = map(lambda val: numpy.array(val, ndmin=1),
                            (x, y, z, area))

        try:
            self.convert = self.units[scene_unit]
        except KeyError:
            print 'Warning, unit', scene_unit, 'not found, meter assumed'
            self.convert = 1

        if normals is None:
            normals = random_normals(len(x))

        if shape_id is None:
            shape_id = range(len(x))

        if properties is None:
            properties = {}

        assert len(x) == len(y) == len(z) == len(area) == len(normals) == len(
            shape_id)

        self.size = len(x)
        self.x = x * self.convert
        self.y = y * self.convert
        self.z = z * self.convert
        self.area = area * self.convert**2
        self.point_id = range(len(x))
        self.shape_id = shape_id
        self.normals = normals
        self.properties = properties

    @staticmethod
    def from_scene_mesh(scene_mesh, properties=None, scene_unit='m'):
        """ Instantiation from a scene mesh dict

        Args:
            scene_mesh: a {shape_id: (vertices, faces)} dict
            properties: (name:{shape_id: entity}) optional additional
                named data associated to surfacic points.
            properties: (name: {sh_id: value}) optional additional data that
             allow associating scalar property to points via their shape_id.
            scene_unit: (string) the length unit used for inputs.
        """

        areas, x, y, z, normals, shape_id = [[] for _ in range(6)]
        for sh_id, (vertices, faces) in scene_mesh.iteritems():
            areas += [surface(f, vertices) for f in faces]
            xx, yy, zz = zip(*[centroid(f, vertices) for f in faces])
            x += list(xx)
            y += list(yy)
            z += list(zz)
            normals += [normal(f, vertices) for f in faces]
            shape_id.extend([sh_id] * len(faces))
        return SurfacicPointCloud(x=x, y=y, z=z, area=areas, normals=normals,
                                  shape_id=shape_id,
                                  properties=properties, scene_unit=scene_unit)

    def as_data_frame(self, add_properties=True):
        nx, ny, nz = zip(*self.normals)
        df = pandas.DataFrame({'point_id': self.point_id, 'x': self.x, 'y': self.y,
                               'z': self.z, 'shape_id': self.shape_id,
                               'area': self.area,
                               'norm_x': nx, 'norm_y': ny, 'norm_z': nz})

        if add_properties and len(self.properties) > 0:
            d = {'shape_id': self.shape_id}
            for k, v in self.properties.iteritems():
                d.update({k: [v[sh] for sh in self.shape_id]})
            df = df.merge(pandas.DataFrame(d))

        return df

    @staticmethod
    def from_data_frame(df):
        d = df.to_dict('list')
        cols = (
            'x', 'y', 'z', 'area', 'shape_id', 'point_id', 'norm_x', 'norm_y',
            'norm_z')

        property_cols = [col for col in d if col not in cols]
        properties = None
        if len(property_cols) > 0:
            dfp = df.loc[:,['shape_id'] + property_cols].groupby('shape_id').agg(
                lambda x: x.iloc[0]).reset_index()
            dfpd = dfp.to_dict('list')
            properties = {k: dict(zip(dfpd['shape_id'], dfpd[k])) for k in
                          property_cols}

        normals = zip(d['norm_x'], d['norm_y'], d['norm_z'])

        return SurfacicPointCloud(x=d['x'], y=d['y'], z=d['z'], area=d['area'],
                                  shape_id=d['shape_id'], normals=normals,
                                  properties=properties)

    def shape_map(self):
        return pandas.DataFrame(
            {'point_id': self.point_id, 'shape_id': self.shape_id
             })

    def area_map(self):
        return pandas.DataFrame(
            {'point_id': self.point_id, 'area': self.area
             })

    def xyz_map(self):
        return pandas.DataFrame(
            {'point_id': self.point_id, 'x': self.x, 'y': self.y, 'z': self.z
             })

    def as_scene_mesh(self):
        """ A simple mesh representation of the point cloud"""

        scene = {}
        df = self.as_data_frame(add_properties=False)
        for sh_id, g in df.groupby('shape_id'):
            vertices = []
            faces = []
            nf = 0
            for ind, row in g.iterrows():
                tri = equilateral(row.area)
                rot = numpy.random.rand() * numpy.pi / 3
                norm = row.norm_x, row.norm_y, row.norm_z
                pos = row.x, row.y, row.z
                pts = move_points(tri, pos, norm, rot)
                vertices.extend(pts)
                faces.append((3 * nf, 3 * nf + 1, 3 * nf + 2))
                nf += 1
            scene[sh_id] = vertices, faces
        return scene

    def as_triangle_scene(self):
        """ A {id: [triangles,..] representation of the point cloud"""
        scene = {}
        df = self.as_data_frame(add_properties=False)
        for sh_id, g in df.groupby('shape_id'):
            triangles=[]
            for ind, row in g.iterrows():
                tri = equilateral(row.area)
                rot = numpy.random.rand() * numpy.pi / 3
                norm = row.norm_x, row.norm_y, row.norm_z
                pos = row.x, row.y, row.z
                pts = move_points(tri, pos, norm, rot)
                triangles.append(pts)
            scene[sh_id] = triangles
        return scene

    def save(self, path='surfacic_point_cloud.csv'):
        """ Save a csv representation of the object
        """
        df = self.as_data_frame()
        df.to_csv(path, index=False)
        return path

    @staticmethod
    def load(path='surfacic_point_cloud.csv'):
        df = pandas.read_csv(path)
        return SurfacicPointCloud.from_data_frame(df)

    def bbox(self):
        return (self.x.min(), self.y.min(), self.z.min()), (self.x.max(), \
               self.y.max(), self.z.max())

    def inclinations(self):
        """ inclinations angles of normals (degrees, positive)"""
        theta, phi = zip(*map(spherical, self.normals))
        inclin = numpy.degrees(theta)
        inclin = numpy.where(inclin == 90, 90, inclin % 90)
        df = pandas.DataFrame(
            {'point_id': self.point_id, 'shape_id': self.shape_id, 'inclination': inclin})
        return df

    def subset(self, point_id=None, shape_id=None):
        """return a surfacic point cloud that is a subset of the calling
        object"""

        df = self.as_data_frame()
        if point_id is not None:
            if not hasattr(point_id, '__len__'):
                point_id = [point_id]
            df = df.loc[df.point_id.isin(point_id), :]
        if shape_id is not None:
            if not hasattr(shape_id, '__len__'):
                shape_id = [shape_id]
            df = df.loc[df.shape_id.isin(shape_id), :]

        return self.from_data_frame(df)
