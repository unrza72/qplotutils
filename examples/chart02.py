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
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication


PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.chart.view import ChartView
from qplotutils.chart.items import LineChartItem, HLine, VLine

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"


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

    view = ChartView(orientation=ChartView.CARTESIAN)
    view.resize(800, 400)
    view.show()

    # A line chart_tests item (again)
    l = LineChartItem()
    x = np.arange(-30, 300, 0.2, dtype=np.float)
    y = np.sin(2 * np.pi * 3 / float(max(x) - min(x)) * x)
    l.plot(y, x, "a sine")

    view.addItem(l)
    view.autoRange()

    # Add a horizontal line
    h = HLine()
    h.setY(0.1, "A Hline", QColor(Qt.green))
    view.addItem(h)

    # Add a vertical line
    v = VLine()
    v.setX(12, "A Vline", QColor(Qt.yellow))
    view.addItem(v)

    # Set legend visible
    view.setLegendVisible(True, ChartView.BOTTOM_RIGHT)

    qapp.exec_()