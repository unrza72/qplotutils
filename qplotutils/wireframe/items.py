import logging

import numpy as np
from OpenGL import GL
from OpenGL.GL import (
    GL_DEPTH_TEST,
    GL_BLEND,
    GL_ALPHA_TEST,
    GL_CULL_FACE,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
    glEnable,
    glDisable,
    GL_ONE,
    GL_LINE_SMOOTH,
    GL_POLYGON_SMOOTH,
    GL_LINE_SMOOTH_HINT,
    GL_NICEST,
    glHint,
    GL_POLYGON_SMOOTH_HINT,
    glBlendFunc,
    glLineWidth,
    glBegin,
    GL_LINES,
    glColor4f,
    glVertex3f,
    glEnd,
    glVertexPointerf,
    glEnableClientState,
    glNormalPointerf,
    glDrawArrays,
    GL_TRIANGLES,
    glDisableClientState,
    GL_NORMAL_ARRAY,
    GL_VERTEX_ARRAY,
    GL_COLOR_ARRAY,
    glDrawElements,
    GL_UNSIGNED_INT,
)
from qtpy.QtCore import QObject
from qtpy.QtGui import QMatrix4x4

from qplotutils.wireframe.shader import ShaderRegistry

GLOptions = {
    "opaque": {
        GL_DEPTH_TEST: True,
        GL_BLEND: False,
        GL_ALPHA_TEST: False,
        GL_CULL_FACE: False,
    },
    "translucent": {
        GL_DEPTH_TEST: True,
        GL_BLEND: True,
        GL_ALPHA_TEST: False,
        GL_CULL_FACE: False,
        "glBlendFunc": (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA),
    },
    "additive": {
        GL_DEPTH_TEST: False,
        GL_BLEND: True,
        GL_ALPHA_TEST: False,
        GL_CULL_FACE: False,
        "glBlendFunc": (GL_SRC_ALPHA, GL_ONE),
    },
}

_log = logging.getLogger(__name__)

DEBUG = True


