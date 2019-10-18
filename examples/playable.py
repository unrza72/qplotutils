#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playable Example
----------------

Simple visualization example


"""
import logging
import os
import signal
import sys

import numpy as np
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from qtpy.QtCore import QPointF
from qtpy.QtGui import QPicture, QPen, QBrush
from qtpy.QtCore import QTimer
from qtpy.QtCore import Qt, QRectF
from qtpy.QtGui import QColor, QPainter, QPainterPath
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import (
    QStyleOptionGraphicsItem,
)
from shapely.geometry import Polygon

from qplotutils.player import PlaybackWidget

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.bench import Bench, Placement, Dock

from qplotutils.chart.utils import makePen
from qplotutils import Configuration, CONFIG
from qplotutils.chart.view import ChartView
from qplotutils.chart.items import LineChartItem, ChartItem


np.random.seed(42)

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

#: Module level logger
_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)

_cfg = CONFIG


class SignalDock(Dock):
    def __init__(self, title="OSCI", orientation=ChartView.CARTESIAN):
        super(SignalDock, self).__init__(title)

        self.view = ChartView(orientation=orientation)
        self.addWidget(self.view)

    def receiveTime(self, e):
        self.timeline.setX(e.position.x())



class PlayerExample(QMainWindow):

    def __init__(self):
        super().__init__()

        self._w = QWidget()
        self._l = QVBoxLayout()
        self._w.setLayout(self._l)

        self.bench = Bench()

        self.dock_01 = SignalDock("Birdseye", ChartView.AUTOSAR)
        self.bi = self.dock_01.view
        self.bi.setAspectRatio(1)
        self.bench.addDock(self.dock_01)

        self.player = PlaybackWidget()

        self._l.addWidget(self.bench)
        self._l.addWidget(self.player)

        self.setCentralWidget(self._w)


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

    # Creating the bench
    pe = PlayerExample()

    pe.show()
    qapp.exec_()