#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart01
-------


"""
import os
import signal
import sys
import numpy as np
from qtpy.QtGui import QBrush, QColor
from qtpy.QtCore import QRectF, QPointF, Qt
from qtpy.QtGui import QPainter, QPolygonF
from qtpy.QtWidgets import QStyleOptionGraphicsItem
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication
import logging

from qplotutils.chart.utils import makePen, makeBrush

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)


from qplotutils import Configuration
from qplotutils.chart.view import ChartView
from qplotutils.chart.items import LineChartItem, ChartItem

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger("Poly example")
_log.setLevel(logging.INFO)

class PolyItem(ChartItem):

    def __init__(self, coords, parent=None):
        super(PolyItem, self).__init__(parent=parent)
        self.coords = coords

        points = [QPointF(x,y) for x, y in coords]
        self._poly = QPolygonF(points)

        self._color = QColor(109, 196, 45, 120)

    def boundingRect(self):
        return self._poly.boundingRect()

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        p.setPen(makePen(Qt.red))
        p.setBrush(makeBrush(self.color))
        p.drawPolygon(self._poly)




if __name__ == "__main__":
    """ Minimal example showing a bench with 2 docks.
    The docks can be resized and dragged around.
    """

    cfg = Configuration()
    cfg.debug = False

    def sigint_handler(signum, frame):
        """ Install handler for the SIGINT signal. To kill app through shell.

        :param signum:
        :param frame:
        :return:
        """
        # sys.stderr.write('\r')
        QApplication.exit()

    signal.signal(signal.SIGINT, sigint_handler)

    qapp = QApplication([])

    # call the python loop periodically to catch interrupts from shell
    timer = QTimer()
    timer.start(1000)
    timer.timeout.connect(lambda: None)

    view = ChartView(orientation=ChartView.AUTOSAR)
    view.resize(400, 1000)


    d = [
        [0,0]
    ]
    fan_angles = np.linspace(60, -60, 120/5, endpoint=True)
    fan_ranges = np.random.randint(15, 150, fan_angles.size)
    for angle_left, angle_right, range_ in zip(fan_angles[:-1], fan_angles[1:], fan_ranges[:-1]):
        print(angle_left, angle_right, range_)
        x = np.cos(angle_left * np.pi / 180) * range_
        y = np.sin(angle_left * np.pi / 180) * range_
        d.append([x, y])
        x = np.cos(angle_right * np.pi / 180) * range_
        y = np.sin(angle_right * np.pi / 180) * range_
        d.append([x, y])



    pi = PolyItem(
        d
    )
    view.addItem(pi)

    view.setAspectRatio(1)
    view.setRange(QRectF(-5, -40, 170, 80))

    # view.autoRange()
    view.show()
    qapp.exec_()