class GLGraphicsItem(QObject):
    _nextId = 0

    def __init__(self, parentItem=None):
        super(GLGraphicsItem, self).__init__()
        self._id = GLGraphicsItem._nextId
        GLGraphicsItem._nextId += 1

        self.__parent = None
        self.__view = None
        self.__children = set()
        self.__transform = QMatrix4x4()
        self.__visible = True
        self.setParentItem(parentItem)
        self.setDepthValue(0)
        self.__glOpts = {}

    def setParentItem(self, item):
        """Set this item's parent in the scenegraph hierarchy."""
        if self.__parent is not None:
            self.__parent.__children.remove(self)
        if item is not None:
            item.__children.add(self)
        self.__parent = item

        if self.__parent is not None and self.view() is not self.__parent.view():
            if self.view() is not None:
                self.view().removeItem(self)
            self.__parent.view().addItem(self)

    def setGLOptions(self, opts):
        """
        Set the OpenGL state options to use immediately before drawing this item.
        (Note that subclasses must call setupGLState before painting for this to work)

        The simplest way to invoke this method is to pass in the name of
        a predefined set of options (see the GLOptions variable):

        ============= ======================================================
        opaque        Enables depth testing and disables blending
        translucent   Enables depth testing and blending
                      Elements must be drawn sorted back-to-front for
                      translucency to work correctly.
        additive      Disables depth testing, enables blending.
                      Colors are added together, so sorting is not required.
        ============= ======================================================

        It is also possible to specify any arbitrary settings as a dictionary.
        This may consist of {'functionName': (args...)} pairs where functionName must
        be a callable attribute of OpenGL.GL, or {GL_STATE_VAR: bool} pairs
        which will be interpreted as calls to glEnable or glDisable(GL_STATE_VAR).

        For example::

            {
                GL_ALPHA_TEST: True,
                GL_CULL_FACE: False,
                'glBlendFunc': (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA),
            }


        """
        if isinstance(opts, str):
            opts = GLOptions[opts]
        self.__glOpts = opts.copy()
        self.update()

    def updateGLOptions(self, opts):
        """
        Modify the OpenGL state options to use immediately before drawing this item.
        *opts* must be a dictionary as specified by setGLOptions.
        Values may also be None, in which case the key will be ignored.
        """
        self.__glOpts.update(opts)

    def parentItem(self):
        """Return a this item's parent in the scenegraph hierarchy."""
        return self.__parent

    def childItems(self):
        """Return a list of this item's children in the scenegraph hierarchy."""
        return list(self.__children)

    # def _setView(self, v):
    #     self.__view = v
    #
    # def view(self):
    #     return self.__view
    @property
    def view(self):
        return self.__view

    @view.setter
    def view(self, value):
        self.__view = value

    def setDepthValue(self, value):
        """
        Sets the depth value of this item. Default is 0.
        This controls the order in which items are drawn--those with a greater depth value will be drawn later.
        Items with negative depth values are drawn before their parent.
        (This is analogous to QGraphicsItem.zValue)
        The depthValue does NOT affect the position of the item or the values it imparts to the GL depth buffer.
        """
        self.__depthValue = value

    def depthValue(self):
        """Return the depth value of this item. See setDepthValue for more information."""
        return self.__depthValue

    def setTransform(self, tr):
        """Set the local transform for this object.
        Must be a :class:`Transform3D <pyqtgraph.Transform3D>` instance. This transform
        determines how the local coordinate system of the item is mapped to the coordinate
        system of its parent."""
        self.__transform = tr  # Transform3D(tr)
        self.update()

    def resetTransform(self):
        """Reset this item's transform to an identity transformation."""
        self.__transform.setToIdentity()
        self.update()

    def applyTransform(self, tr, local):
        """
        Multiply this object's transform by *tr*.
        If local is True, then *tr* is multiplied on the right of the current transform::

            newTransform = transform * tr

        If local is False, then *tr* is instead multiplied on the left::

            newTransform = tr * transform
        """
        if local:
            self.setTransform(self.transform() * tr)
        else:
            self.setTransform(tr * self.transform())

    def transform(self):
        """Return this item's transform object."""
        return self.__transform

    def viewTransform(self):
        """Return the transform mapping this item's local coordinate system to the
        view coordinate system."""
        tr = self.__transform
        p = self
        while True:
            p = p.parentItem()
            if p is None:
                break
            tr = p.transform() * tr
        return tr

    def translate(self, dx, dy, dz, local=False):
        """
        Translate the object by (*dx*, *dy*, *dz*) in its parent's coordinate system.
        If *local* is True, then translation takes place in local coordinates.
        """
        tr = QMatrix4x4()  # Transform3D()
        tr.translate(dx, dy, dz)
        self.applyTransform(tr, local=local)

    def rotate(self, angle, x, y, z, local=False):
        """
        Rotate the object around the axis specified by (x,y,z).
        *angle* is in degrees.

        """
        tr = QMatrix4x4()
        tr.rotate(angle, x, y, z)
        self.applyTransform(tr, local=local)

    def scale(self, x, y, z, local=True):
        """
        Scale the object by (*dx*, *dy*, *dz*) in its local coordinate system.
        If *local* is False, then scale takes place in the parent's coordinates.
        """
        tr = QMatrix4x4()
        tr.scale(x, y, z)
        self.applyTransform(tr, local=local)

    def hide(self):
        """Hide this item.
        This is equivalent to setVisible(False)."""
        self.setVisible(False)

    def show(self):
        """Make this item visible if it was previously hidden.
        This is equivalent to setVisible(True)."""
        self.setVisible(True)

    def setVisible(self, vis):
        """Set the visibility of this item."""
        self.__visible = vis
        self.update()

    def visible(self):
        """Return True if the item is currently set to be visible.
        Note that this does not guarantee that the item actually appears in the
        view, as it may be obscured or outside of the current view area."""
        return self.__visible

    def initializeGL(self):
        """
        Called after an item is added to a GLViewWidget.
        The widget's GL context is made current before this method is called.
        (So this would be an appropriate time to generate lists, upload textures, etc.)
        """
        pass

    def setupGLState(self):
        """
        This method is responsible for preparing the GL state options needed to render
        this item (blending, depth testing, etc). The method is called immediately before painting the item.
        """
        for k, v in self.__glOpts.items():
            if v is None:
                continue
            if isinstance(k, str):
                func = getattr(GL, k)
                func(*v)
            else:
                if v is True:
                    glEnable(k)
                else:
                    glDisable(k)

    def paint(self):
        """
        Called by the GLViewWidget to draw this item.
        It is the responsibility of the item to set up its own modelview matrix,
        but the caller will take care of pushing/popping.
        """
        self.setupGLState()

    def update(self):
        """
        Indicates that this item needs to be redrawn, and schedules an update
        with the view it is displayed in.
        """
        v = self.view
        if v is None:
            return
        v.update()

    def mapToParent(self, point):
        tr = self.transform()
        if tr is None:
            return point
        return tr.map(point)

    def mapFromParent(self, point):
        tr = self.transform()
        if tr is None:
            return point
        return tr.inverted()[0].map(point)

    def mapToView(self, point):
        tr = self.viewTransform()
        if tr is None:
            return point
        return tr.map(point)

    def mapFromView(self, point):
        tr = self.viewTransform()
        if tr is None:
            return point
        return tr.inverted()[0].map(point)


