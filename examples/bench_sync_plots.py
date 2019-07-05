#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synchronized Timeline
---------------------

Bench with docks that have a view with synced timelines
"""
import os
import signal
import sys
import numpy as np
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication


PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.chart.interactive import InteractiveVerticalLine
from qplotutils.chart.items import LineChartItem
from qplotutils.chart.view import ChartView
from qplotutils.bench import Dock, Bench


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"


class SignalDock(Dock):

    def __init__(self, title="OSCI"):
        super(SignalDock, self).__init__(title)

        self.view = ChartView(orientation=ChartView.CARTESIAN)
        self.addWidget(self.view)

        self.timeline = InteractiveVerticalLine()
        self.view.addItem(self.timeline)

    def receiveTime(self, e):
        self.timeline.setX(e.position.x())


if __name__ == "__main__":
    """ Minimal example showing a bench with 2 docks.
    The docks can be resized and dragged around.
    """


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
    bench = Bench()
    bench.resize(800, 900)

    # First dock
    dock_01 = SignalDock("OSCI 1")
    bench.addDock(dock_01)

    # Second dock
    dock_02 = SignalDock("OSCI 2")
    bench.addDock(dock_02)

    bench.setWindowTitle("Bench Example 01")
    bench.show()

    l = LineChartItem()
    x = np.arange(-30, 300, 0.2, dtype=np.float)
    y = np.sin(2 * np.pi * 3 / float(max(x) - min(x)) * x)
    l.plot(y, x, "a sine")
    dock_01.view.addItem(l)
    dock_01.view.autoRange()

    l = LineChartItem()
    x = np.arange(-30, 300, 0.2, dtype=np.float)
    y = np.cos(2 * np.pi * 3 / float(max(x) - min(x)) * x)
    l.plot(y, x, "a cosine")
    dock_02.view.addItem(l)
    dock_02.view.autoRange()

    # weave timestamps
    dock_01.timeline.positionChange.connect(dock_02.receiveTime)
    dock_02.timeline.positionChange.connect(dock_01.receiveTime)

    dock_01.timeline.setX(12)

    qapp.exec_()

