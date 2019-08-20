#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qplotutils.chart_tests.roi
--------------------------

Region of interest
"""
import logging

import math
import numpy as np
from qtpy.QtCore import Qt, QPointF, QRectF, QLineF
from qtpy.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath
from qtpy.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem

from qplotutils.common import Vector2
from .items import ChartItem

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


class RoiState(object):
    """ Internal properties of the ROI. """

    def __init__(self):
        self.pos = QPointF(0, 0)

        #: Right extend from the center (assuming an unrotated ROI)
        self.w0 = 1

        #: Left extend from the center (assuming an unrotated ROI)
        self.w1 = 1

        #: Upper extend from the center (assuming an unrotated ROI)
        self.h0 = 1

        #: Lower extend from the center (assuming an unrotated ROI)
        self.h1 = 1

        #: Rotation in radians
        self.rotation = 0


class RectangularRegion(ChartItem):
    """ Rectangular overlay, that (optionally) can be resized by handles.

    TODO:
      * Notification framework
      * Modifiers to allow for more flexible mouse interactions
    """

    def __init__(self, x, y, width=1, height=1, rotation=0, parent=None):
        """ Constructor.

        :param x: Initial x position of ROIs center.
        :param y: Initial y position of ROIs center.
        :param width: Initial width
        :param height: Initial height
        :param rotation: Initial rotation in radians
        :param parent: Optional parent item.
        """
        super(RectangularRegion, self).__init__(parent)

        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsFocusable
            | QGraphicsItem.ItemSendsGeometryChanges
        )

        # self.setHandlesChildEvents(False)
        # self.setFiltersChildEvents(True)
        self.__in_move = False

        self._path = QPainterPath()
        self.pen = QPen(QBrush(QColor(161, 0, 161, 255)), 1.0, Qt.SolidLine)
        self.pen.setCosmetic(True)
        self.brush = QBrush(QColor(255, 255, 255, 40))

        self.state = RoiState()
        self.state.pos = QPointF(x, y)
        self.state.w0 = width
        self.state.w1 = width
        self.state.h0 = height
        self.state.h1 = height

        self.state.rotation = rotation

        self.setPos(self.state.pos)
        self.updatePath()

        self._handles = []

    @property
    def handles(self):
        """ Returns all handles which are attached to the ROI.

        :return: list
        """
        return self._handles

    def addHandle(self, handle):
        """ Adds a handle to the ROI.

        :param handle: Resize or rotate handle
        """
        handle.setParentItem(self)
        # self.addToGroup(handle)
        self.handles.append(handle)
        handle.updatePosition()

    def removeHandle(self, handle):
        """ Removes the given handle from the ROI.

        :param handle: Handle
        :return:
        """
        if handle not in self.handles:
            _log.warning("Handle not part of ROI.")
            return

        self.handles.remove(handle)
        # self.removeFromGroup(handle)
        self.scene().removeItem(handle)

    def boundingRect(self):
        return self._path.boundingRect()

    def updatePath(self):
        p0 = Vector2(self.state.w0, self.state.h0)
        p1 = Vector2(-self.state.w1, self.state.h0)
        p2 = Vector2(-self.state.w1, -self.state.h1)
        p3 = Vector2(self.state.w0, -self.state.h1)

        p0t = p0.rotate(self.state.rotation)
        p1t = p1.rotate(self.state.rotation)
        p2t = p2.rotate(self.state.rotation)
        p3t = p3.rotate(self.state.rotation)

        self._path = QPainterPath()
        self._path.moveTo(p0t.x, p0t.y)
        self._path.lineTo(p1t.x, p1t.y)
        self._path.lineTo(p2t.x, p2t.y)
        self._path.lineTo(p3t.x, p3t.y)
        self._path.closeSubpath()

        self.prepareGeometryChange()

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(self.pen)
        p.setBrush(self.brush)
        p.drawPath(self._path)

        p.setBrush(Qt.transparent)
        p.drawLine(QLineF(-0.5, 0, 0.5, 0))
        p.drawLine(QLineF(0, -0.5, 0, 0.5))
        p.drawEllipse(QPointF(0, 0), 0.25, 0.25)

    def mousePressEvent(self, e):
        # !!!Fucking lesson learned, call super to avoid weird jumps in position!!!
        super(RectangularRegion, self).mousePressEvent(e)
        self.__in_move = True

    def mouseReleaseEvent(self, e):
        super(RectangularRegion, self).mouseReleaseEvent(e)
        self.__in_move = False

    def itemChange(self, change, value):
        # TODO: Currently untestable with QTest / QtBot
        if change == QGraphicsItem.ItemPositionChange and self.__in_move:
            value = self._move(self.pos(), value)
        return super(RectangularRegion, self).itemChange(change, value)

    def _move(self, old_pos, new_pos):
        """ Preforms a roi move.

        :param old_pos:
        :param new_pos:
        :return new pos

        """
        delta = old_pos - new_pos
        _log.debug("Delta: {}".format(delta))

        self.state.pos = new_pos
        value = new_pos

        for handle in self.handles:
            handle.updatePosition()

        return value

    def rotation(self):
        """ Override takes rotation from the state instead of items transformation.

        :return: rotation in degrees
        """
        return self.state.rotation * 180 / np.pi

    def setRotation(self, degree):
        """ Override to propagate rotation to state instead of applying it to the items transform

        :param degree: Rotation in degrees
        """
        self.state.rotation = (degree % 360) * np.pi / 180.0

        for h in self.handles:
            h.updatePosition()

        self.updatePath()


class HandlePosition(object):
    """ Enum with the handle positions. """

    #: Upper border position
    TOP = 1

    #: Right border position
    RIGHT = 2

    #: Lower border position
    BOTTOM = 4

    #: Left border position
    LEFT = 8

    @classmethod
    def to_vec(cls, location):
        """ Returns scaling vector to indicate placement direction.

        :param location:
        :return:
        """
        if 2 ** 0 & location:
            y = 1
        elif 2 ** 2 & location:
            y = -1
        else:
            y = 0

        if 2 ** 1 & location:
            x = 1
        elif 2 ** 3 & location:
            x = -1
        else:
            x = 0

        v = Vector2(x, y)

        return v


class RoiHandle(ChartItem):
    """ Base for all ROI handles. """

    def __init__(self, position=HandlePosition.BOTTOM | HandlePosition.LEFT):
        """ Constructor

        :param parent: parent ROI
        :param position: Placement position.
        """
        super(RoiHandle, self).__init__()
        # self.setParentItem(parent)
        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsFocusable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemIgnoresTransformations
            | QGraphicsItem.ItemSendsGeometryChanges
        )

        self.setAcceptHoverEvents(True)

        self.handle_position = HandlePosition.to_vec(position)
        self._brush = QBrush(QColor(Qt.transparent))

    def __repr__(self):
        return "<RoiHandle>"

    def __del__(self):
        _log.debug("Finalizing: {}".format(self))

    def updatePosition(self):
        state = self.parentItem().state

        if self.handle_position.x > 0:
            x = state.w0
        else:
            x = state.w1

        if self.handle_position.y > 0:
            y = state.h0
        else:
            y = state.h1

        p0 = Vector2(x, y) * self.handle_position
        a = state.rotation
        p0t = p0.rotate(a)
        self.setPos(p0t.qpointF)

    def hoverEnterEvent(self, e):
        self._brush = QBrush(QColor(Qt.white))
        super(RoiHandle, self).hoverEnterEvent(e)

    def hoverLeaveEvent(self, e):
        self._brush = QBrush(QColor(Qt.transparent))
        super(RoiHandle, self).hoverLeaveEvent(e)

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        p.setPen(QPen(QColor(255, 255, 255, 200)))
        p.setBrush(self._brush)


class ResizeHandle(RoiHandle):
    """ Handle for resizing. Depending on the placement either along one axis if placed
    at TOP, BOTTOM, LEFT, RIGHT only, or along two axis if placed TOP | LEFT, ...

    """

    def __init__(self, position=HandlePosition.BOTTOM | HandlePosition.LEFT):
        """ Constructor.

        :param parent: parent ROI
        :param position: Handle position.
        """
        super(ResizeHandle, self).__init__(position)
        self.__in_resize = False
        self._size = 10
        # self.updatePosition()

    def boundingRect(self):
        return QRectF(-self._size / 2, -self._size / 2.0, self._size, self._size)

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        super(ResizeHandle, self).paint(p, o, widget)
        p.drawRect(QRectF(-self._size / 2, -self._size / 2.0, self._size, self._size))

    def mousePressEvent(self, e):
        super(ResizeHandle, self).mousePressEvent(e)
        self.__in_resize = True

    def mouseReleaseEvent(self, e):
        super(ResizeHandle, self).mouseReleaseEvent(e)
        self.__in_resize = False

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.__in_resize:
            # TODO: untestable events cannot be triggered through qtbot
            new_pos = value
            _log.debug("new pos: {}".format(new_pos))
            value = self._resize(new_pos)
        return super(ResizeHandle, self).itemChange(change, value)

    def _resize(self, new_pos):
        # back rotation around the current angle
        state = self.parentItem().state
        a = -state.rotation
        p0t = Vector2.fromQpointF(new_pos).rotate(a)

        result = Vector2(p0t.x, p0t.y)

        # FIXME: McCabe
        if self.handle_position.x > 0 and p0t.x > 0:
            self.parentItem().state.w0 = abs(p0t.x)
        elif self.handle_position.x < 0 and p0t.x < 0:
            self.parentItem().state.w1 = abs(p0t.x)
        else:
            result.x = 0

            # Fast move will be forced to zero.
            if self.handle_position.x > 0:
                self.parentItem().state.w0 = 0
            if self.handle_position.x < 0:
                self.parentItem().state.w1 = 0

        if self.handle_position.y > 0 and p0t.y > 0:
            self.parentItem().state.h0 = abs(p0t.y)
        elif self.handle_position.y < 0 and p0t.y < 0:
            self.parentItem().state.h1 = abs(p0t.y)
        else:
            result.y = 0
            if self.handle_position.y > 0:
                self.parentItem().state.h0 = 0
            if self.handle_position.y < 0:
                self.parentItem().state.h1 = 0

        self.parentItem().updatePath()

        for handle in self.parentItem().handles:
            if handle is not self:
                handle.updatePosition()

        # compute new handle position
        p1t = result.rotate(-a)
        return p1t.qpointF


class RotateHandle(RoiHandle):
    def __init__(self, position=HandlePosition.TOP | HandlePosition.RIGHT):
        super(RotateHandle, self).__init__(position)
        self.__in_rotate = False
        self.handle_radius = 6
        self.__r = QRectF(
            -self.handle_radius,
            -self.handle_radius,
            2 * self.handle_radius,
            2 * self.handle_radius,
        )
        self.last_pos = Vector2(0, 0)
        # self.updatePosition()

    def updatePosition(self):
        super(RotateHandle, self).updatePosition()
        self.last_pos = Vector2.fromQpointF(self.pos())

    def boundingRect(self):
        return self.__r

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        super(RotateHandle, self).paint(p, o, widget)
        p.drawEllipse(self.__r)

    def mousePressEvent(self, e):
        super(RotateHandle, self).mousePressEvent(e)
        self.__in_rotate = True

    def mouseReleaseEvent(self, e):
        super(RotateHandle, self).mouseReleaseEvent(e)
        self.__in_rotate = False
        # self.updatePosition()
        _log.debug("Mouse release")

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.__in_rotate:
            state = self.parentItem().state

            u = self.last_pos
            v = Vector2.fromQpointF(value)  # .toPointF())

            delta = v.angle(u)
            a = state.rotation + delta

            # unrotated position of handle
            if self.handle_position.x > 0:
                x = state.w0
            elif self.handle_position.x < 0:
                x = state.w1
            else:
                x = 0

            if self.handle_position.y > 0:
                y = state.h0
            elif self.handle_position.y < 0:
                y = state.h1
            else:
                y = 0

            p0 = Vector2(x, y)
            p0t = p0.rotate(a)

            # update roi box and other handles
            self.parentItem().updatePath()
            for handle in self.parentItem().handles:
                if handle is not self:
                    handle.updatePosition()

            # update me
            self.last_pos = p0t
            self.parentItem().state.rotation = a
            value = p0t.qpointF

        return super(RotateHandle, self).itemChange(change, value)
