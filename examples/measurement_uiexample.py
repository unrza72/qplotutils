#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wire frame
----------



"""
import os
import sys
import logging
import signal
import numpy as np

from qtpy.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QVBoxLayout
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils import CONFIG
from qplotutils.bench import Bench, Dock, Placement
from qplotutils.chart.items import LineChartItem
from qplotutils.chart.view import ChartView
from qplotutils.player import PlaybackWidget
from qplotutils.wireframe.items import Box, CoordinateCross, Grid, MeshItem, Mesh
from qplotutils.wireframe.view import ChartView3d


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"


_log = logging.getLogger(__name__)

class UiExample(QMainWindow):
    def __init__(self, parent=None):
        super(UiExample, self).__init__()

        self.setCentralWidget(QWidget())
        l = QVBoxLayout()
        self.centralWidget().setLayout(l)

        self.bench = Bench()
        self.player = PlaybackWidget()
        l.addWidget(self.bench)
        l.addWidget(self.player)

        dock_1 = Dock("GL Dock")
        # dock_ctrl = Dock("Controls")

        w = ChartView3d()
        # w.cam_ctrl.setHidden(True)
        w.props.distance = 5
        dock_1.addWidget(w)
        # dock_ctrl.addWidget(w.cam_ctrl)

        dock_2 = Dock("Signals")

        c = ChartView()
        dock_2.addWidget(c)

        # A line chart_tests item (again)
        l = LineChartItem()
        x = np.arange(-30, 300, 0.2, dtype=np.float)
        y = np.sin(2 * np.pi * 3 / float(max(x) - min(x)) * x)
        l.plot(y, x, "a sine")

        c.addItem(l)
        c.autoRange()

        self.bench.addDock(dock_1)
        # bench.addDock(dock_ctrl, Placement.RIGHT, ref=dock_1)
        self.bench.addDock(dock_2, Placement.LEFT, ref=dock_1)

        cc = CoordinateCross()
        w.addItem(cc)

        grid = Grid(20)
        w.addItem(grid)

        b = MeshItem(Mesh.cube(2), shader="shaded")
        b.translate(2, 2, 0)
        w.addItem(b)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    CONFIG.debug_layout = False

    def sigint_handler(signum, frame):
        """ Install handler for the SIGINT signal. To kill app through shell.

        :param signum:
        :param frame:
        :return:
        """
        QApplication.exit()

    signal.signal(signal.SIGINT, sigint_handler)
    qapp = QApplication([])

    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    uie = UiExample()
    uie.show()
    uie.resize(1000, 800)
    # bench.resize(800, 800)
    # bench.show()
    #
    # if False and os.path.exists("meas_ui.json"):
    #     bench.loadLayout("meas_ui.json")
    # else:
    #
    #     dock_1 = Dock("GL Dock")
    #     # dock_ctrl = Dock("Controls")
    #
    #     w = ChartView3d()
    #     # w.cam_ctrl.setHidden(True)
    #     w.props.distance = 5
    #     dock_1.addWidget(w)
    #     # dock_ctrl.addWidget(w.cam_ctrl)
    #
    #     dock_2 = Dock("Signals")
    #
    #     c = ChartView()
    #     dock_2.addWidget(c)
    #
    #     # A line chart_tests item (again)
    #     l = LineChartItem()
    #     x = np.arange(-30, 300, 0.2, dtype=np.float)
    #     y = np.sin(2 * np.pi * 3 / float(max(x) - min(x)) * x)
    #     l.plot(y, x, "a sine")
    #
    #     c.addItem(l)
    #     c.autoRange()
    #
    #     bench.addDock(dock_1)
    #     # bench.addDock(dock_ctrl, Placement.RIGHT, ref=dock_1)
    #     bench.addDock(dock_2, Placement.LEFT, ref=dock_1)
    #
    #     cc = CoordinateCross()
    #     w.addItem(cc)
    #
    #     grid = Grid(20)
    #     w.addItem(grid)
    #
    #     b = MeshItem(Mesh.cube(2), shader="shaded")
    #     b.translate(2, 2, 0)
    #     w.addItem(b)

    qapp.exec_()
    # bench.saveLayout("meas_ui.json")
