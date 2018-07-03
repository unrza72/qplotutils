#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__TODO__


"""
import random

import logging
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

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


class ScatterItem(ChartItem):

    def __init__(self, x, y, z=None, parent=None):
        super(ScatterItem, self).__init__(parent)
        self.setFlags(self.flags() | QGraphicsItem.ItemIgnoresTransformations)
        self.chartItemFlags = ChartItemFlags.FLAG_NO_LABEL

        self.x = x
        self.y = y
        self.z = z

        self.w = 6

        self._bRect = QRectF(-self.w, -self.w, 2*self.w, 2*self.w)

        self.normalize = Normalize(0,1)
        self.colormap = Colormap()

        self.setPos(self.x, self.y)

        self._picture = None

        # self._updatePicture()


    # def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
    #
    #     a = self.colormap(self.normalize(self.z))
    #
    #     color = QColor.fromRgbF(a[0], a[1], a[2])
    #
    #     p.setPen(QPen(color))
    #     p.setBrush(QBrush(color))
    #     # p.drawRect(self.b_rect)
    #     p.drawEllipse(0,0,self.w,self.w)


    def _updatePicture(self):
        self._picture = QPicture()
        painter = QPainter(self._picture)
        self._generatePicture(painter)
        painter.end()

    def _generatePicture(self, p=QPainter()):
        a = self.colormap(self.normalize(self.z))

        color = QColor.fromRgbF(a[0], a[1], a[2])

        p.setPen(QPen(color))
        p.setBrush(QBrush(color))
        # p.drawRect(self.b_rect)
        p.drawEllipse(0, 0, self.w, self.w)

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



# stolen from MPL, lets build up on that for compat
# TODO: alpha channel
_autumn_data = {'red':   ((0., 1.0, 1.0), (1.0, 1.0, 1.0)),
                'green': ((0., 0., 0.), (1.0, 1.0, 1.0)),
                'blue':  ((0., 0., 0.), (1.0, 0., 0.))}

_test_data = {'red': (
        (0., .0, .0),
        (0.5, 1.0, 1.0),
        (1.0, .0, 0.0)
    ),
    'green': (
        (0., 0., 0.),
        (1.0, 1.0, 1.0)
    ),
    'blue': (
        (0., 0., 0.),
        (1.0, 0., 0.)
    )
}




class Colormap(object):

    N = 256  # LUT default size

    def __init__(self, data=_autumn_data):

        self.lut = np.zeros((self.N,3), dtype=np.float)

        self.__build_lut(data)

    def __build_lut(self, data):
        r = self.__channel_gradient(data["red"])
        g = self.__channel_gradient(data["green"])
        b = self.__channel_gradient(data["blue"])

        self.lut[:,0] = r
        self.lut[:,1] = g
        self.lut[:,2] = b

    def __channel_gradient(self, d):
        c = np.zeros(self.N, dtype=np.float)

        for l, r in zip(d[0:-1], d[1:]):
            l_idx = self.lut_index(l[0])
            l_sv = l[1]
            l_v = l[2]

            r_idx = self.lut_index(r[0])
            r_v = r[1]
            r_ev = r[2]

            c[l_idx:r_idx] = l_sv + (r_v - l_v) / (r_idx - l_idx * 1.0) * np.arange(0, r_idx - l_idx)
            c[r_idx] = r_ev

        return c

    @classmethod
    def lut_index(cls, v):
        if not 0 <= 0 <= 1:
            raise Exception("Value not normalized")
        return int(np.round(v * (cls.N - 1), 0))

    def __call__(self, v):
        idx = self.lut_index(v)
        return self.lut[idx,:]

class Normalize(object):

    def __init__(self, value_min, value_max, lower_bound=0.0, upper_bound=1.0):
        self.value_min = value_min
        self.value_max = value_max

    def __call__(self, values, dtype=np.float32):
        # if not self.value_min <= values <= self.value_max:
        #     return np.NaN  # Colormap can decide to what to do with these values
        out_of_bounds_greater = np.ma.masked_greater(values, self.value_max)
        out_of_bounds_less = np.ma.masked_less(values, self.value_min)

        invalids = np.logical_or(np.ma.getmask(out_of_bounds_less),
                                 np.ma.getmask(out_of_bounds_greater))

        valid = np.ma.array(values, mask=invalids,
                             dtype=dtype, copy=True)

        result = (valid - self.value_min) / (self.value_max - self.value_min * 1.0)
        return result


class Colorbar(ChartItem):

    def __init__(self, colormap, v_min, v_max, parent=None):
        """ Displays the chart item in a legend table. """
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

    # def addEntry(self, chart_item):
    #     """ Slot. Adds an entry for the given chart item to the legend.
    #
    #     :param chart_item:
    #     """
    #     _log.debug("Add entry chart item: {}".format(chart_item.label))
    #     self._entries.append(chart_item)
    #
    #     self._updateBoundingRect()
    #     self._updatePicture()
    #
    #     # self.setVisible(True)
    #
    # def removeEntry(self, chart_item):
    #     """ Slot. Removes the entry for the given chart item to the legend.
    #
    #     :param chart_item: chart item such as line chart item, e.g.
    #     """
    #
    #     _log.debug("Remove chart item entry: {}".format(chart_item.label))
    #     self._entries.remove(chart_item)
    #
    #     self._updateBoundingRect()
    #     self._updatePicture()

    # def _updateBoundingRect(self):
    #     metrics = QFontMetrics(self.font)
    #     runWidth = 0
    #
    #     for entry in self._entries:
    #
    #         # (text, color, width, tick) = entry
    #         if entry.label is not None:
    #             w = metrics.width(entry.label)
    #             if w > runWidth:
    #                 runWidth = w
    #
    #     self._bRect.setWidth(runWidth + 40)
    #     self._bRect.setHeight(len(self._entries) * 20 + 8)

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

        # p.setBrush(QBrush(Qt.transparent))
        # p.setPen(QPen(QColor(255, 255, 255, 255)))
        # p.drawLine(QLine(5, 10,30,10))
        # p.drawLine(QLine(5, 100, 30, 100))
        # p.drawLine(QLine(5, 190, 30, 190))

        p.setBrush(QBrush(Qt.transparent))
        p.setPen(QPen(QColor("#FFFFFF")))
        tickRect = QRectF(32, 6, self._bRect.width() - 32, 11)
        p.drawText(tickRect, self.fontFlags, "{}".format(self.v_max))
        tickRect = QRectF(32, 94, self._bRect.width() - 32, 11)
        p.drawText(tickRect, self.fontFlags, "{}".format(self.v_max - (self.v_max - self.v_min) / 2.))
        tickRect = QRectF(32, 184, self._bRect.width() - 32, 11)
        p.drawText(tickRect, self.fontFlags, "{}".format(self.v_min))


        # for k, entry in enumerate(self._entries):
        #     # (text, color, width, tick) = entry
        #
        #     p.setBrush(QBrush(entry.color, Qt.SolidPattern))
        #     p.setPen(QPen(Qt.transparent))
        #
        #     p.drawRect(6, 8 + k * 20, 11, 11)
        #
        #     p.setBrush(QBrush(Qt.transparent))
        #     p.setPen(QPen(QColor("#FFFFFF")))
        #     tickRect = QRectF(24, 8 + k * 20, self._bRect.width() - 24, 11)
        #     p.drawText(tickRect, self.fontFlags, "{}".format(entry.label))

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

    def __del__(self):
        _log.debug("Finalizing: {}".format(self))


