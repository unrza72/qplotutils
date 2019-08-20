#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==================================
Test for qplotutils.wireframe.view
==================================



Autogenerated package stub.
"""
import pytest
from pytestqt.qtbot import QtBot
import logging
import sys
import os
import numpy as np

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtOpenGL import *
from qtpy.QtWidgets import *

from qplotutils.bench import Bench, Dock
from qplotutils.wireframe.items import CoordinateCross, Grid, MeshItem, Mesh
from qplotutils.wireframe.view import *

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

DELAY = 50

_log = logging.getLogger(__name__)
_log.setLevel(level=logging.WARNING)


@pytest.fixture()
def chartwidget3d(qtbot: QtBot):
    w = ChartView3d()
    w.props.distance = 5
    w.resize(800, 800)
    qtbot.addWidget(w)
    w.show()

    cc = CoordinateCross()
    w.addItem(cc)

    grid = Grid(20)
    w.addItem(grid)

    return w


class TestChartView3d(object):
    def test_show_item(self, chartwidget3d: ChartView3d, qtbot: QtBot):
        b = MeshItem(Mesh.cube(2), shader="shaded")
        b.translate(2, 2, 0)
        chartwidget3d.addItem(b)

        qtbot.wait(DELAY)
        assert len(chartwidget3d.items) == 3

    def test_show_check_props(self, chartwidget3d: ChartView3d, qtbot: QtBot):
        for k in range(20):
            chartwidget3d.props.azimuth_angle += 2
            qtbot.wait(5)

        for k in range(20):
            chartwidget3d.props.elevation_angle += 2
            qtbot.wait(5)

        for k in range(20):
            chartwidget3d.props.distance += 2
            qtbot.wait(5)

        qtbot.wait(DELAY)

    def test_azimuth_w_mouse(
        self, chartwidget3d: ChartView3d, qapp: QApplication, qtbot: QtBot
    ):

        p = QPointF(400, 200)
        qtbot.mousePress(chartwidget3d, Qt.LeftButton, pos=p.toPoint())

        # leftclick move in x direction is on azimuth
        move_right = np.ones((10), np.int) * 6
        move_left = -1 * move_right

        move = np.concatenate((move_right, move_left))

        for delta in move:
            az = chartwidget3d.props.azimuth_angle
            el = chartwidget3d.props.elevation_angle

            p.setX(p.x() + delta)
            _log.debug("move to {},{}".format(p.x(), p.y()))

            # Workaround: bug in QTest lib. See: https://bugreports.qt.io/browse/QTBUG-5232
            event = QMouseEvent(
                QEvent.MouseMove, p, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier
            )
            qapp.sendEvent(chartwidget3d, event)

            qtbot.wait(2)

            assert az != chartwidget3d.props.azimuth_angle
            assert el == chartwidget3d.props.elevation_angle

        qtbot.mouseRelease(chartwidget3d, Qt.LeftButton, pos=p.toPoint())
        qtbot.wait(200)

    def test_pan(self, chartwidget3d: ChartView3d, qapp: QApplication, qtbot: QtBot):

        p = QPointF(400, 200)
        qtbot.mousePress(chartwidget3d, Qt.LeftButton, pos=p.toPoint())

        # leftclick move in x direction is on azimuth
        move_right = np.ones((10), np.int) * 6
        move_left = -1 * move_right

        move = np.concatenate((move_right, move_left))

        qtbot.wait(200)

        for delta in move:
            # az = chartwidget3d.props.azimuth_angle
            # el = chartwidget3d.props.elevation_angle

            p.setX(p.x() + delta)
            _log.debug("move to {},{}".format(p.x(), p.y()))

            # Workaround: bug in QTest lib. See: https://bugreports.qt.io/browse/QTBUG-5232
            event = QMouseEvent(
                QEvent.MouseMove, p, Qt.MiddleButton, Qt.MiddleButton, Qt.NoModifier
            )
            qapp.sendEvent(chartwidget3d, event)

            qtbot.wait(20)

            # assert az != chartwidget3d.props.azimuth_angle
            # assert el == chartwidget3d.props.elevation_angle

        qtbot.mouseRelease(chartwidget3d, Qt.LeftButton, pos=p.toPoint())
        qtbot.wait(200)

    def test_zoom(self, chartwidget3d: ChartView3d, qapp: QApplication, qtbot: QtBot):

        p = QPointF(400, 200)
        qtbot.mousePress(chartwidget3d, Qt.LeftButton, pos=p.toPoint())

        # leftclick move in x direction is on azimuth
        move_right = np.ones((10), np.int) * 6
        move_left = -1 * move_right

        move = np.concatenate((move_right, move_left))

        qtbot.wait(DELAY)

        for delta in move:
            # az = chartwidget3d.props.azimuth_angle
            # el = chartwidget3d.props.elevation_angle

            p.setX(p.x() + delta)
            _log.debug("move to {},{}".format(p.x(), p.y()))

            # Workaround: bug in QTest lib. See: https://bugreports.qt.io/browse/QTBUG-5232
            event = QMouseEvent(
                QEvent.MouseMove, p, Qt.MiddleButton, Qt.MiddleButton, Qt.NoModifier
            )
            qapp.sendEvent(chartwidget3d, event)

            qtbot.wait(DELAY)

            # assert az != chartwidget3d.props.azimuth_angle
            # assert el == chartwidget3d.props.elevation_angle

        qtbot.mouseRelease(chartwidget3d, Qt.LeftButton, pos=p.toPoint())
        qtbot.wait(DELAY)

    # def test_show_all(self, chartwidget3d: ChartView3d,  qapp : QApplication, qtbot: QtBot):
    #
    #
    #     p = QPointF(400, 400)
    #     qtbot.mousePress(w, Qt.LeftButton, pos=p.toPoint())
    #
    #     # leftclick move in x direction is on azimuth
    #     for k in range(10):
    #         az = w.props.azimuth_angle
    #         el = w.props.elevation_angle
    #
    #
    #
    #         p.setX(p.x() + 10)
    #         _log.debug("move to {},{}".format(p.x(), p.y()))
    #
    #         # Workaround: bug in QTest lib. See: https://bugreports.qt.io/browse/QTBUG-5232
    #         event = QMouseEvent(QEvent.MouseMove, p, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    #         qapp.sendEvent(w, event)
    #
    #         qtbot.wait(20)
    #
    #         assert az != w.props.azimuth_angle
    #         assert el == w.props.elevation_angle
    #
    #     # leftclick move in y direction is on elevation
    #     for k in range(10):
    #         az = w.props.azimuth_angle
    #         el = w.props.elevation_angle
    #
    #         # elevation max is 90
    #         if el == 90:
    #             break
    #
    #         p.setY(p.y() + 10)
    #         _log.debug("move to {},{}".format(p.x(), p.y()))
    #
    #         # Workaround: bug in QTest lib. See: https://bugreports.qt.io/browse/QTBUG-5232
    #         event = QMouseEvent(QEvent.MouseMove, p, Qt.LeftButton, Qt.LeftButton,
    #                             Qt.NoModifier)
    #         qapp.sendEvent(w, event)
    #
    #         qtbot.wait(20)
    #
    #         assert az == w.props.azimuth_angle
    #         assert el != w.props.elevation_angle
    #
    #     for k in range(20):
    #         az = w.props.azimuth_angle
    #         el = w.props.elevation_angle
    #
    #         # elevation max is 90
    #         if el == -90:
    #             break
    #
    #         p.setY(p.y() - 10)
    #         _log.debug("move to {},{}".format(p.x(), p.y()))
    #
    #         # Workaround: bug in QTest lib. See: https://bugreports.qt.io/browse/QTBUG-5232
    #         event = QMouseEvent(QEvent.MouseMove, p, Qt.LeftButton, Qt.LeftButton,
    #                             Qt.NoModifier)
    #         qapp.sendEvent(w, event)
    #
    #         qtbot.wait(20)
    #
    #         assert az == w.props.azimuth_angle
    #         assert el != w.props.elevation_angle
    #
    #
    #     qtbot.mouseRelease(w, Qt.LeftButton, pos=p.toPoint())
    #     qtbot.wait(1000)

    # def test_addItem(self, qtbot: QtBot):
    #     """ Tests for addItem
    #
    #     """
    #     # Autogenerated test skeleton for addItem
    #     pass
    #
    # def test_cameraPosition(self, qtbot: QtBot):
    #     """ Tests for cameraPosition
    #
    #     """
    #     # Autogenerated test skeleton for cameraPosition
    #     pass
    #
    # def test_camera_update(self, qtbot: QtBot):
    #     """ Tests for camera_update
    #
    #     """
    #     # Autogenerated test skeleton for camera_update
    #     pass
    #
    # def test_drawItemTree(self, qtbot: QtBot):
    #     """ Tests for drawItemTree
    #
    #     """
    #     # Autogenerated test skeleton for drawItemTree
    #     pass
    #
    # def test_getViewport(self, qtbot: QtBot):
    #     """ Tests for getViewport
    #
    #     """
    #     # Autogenerated test skeleton for getViewport
    #     pass
    #
    # def test_initializeGL(self, qtbot: QtBot):
    #     """ Tests for initializeGL
    #
    #     """
    #     # Autogenerated test skeleton for initializeGL
    #     pass
    #
    # def test_keyReleaseEvent(self, qtbot: QtBot):
    #     """ Tests for keyReleaseEvent
    #
    #     """
    #     # Autogenerated test skeleton for keyReleaseEvent
    #     pass
    #
    # def test_mouseMoveEvent(self, qtbot: QtBot):
    #     """ Tests for mouseMoveEvent
    #
    #     """
    #     # Autogenerated test skeleton for mouseMoveEvent
    #     pass
    #
    # def test_mousePressEvent(self, qtbot: QtBot):
    #     """ Tests for mousePressEvent
    #
    #     """
    #     # Autogenerated test skeleton for mousePressEvent
    #     pass
    #
    # def test_orbit(self, qtbot: QtBot):
    #     """ Tests for orbit
    #
    #     """
    #     # Autogenerated test skeleton for orbit
    #     pass
    #
    # def test_paintGL(self, qtbot: QtBot):
    #     """ Tests for paintGL
    #
    #     """
    #     # Autogenerated test skeleton for paintGL
    #     pass
    #
    # def test_pan(self, qtbot: QtBot):
    #     """ Tests for pan
    #
    #     """
    #     # Autogenerated test skeleton for pan
    #     pass
    #
    # def test_pixelSize(self, qtbot: QtBot):
    #     """ Tests for pixelSize
    #
    #     """
    #     # Autogenerated test skeleton for pixelSize
    #     pass
    #
    # def test_projectionMatrix(self, qtbot: QtBot):
    #     """ Tests for projectionMatrix
    #
    #     """
    #     # Autogenerated test skeleton for projectionMatrix
    #     pass
    #
    # def test_removeItem(self, qtbot: QtBot):
    #     """ Tests for removeItem
    #
    #     """
    #     # Autogenerated test skeleton for removeItem
    #     pass
    #
    # def test_resizeGL(self, qtbot: QtBot):
    #     """ Tests for resizeGL
    #
    #     """
    #     # Autogenerated test skeleton for resizeGL
    #     pass
    #
    # def test_setCameraPosition(self, qtbot: QtBot):
    #     """ Tests for setCameraPosition
    #
    #     """
    #     # Autogenerated test skeleton for setCameraPosition
    #     pass
    #
    # def test_setModelview(self, qtbot: QtBot):
    #     """ Tests for setModelview
    #
    #     """
    #     # Autogenerated test skeleton for setModelview
    #     pass
    #
    # def test_setProjection(self, qtbot: QtBot):
    #     """ Tests for setProjection
    #
    #     """
    #     # Autogenerated test skeleton for setProjection
    #     pass
    #
    # def test_viewMatrix(self, qtbot: QtBot):
    #     """ Tests for viewMatrix
    #
    #     """
    #     # Autogenerated test skeleton for viewMatrix
    #     pass
    #
    # def test_wheelEvent(self, qtbot: QtBot):
    #     """ Tests for wheelEvent
    #
    #     """
    #     # Autogenerated test skeleton for wheelEvent
    #     pass


class TestViewProperties(object):
    def test_azimuth_angle(self, qtbot: QtBot):
        """ Tests for azimuth_angle

        """
        # Autogenerated test skeleton for azimuth_angle
        pass

    def test_center(self, qtbot: QtBot):
        """ Tests for center

        """
        # Autogenerated test skeleton for center
        pass

    def test_distance(self, qtbot: QtBot):
        """ Tests for distance

        """
        # Autogenerated test skeleton for distance
        pass

    def test_elevation_angle(self, qtbot: QtBot):
        """ Tests for elevation_angle

        """
        # Autogenerated test skeleton for elevation_angle
        pass

    def test_fov(self, qtbot: QtBot):
        """ Tests for fov

        """
        # Autogenerated test skeleton for fov
        pass