class Grid(GLGraphicsItem):
    def __init__(
        self, x=10, y=10, xs=1.0, ys=1.0, edge_color=(0.7, 0.7, 0.7, 1), parentItem=None
    ):
        super(Grid, self).__init__(parentItem)
        self.edge_color = edge_color

        self.x, self.y = x, y
        self.xs, self.ys = xs, ys

    def paint(self):
        super(Grid, self).paint()

        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glLineWidth(1.3)
        glBegin(GL_LINES)  # lgtm [py/call/wrong-arguments]

        xvals = np.linspace(-self.x / 2.0, self.x / 2.0, self.x / self.xs + 1)
        yvals = np.linspace(-self.y / 2.0, self.y / 2.0, self.y / self.ys + 1)

        glColor4f(*self.edge_color)
        for x in xvals:
            glVertex3f(x, yvals[0], 0)
            glVertex3f(x, yvals[-1], 0)
        for y in yvals:
            glVertex3f(xvals[0], y, 0)
            glVertex3f(xvals[-1], y, 0)
        glEnd()  # lgtm [py/call/wrong-arguments]


class CoordinateCross(GLGraphicsItem):
    def __init__(self, parentItem=None):
        super(CoordinateCross, self).__init__(parentItem)

    def paint(self):
        super(CoordinateCross, self).paint()
        glLineWidth(20.0)
        glBegin(GL_LINES)  # lgtm [py/call/wrong-arguments]
        # X
        glColor4f(1, 0, 0, 0.3)
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)

        glColor4f(0, 1, 0, 0.3)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 1, 0)

        glColor4f(0, 0, 1, 0.3)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 1)

        glEnd()  # lgtm [py/call/wrong-arguments]


