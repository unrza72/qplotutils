#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__TODO__


"""
import random

import logging
import numpy as np
import weakref


from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtOpenGL import *
from qtpy.QtWidgets import *

from qplotutils.chart import color
from qplotutils.chart.color import Normalize, Colormap
from qplotutils.chart.items import ChartItem, ChartItemFlags, LineChartItem
from qplotutils.chart.view import ChartView

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015, 2017, 2018, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)



# def _map_to_color(v):
#     return QColor(Qt.white)


class ScatterItem(ChartItem):

    def __init__(self, x, y, z=None, parent=None):
        super(ScatterItem, self).__init__(parent)
        self.setFlags(self.flags() | QGraphicsItem.ItemIgnoresTransformations)
        self.chartItemFlags = ChartItemFlags.FLAG_NO_LABEL

        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

        self.x = x
        self.y = y
        self.z = z

        self.w = 6

        self._bRect = QRectF(-self.w, -self.w, 2*self.w, 2*self.w)
        self.setPos(self.x, self.y)

        self._picture = None

        self.color_assignment_callback = lambda v: QColor(Qt.white)


    def updatePicture(self):
        self._picture = QPicture()
        p = QPainter(self._picture)
        # self._generatePicture(painter)
        # painter.end()

        # def _generatePicture(self, p=QPainter()):
        #     a = self.colormap(self.normalize(self.z))
        #     color = QColor.fromRgbF(a[0], a[1], a[2], a[3])
        color = self.color_assignment_callback(self.z)

        p.setPen(QPen(color))
        p.setBrush(QBrush(color))
        # p.drawRect(self.b_rect)
        p.drawEllipse(QPointF(0, 0), self.w, self.w)

        # self._generatePicture(painter)
        p.end()

    def boundingRect(self):
        return self._bRect

    def shape(self):
        path = QPainterPath()
        path.addRect(self._bRect)
        return path

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        if self._picture is None:
            return
        self._picture.play(p)



class Colorbar(ChartItem):

    def __init__(self, colormap, v_min, v_max, parent=None):
        """ Displays the chart_tests item in a legend table. """
        super(Colorbar, self).__init__()  # Pycharm / pyLint inspection error. Please ignore
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIgnoresTransformations)
        self.chartItemFlags = ChartItemFlags.FLAG_NO_LABEL


        self._picture = None
        self._bRect = QRectF(0, 0, 200, 200)

        self.cm = colormap
        self.v_min = v_min
        self.v_max = v_max

        self.font = QFont("Helvetica [Cronyx]", 10, QFont.Normal)
        self.fontFlags = Qt.TextDontClip | Qt.AlignLeft | Qt.AlignVCenter
        self.setVisible(True)

        metrics = QFontMetrics(self.font)
        runWidth = 0

        for entry in [v_min, v_max]:
            w = metrics.width("{}".format(entry))
            if w > runWidth:
                runWidth = w
        self._bRect.setWidth(runWidth + 60)

        self._updatePicture()

    def _updatePicture(self):
        self._picture = QPicture()
        painter = QPainter(self._picture)
        self._generatePicture(painter)
        painter.end()

    def _generatePicture(self, p=QPainter()):
        p.setPen(QPen(QColor("#aaaaaa")))
        p.setBrush(QBrush(QColor(80, 80, 80, 210), Qt.SolidPattern))
        p.drawRoundedRect(self._bRect, 2, 2)

        for n in range(0, 180, 1):
            v = n / 180.
            a = self.cm(v)
            color = QColor.fromRgbF(a[0], a[1], a[2])

            p.setBrush(QBrush(color))
            p.setPen(QPen(color))
            p.drawRect(QRect(5, 190 - n, 20, -1))

        p.setBrush(QBrush(Qt.transparent))
        p.setPen(QPen(QColor("#FFFFFF")))
        tickRect = QRectF(32, 6, self._bRect.width() - 32, 11)
        p.drawText(tickRect, self.fontFlags, "{}".format(self.v_max))
        # tickRect = QRectF(32, 94, self._bRect.width() - 32, 11)
        # p.drawText(tickRect, self.fontFlags, "{}".format(self.v_max - (self.v_max - self.v_min) / 2.))
        tickRect = QRectF(32, 184, self._bRect.width() - 32, 11)
        p.drawText(tickRect, self.fontFlags, "{}".format(self.v_min))

    def boundingRect(self):
        return self._bRect

    # def shape(self):
    #     path = QPainterPath()
    #     path.addRect(self._bRect)
    #     return path

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        if self._picture is None:
            return
        self._picture.play(p)

    def __del__(self):
        _log.debug("Finalizing: {}".format(self))


class ScatterPlotView(ChartView):
    """ Quickly display scattering data, with support for color maps to

    """

    def __init__(self, colormap, min=None, max=None, parent=None):
        super(ScatterPlotView, self).__init__(parent, orientation=ChartView.CARTESIAN)

        self.setCacheMode(QGraphicsView.CacheBackground)

        self.normalize = Normalize(min, max)
        self.lower_bound_dynamic = min is None
        self.upper_bound_dynamic = max is None

        self.colormap = colormap

        self.cb = Colorbar(colormap, min, max)
        self.add_chart_key(self.cb, ChartView.BOTTOM_LEFT)

        self.scatter_items = []

    def __colormap_callback(self, v):
        a = self.colormap(self.normalize(v))
        color = QColor.fromRgbF(a[0], a[1], a[2], a[3])
        return color

    def addItem(self, item=ChartItem()):
        if self.lower_bound_dynamic or self.upper_bound_dynamic and len(self.scatter_items) > 50:
            _log.warning("Depending on the ordering of your data adding scatter items might be very slow. O(n**2)")
        self.addItems([item])

    def addItems(self, items):
        force_update_all = False
        for item in items:
            if isinstance(item, ScatterItem):
                item.color_assignment_callback = self.__colormap_callback
                r = weakref.ref(item)
                self.scatter_items.append(r)

                if self.normalize.value_min is None or self.lower_bound_dynamic and item.z < self.normalize.value_min:
                    self.normalize.value_min = item.z
                    force_update_all = True

                if self.normalize.value_max is None or self.upper_bound_dynamic and item.z > self.normalize.value_max:
                    self.normalize.value_max = item.z
                    force_update_all = True

            item.updatePicture()
            super(ScatterPlotView, self).addItem(item)

        if force_update_all:
            self.cb.v_min = self.normalize.value_min
            self.cb.v_max = self.normalize.value_max
            self.cb._updatePicture()
            for s in self.scatter_items:
                s().updatePicture()