class ScatterPlotView(ChartView):
    """ Quickly display scattering data, with support for color maps to

    """

    def __init__(self, colormap, min, max, parent=None):
        super(ScatterPlotView, self).__init__(parent, orientation=ChartView.CARTESIAN)

        self.normalize = Normalize(min, max)
        self.colormap = colormap



    def addItem(self, item=ChartItem()):
        if isinstance(item, ScatterItem):
            #     if item.z < self.normalize.value_min:
            #         self.normalize.value_min = item.z
            #
            #     if item.z > self.normalize.value_max:
            #         self.normalize.value_max = item.z

            item.normalize = self.normalize
            item.colormap = self.colormap
            item._updatePicture()

        super(ScatterPlotView, self).addItem(item)



if __name__ == "__main__":

    qapp = QApplication([])

    cm = Colormap()
    view = ScatterPlotView(cm, 0, 500)

    for k in range(500):
        s = ScatterItem(random.randint(-100, 100), random.randint(-100, 100), k)
        view.addItem(s)

    # l = LineChartItem()
    # x = np.arange(-30, 300, 0.2, dtype=np.float)
    # y = np.sin(2 * np.pi * 3 / float(max(x) - min(x)) * x)
    # l.plot(y, x, "a sine")
    # view.addItem(l)

    view.resize(400,400)
    view.autoRange()
    view.show()
    # view.legend = True

    cb = Colorbar(cm, view.normalize.value_min, view.normalize.value_max)
    view.scene().addItem(cb)
    parent_w = view.size().width()
    parent_h = view.size().height()
    cb.setPos(parent_w - cb.boundingRect().width() - 10, 10)
    cb.setVisible(True)






    qapp.exec_()