class Box(GLGraphicsItem):
    def __init__(self, parentItem=None):
        super(Box, self).__init__(parentItem)

        self.length = 4  # in x from point of origin
        self.width = 2  # in y central to point of origin
        self.height = 1.2  # in z from point of origin

    def paint(self):
        super(Box, self).paint()

        l = self.length
        wh = self.width / 2.0
        # h = self.height

        p = [
            [0, wh, 0],
            [l, wh, 0],
            [l, -wh, 0],
            [0, -wh, 0],
            [0, wh, 1],
            [l, wh, 1],
            [l, -wh, 1],
            [0, -wh, 1],
        ]

        m = [
            [0, 1, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]

        glLineWidth(2.0)
        glBegin(GL_LINES)  # lgtm [py/call/wrong-arguments]

        glColor4f(1, 0, 0, 1)
        for k in range(8):
            for j in range(k + 1, 8):
                if m[k][j] == 1:
                    glVertex3f(*p[k])
                    glVertex3f(*p[j])

        glEnd()  # lgtm [py/call/wrong-arguments]


class Mesh(object):
    def __init__(self, has_wireframe=False):
        self.has_wireframe = has_wireframe

        # Array (N,3,3) of all the faces of the mesh. Where N is the number of triangles which is defined by 3 vectors in R3
        self.face_vertices = None

        # Array (N,3,3) of the face normal vectors, Same size as face vertices.
        # self.face_normal_vectors = None
        self._vertix_normalized_face_normal_vectors = None
        self._face_normalized_face_normal_vectors = None

        # self.debug_face_normals_vertices = None
        # self.debug_face_normals_edges = None

        self.face_edges = None

        self.smooth = False

        # Wireframe array and adge mapping
        self.wireframe_vertices = None
        self.wireframe_edges = None

    @property
    def face_normal_vectors(self):
        if self.smooth:
            return self._vertix_normalized_face_normal_vectors
        else:
            return self._face_normalized_face_normal_vectors

    @staticmethod
    def sphere(stacks=8, sectors=8, radius=1):

        vertices = np.zeros(shape=((stacks - 1) * sectors + 2, 3), dtype=np.float)

        sh = np.pi / (1.0 * stacks)
        thetas = np.linspace(
            0 + sh, np.pi - sh, stacks - 1, endpoint=True, dtype=np.float
        )
        phis = np.linspace(0, 2 * np.pi, sectors, endpoint=False, dtype=np.float)

        for k, theta in enumerate(thetas):
            z = radius * np.cos(theta)
            xy = radius * np.sin(theta)

            for j, phi in enumerate(phis):
                x = xy * np.sin(phi)
                y = xy * np.cos(phi)

                vertices[k * sectors + j] = [x, y, z]

        vertices[-2] = [0, 0, -1 * radius]
        vertices[-1] = [0, 0, 1 * radius]

        faces_top = np.zeros((sectors, 3), np.int)
        faces_bottom = np.zeros((sectors, 3), np.int)
        faces1 = np.zeros((sectors * (stacks - 2), 3), np.int)
        faces2 = np.zeros((sectors * (stacks - 2), 3), np.int)

        # top
        for k in range(sectors):
            f0 = len(vertices) - 1
            f1 = k
            if k + 1 == sectors:
                f2 = 0
            else:
                f2 = k + 1
            faces_top[k] = [f0, f2, f1]

        # bottom
        for k in range(sectors):
            f0 = len(vertices) - 2
            f1 = (stacks - 2) * sectors + k
            if k + 1 == sectors:
                f2 = (stacks - 2) * sectors
            else:
                f2 = (stacks - 2) * sectors + k + 1
            faces_bottom[k] = [f1, f2, f0]

        for k in range(stacks - 2):
            for l in range(sectors):
                f0 = k * sectors + l
                if l + 1 == sectors:
                    f1 = k * sectors
                else:
                    f1 = k * sectors + l + 1
                f2 = (k + 1) * (sectors) + l

                if l == 0:
                    f3 = (k + 1) * (sectors) + sectors - 1
                else:
                    f3 = (k + 1) * (sectors) + (l - 1)

                faces1[f0] = [f0, f1, f2]

                faces2[f0] = [f0, f2, f3]

        faces = np.concatenate((faces_top, faces_bottom, faces1, faces2), axis=0)
        tt = Mesh.compute_face_arrays(vertices, faces)
        return tt

    @staticmethod
    def cone(n_faces=4, radius=1, height=1):
        """ Return a mesh for a cone with the defined number of faces
        """

        vertices = np.zeros((n_faces + 2, 3), np.float)
        for k in range(n_faces):
            x = np.sin(2 * np.pi * k / n_faces) * radius
            y = np.cos(2 * np.pi * k / n_faces) * radius

            vertices[k] = [x, y, 0]
        vertices[n_faces] = [0, 0, height]

        a = np.arange(0, n_faces, 1, dtype=np.uint8)
        b = np.roll(a, 1)
        t_faces = np.array([a, b, np.ones(n_faces) * n_faces], dtype=np.uint8).T

        b_faces = np.array([b, a, np.ones(n_faces) * (n_faces + 1)], dtype=np.uint8).T

        faces = np.append(t_faces, b_faces, axis=0)

        tt = Mesh.compute_face_arrays(vertices, faces)
        return tt

    @staticmethod
    def compute_face_arrays(vertices, faces, wireframe_edges=None):
        # n_faces = faces.shape[0]
        n_vertices = vertices.shape[0]

        # compute face vertices
        v = vertices[faces]

        # face normals
        nv = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
        nvl = np.linalg.norm(nv, axis=1)
        nv = nv / nvl.reshape(-1, 1)

        # non-smoothed face normals
        norms = np.zeros((nv.shape[0], 3, 3))
        norms[:] = nv[:, np.newaxis, :]

        # smothed normals,
        # make vector to compute all normals attached to a vertix
        vertices_norms_mask = np.zeros(
            (faces.shape[0], vertices.shape[0]), dtype=np.uint8
        )
        for k, f in enumerate(faces):
            vertices_norms_mask[k, f[0]] = 1
            vertices_norms_mask[k, f[1]] = 1
            vertices_norms_mask[k, f[2]] = 1

        vertice_norms = np.zeros(vertices.shape, np.float)
        for v_idx in range(n_vertices):
            f_idx, = np.where(vertices_norms_mask[:, v_idx] == 1)
            if f_idx is None or len(f_idx) == 0:
                continue

            f_idx_u = np.unique(f_idx)
            nn = nv[f_idx_u]
            vertice_norms[v_idx] = np.sum(nn, axis=0) / len(f_idx_u)

        norms2 = vertice_norms[faces]

        # computation for mesh grid vizu
        face_edges = np.zeros((faces.shape[0] * 3, 2), np.int)
        for k, f in enumerate(faces):
            a = np.sort(f)
            face_edges[k] = [a[0], a[1]]
            face_edges[faces.shape[0] + k] = [a[1], a[2]]
            face_edges[faces.shape[0] * 2 + k] = [a[0], a[2]]

        face_edges = np.unique(face_edges, axis=0)

        md = Mesh()

        if wireframe_edges is not None:
            md.wireframe_edges = wireframe_edges
            md.has_wireframe = True

        md.wireframe_vertices = vertices
        md.face_vertices = v
        md._face_normalized_face_normal_vectors = norms
        md._vertix_normalized_face_normal_vectors = norms2
        md.face_edges = face_edges
        return md

    @staticmethod
    def cube(edge_length=1.0):
        vertices = (
            np.array(
                [
                    [0, 0, 0],
                    [1, 0, 0],
                    [0, 1, 0],
                    [1, 1, 0],
                    [0, 0, 1],
                    [1, 0, 1],
                    [0, 1, 1],
                    [1, 1, 1],
                ]
            )
            * edge_length
            - edge_length / 2.0
        )

        # Every cube side is constructed of two triangles
        # be careful with culling
        faces = np.array(
            [
                [0, 2, 1],  # ok
                [2, 3, 1],
                [0, 1, 4],  # ok
                [1, 5, 4],
                [1, 3, 5],  # ok
                [3, 7, 5],
                [2, 7, 3],  # ok
                [2, 6, 7],
                [0, 6, 2],  # ok
                [0, 4, 6],
                [4, 5, 6],  # ok
                [5, 7, 6],
            ]
        )

        # Hand constructed:
        wireframe_edges = np.array(
            [
                [0, 1],
                [1, 3],
                [3, 2],
                [2, 0],
                [4, 5],
                [5, 7],
                [7, 6],
                [6, 4],
                [0, 4],
                [1, 5],
                [2, 6],
                [3, 7],
            ],
            np.int8,
        )

        return Mesh.compute_face_arrays(vertices, faces, wireframe_edges)


class MeshItem(GLGraphicsItem):
    def __init__(
        self,
        mesh_data,
        parentItem=None,
        shader=None,
        face_color=(0.6, 0.6, 0.6, 1.0),
        edge_color=(1.0, 0.5, 0.5, 1.0),
        smooth=False,
        gloptions="opaque",
    ):
        super(MeshItem, self).__init__(parentItem)

        self.draw_faces = True
        self.draw_wireframe = False

        self.debug_face_normals = False
        self.debug_face_edges = False

        self.__antialiasing = True
        self.edge_color = edge_color
        self.face_color = face_color

        self.shader_registry = ShaderRegistry()
        self.shader_registry.add(shader)
        self.shader_program = self.shader_registry[shader]
        self.setGLOptions(gloptions)

        self.mesh = mesh_data
        self.mesh.smooth = smooth

    def initializeGL(self):
        _log.debug("InitializeGL")
        # self.mesh = Mesh.cone() # cube()

    def paint(self):
        self.setupGLState()

        if self.__antialiasing:
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            glLineWidth(1.5)

        if self.draw_faces:
            # need face
            with self.shader_program:
                glEnableClientState(GL_VERTEX_ARRAY)

                glVertexPointerf(self.mesh.face_vertices)
                glColor4f(*self.face_color)

                glEnableClientState(GL_NORMAL_ARRAY)
                glNormalPointerf(self.mesh.face_normal_vectors)

                glDrawArrays(
                    GL_TRIANGLES, 0, np.product(self.mesh.face_vertices.shape[:-1])
                )

                glDisableClientState(GL_NORMAL_ARRAY)
                glDisableClientState(GL_VERTEX_ARRAY)
                glDisableClientState(GL_COLOR_ARRAY)

        if self.debug_face_normals:
            # Visualize the face normal vectors
            glEnableClientState(GL_VERTEX_ARRAY)

            N = self.mesh.face_vertices.shape[0] * 3
            v = np.concatenate(
                [
                    self.mesh.face_vertices,
                    self.mesh.face_vertices + self.mesh.face_normal_vectors,
                ]
            )
            e = np.array([np.arange(N), np.arange(N) + N]).T.flatten()

            glColor4f(1.0, 1.0, 0.0, 1.0)
            glVertexPointerf(v)
            glDrawElements(GL_LINES, e.shape[0], GL_UNSIGNED_INT, e)

            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)

        if self.debug_face_edges:
            # visualize all face edges
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointerf(self.mesh.wireframe_vertices)

            glColor4f(1.0, 1.0, 0.0, 1.0)
            edges = self.mesh.face_edges.flatten()
            glDrawElements(GL_LINES, edges.shape[0], GL_UNSIGNED_INT, edges)

            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)

        if self.draw_wireframe and self.mesh.has_wireframe:
            # draw a mesh wireframe which may or may not be identical to the face edges, depending on the mesh
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointerf(self.mesh.wireframe_vertices)
            glColor4f(0, 1, 0, 1)
            edges = self.mesh.wireframe_edges.flatten()
            glDrawElements(GL_LINES, edges.shape[0], GL_UNSIGNED_INT, edges)

            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)
