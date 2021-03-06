#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wireframe view widget to display 3D visualizations.


"""
import logging

import numpy as np
from OpenGL.GL import (
    GL_DEPTH_TEST,
    glEnable,
    GL_LEQUAL,
    glLight,
    GL_LIGHT0,
    GL_POSITION,
    glMaterialfv,
    GL_SPECULAR,
    GL_FRONT,
    GL_SHININESS,
    glDepthFunc,
    glMaterialf,
    glViewport,
    glMatrixMode,
    GL_PROJECTION,
    glLoadIdentity,
    glMultMatrixf,
    GL_MODELVIEW,
    glClearColor,
    glClear,
    GL_DEPTH_BUFFER_BIT,
    GL_COLOR_BUFFER_BIT,
    glPushAttrib,
    GL_ALL_ATTRIB_BITS,
    glLoadName,
    glPopAttrib,
    glPushMatrix,
    glPopMatrix,
)
from OpenGL.error import GLError
from qtpy.QtCore import Signal, Qt, QObject, QTime

from qtpy.QtGui import QMatrix4x4, QVector3D
from qtpy.QtOpenGL import QGLWidget

from qplotutils import CONFIG
from qplotutils.wireframe.base_types import Vector3d
from qplotutils.wireframe.cam_control import CamControl

_log = logging.getLogger(__name__)

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"


class ViewProperties(QObject):
    changed = Signal()

    def __init__(self, parent=None):
        super(ViewProperties, self).__init__(parent)
        self._center = Vector3d(0, 0, 0)
        self._distance = 10
        self._fov = 60
        self._azimuth_angle = 60
        self._elevation_angle = 45

        self.viewport = None
        self.background_color = (37.3 / 100.0, 40 / 100.0, 45.9 / 100.0, 0)

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, value):
        self._center = value
        self.changed.emit()

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value
        self.changed.emit()

    @property
    def fov(self):
        return self._fov

    @fov.setter
    def fov(self, value):
        self._fov = value
        self.changed.emit()

    @property
    def azimuth_angle(self):
        return self._azimuth_angle

    @azimuth_angle.setter
    def azimuth_angle(self, value):
        self._azimuth_angle = value
        self.changed.emit()

    @property
    def elevation_angle(self):
        return self._elevation_angle

    @elevation_angle.setter
    def elevation_angle(self, value):
        self._elevation_angle = value
        self.changed.emit()


class ChartView3d(QGLWidget):
    """ Widget to display openGL items.
    """

    def __init__(self, parent=None):
        """

        :param parent:
        """
        super(ChartView3d, self).__init__(parent)
        self.setFocusPolicy(Qt.ClickFocus)

        self.format().setSamples(4)

        self.props = ViewProperties()
        self.items = []

        self.makeCurrent()

        self.cam_ctrl = CamControl(self.props, self)
        self.cam_ctrl.show()

        self.props.changed.connect(self.camera_update)

        self.frame_count = 0
        self.frame_time = QTime()
        self.frame_time.start()

    def addItem(self, item):
        self.items.append(item)
        if hasattr(item, "initializeGL"):
            self.makeCurrent()
            item.initializeGL()

        item.view = self
        self.update()

    def removeItem(self, item):
        self.items.remove(item)
        item.view = None
        self.update()

    def initializeGL(self):

        self.resizeGL(self.width(), self.height())

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # lighting
        light_position = [1.0, 1.0, 2.0, 0.0]
        glLight(GL_LIGHT0, GL_POSITION, light_position)
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 100.0)

    def getViewport(self):
        vp = self.props.viewport
        if vp is None:
            return 0, 0, self.width(), self.height()
        else:
            return vp

    def resizeGL(self, w, h):
        glViewport(*self.getViewport())
        self.setProjection()
        self.setModelview()

    def setProjection(self, region=None):
        m = self.projectionMatrix(region)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        a = np.array(m.copyDataTo()).reshape((4, 4))
        glMultMatrixf(a.transpose())

    def projectionMatrix(self, region=None):
        # Xw = (Xnd + 1) * width/2 + X
        if region is None:
            region = (0, 0, self.width(), self.height())

        x0, y0, w, h = self.getViewport()
        dist = self.props.distance
        fov = self.props.fov
        nearClip = dist * 0.001
        farClip = dist * 1000.0

        r = nearClip * np.tan(fov * 0.5 * np.pi / 180.0)
        t = r * h / w

        # convert screen coordinates (region) to normalized device coordinates
        # Xnd = (Xw - X0) * 2/width - 1
        ## Note that X0 and width in these equations must be the values used in viewport
        left = r * ((region[0] - x0) * (2.0 / w) - 1)
        right = r * ((region[0] + region[2] - x0) * (2.0 / w) - 1)
        bottom = t * ((region[1] - y0) * (2.0 / h) - 1)
        top = t * ((region[1] + region[3] - y0) * (2.0 / h) - 1)

        tr = QMatrix4x4()
        tr.frustum(left, right, bottom, top, nearClip, farClip)
        return tr

    def setModelview(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        m = self.viewMatrix()
        a = np.array(m.copyDataTo()).reshape((4, 4))
        glMultMatrixf(a.transpose())

    def viewMatrix(self):
        tr = QMatrix4x4()
        ntr = np.eye(4, dtype=np.float)

        tr.translate(0.0, 0.0, -self.props.distance)
        ntr[0:3, 3] = [0.0, 0.0, -self.props.distance]

        tr.rotate(self.props.elevation_angle - 90, 1, 0, 0)

        tr.rotate(self.props.azimuth_angle - 90, 0, 0, -1)
        center = self.props.center
        tr.translate(-center[0], -center[1], -center[2])
        return tr

    # def itemsAt(self, region=None):
    #     """
    #     Return a list of the items displayed in the region (x, y, w, h)
    #     relative to the widget.
    #     """
    #
    #     #TODO: Check if it works
    #     region = (
    #         region[0],
    #         self.height() - (region[1] + region[3]),
    #         region[2],
    #         region[3],
    #     )
    #
    #     # buf = np.zeros(100000, dtype=np.uint)
    #     # buf = glSelectBuffer(100000)
    #     try:
    #         glRenderMode(GL_SELECT)
    #         glInitNames()
    #         glPushName(0)
    #         self._itemNames = {}
    #         self.paintGL(region=region, useItemNames=True)
    #
    #     finally:
    #         hits = glRenderMode(GL_RENDER)
    #
    #     items = [(h.near, h.names[0]) for h in hits]
    #     items.sort(key=lambda i: i[0])
    #     return [self._itemNames[i[1]] for i in items]

    def paintGL(self, region=None, viewport=None, useItemNames=False):
        """
        viewport specifies the arguments to glViewport. If None, then we use self.opts['viewport']
        region specifies the sub-region of self.opts['viewport'] that should be rendered.
        Note that we may use viewport != self.opts['viewport'] when exporting.
        """
        if viewport is None:
            glViewport(*self.getViewport())
        else:
            glViewport(*viewport)

        bgcolor = self.props.background_color
        glClearColor(*bgcolor)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        self.drawItemTree(useItemNames=useItemNames)

        self.frame_count += 1
        fps = self.frame_count / (self.frame_time.elapsed() / 1000.0)
        if CONFIG.debug:
            _log.debug("FPS: {}".format(fps))

    def drawItemTree(self, item=None, useItemNames=False):
        """

        :param item:
        :param useItemNames:
        :return:
        """
        if item is None:
            items = [x for x in self.items if x.parentItem() is None]
        else:
            items = item.childItems()
            items.append(item)

        for i in items:
            if not i.visible():
                continue
            if i is item:
                try:
                    glPushAttrib(GL_ALL_ATTRIB_BITS)
                    if useItemNames:
                        glLoadName(i._id)
                        self._itemNames[i._id] = i
                    i.paint()
                except GLError as ex:
                    _log.info("Error while drawing items: {}".format(ex))

                    if CONFIG.debug:
                        raise
                finally:
                    glPopAttrib()
            else:
                glMatrixMode(GL_MODELVIEW)
                glPushMatrix()
                try:
                    tr = i.transform()
                    a = np.array(tr.copyDataTo()).reshape((4, 4))
                    glMultMatrixf(a.transpose())
                    self.drawItemTree(i, useItemNames=useItemNames)
                finally:
                    glMatrixMode(GL_MODELVIEW)
                    glPopMatrix()

    def setCameraPosition(self, distance=None, elevation=None, azimuth=None):
        """ Sets the camera parameters.

        :param distance: distance to (0,0,0)
        :param elevation: elevation angle
        :param azimuth: azimuth angle
        """
        if distance is not None:
            self.props.distance = distance
        if elevation is not None:
            self.props.elevation_angle = elevation
        if azimuth is not None:
            self.props.azimuth_angle = azimuth

        self.camera_update()

    def cameraPosition(self):
        """Return current position of camera based on center, dist, elevation, and azimuth"""
        center = self.props.center
        dist = self.props.distance
        elev = self.props.elevation_angle * np.pi / 180.0
        azim = self.props.azimuth_angle * np.pi / 180.0

        pos = Vector3d(
            center.x + dist * np.cos(elev) * np.cos(azim),
            center.y + dist * np.cos(elev) * np.sin(azim),
            center.z + dist * np.sin(elev),
        )

        return pos

    def orbit(self, azim, elev):
        """Orbits the camera around the center position. *azim* and *elev* are given in degrees."""
        self.props.azimuth_angle += azim
        self.props.elevation_angle = np.clip(self.props.elevation_angle + elev, -90, 90)
        # self.update()
        self.camera_update()

    def pan(self, dx, dy, dz, relative=False):
        """
        Moves the center (look-at) position while holding the camera in place.

        If relative=True, then the coordinates are interpreted such that x
        if in the global xy plane and points to the right side of the view, y is
        in the global xy plane and orthogonal to x, and z points in the global z
        direction. Distances are scaled roughly such that a value of 1.0 moves
        by one pixel on screen.

        """
        if not relative:
            self.props.center += QVector3D(dx, dy, dz)
        else:
            cPos = self.cameraPosition()
            cVec = self.props.center - cPos
            dist = np.linalg.norm(cVec)

            xDist = (
                dist * 2.0 * np.tan(0.5 * self.props.fov * np.pi / 180.0)
            )  ## approx. width of view at distance of center point
            xScale = xDist / self.width()
            # zVec = QVector3D(0, 0, 1)
            # xVec = QVector3D.crossProduct(zVec, cVec).normalized()
            # yVec = QVector3D.crossProduct(xVec, zVec).normalized()

            zVec = Vector3d(0, 0, 1)
            xVec = np.cross(zVec, cVec)
            xVec /= np.linalg.norm(xVec)
            yVec = np.cross(xVec, zVec)
            yVec /= np.linalg.norm(yVec)

            self.props.center = (
                self.props.center
                + xVec * xScale * dx
                + yVec * xScale * dy
                + zVec * xScale * dz
            )

        self.camera_update()

    def pixelSize(self, pos):
        """
        Return the approximate size of a screen pixel at the location pos
        Pos may be a Vector or an (N,3) array of locations
        """
        cam = self.cameraPosition()
        if isinstance(pos, np.ndarray):
            cam = np.array(cam).reshape((1,) * (pos.ndim - 1) + (3,))
            dist = ((pos - cam) ** 2).sum(axis=-1) ** 0.5
        else:
            dist = (pos - cam).length()
        xDist = dist * 2.0 * np.tan(0.5 * self.props.fov * np.pi / 180.0)
        return xDist / self.width()

    def mousePressEvent(self, ev):
        self._mousePos = ev.pos()

    def mouseMoveEvent(self, ev):
        """ Mouse move event handler

        :param ev:
        """
        diff = ev.pos() - self._mousePos
        self._mousePos = ev.pos()

        if ev.buttons() == Qt.LeftButton:
            self.orbit(-diff.x(), diff.y())
            # print self.opts['azimuth'], self.opts['elevation']
        elif ev.buttons() == Qt.MidButton:
            if ev.modifiers() & Qt.ControlModifier:
                self.pan(diff.x(), 0, diff.y(), relative=True)
            else:
                self.pan(-diff.x(), -diff.y(), 0, relative=True)

    def wheelEvent(self, ev):
        """

        :param ev:
        :return:
        """
        delta = ev.angleDelta()

        if ev.modifiers() & Qt.ControlModifier:
            self.props.fov *= 0.999 ** (delta.y() / 1.0)
        else:
            self.props.distance *= 0.999 ** (delta.y() / 1.0)

        self.camera_update()

    def camera_update(self):
        """ Applies the updated camera view position and angles.
        """
        self.setProjection()
        self.setModelview()
        self.update()

    def keyReleaseEvent(self, ev):
        """ Overrides key release to plug-in default view shortcuts

        :param ev: Key press event
        """
        if ev.key() == Qt.Key_1:
            self.setCameraPosition(elevation=90, azimuth=-90)
        elif ev.key() == Qt.Key_2:
            self.setCameraPosition(elevation=0, azimuth=-90)
        elif ev.key() == Qt.Key_3:
            self.setCameraPosition(elevation=0, azimuth=0)

        elif ev.key() == Qt.Key_4:
            self.setCameraPosition(elevation=21, azimuth=-161)

        elif ev.key() == Qt.Key_C:
            if self.cam_ctrl.isVisible():
                self.cam_ctrl.close()
            else:
                self.cam_ctrl.show()
