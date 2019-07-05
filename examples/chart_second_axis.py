#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart with two horizontal axes
------------------------------

"""
import os
import signal
import sys
import numpy as np
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication

import logging

from qplotutils import CONFIG

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.chart.view import ChartView, SecondaryHorizontalAxis, SecondaryVerticalAxis
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
    logging.basicConfig(level=logging.DEBUG)


    def sigint_handler(signum, frame):
        """ Install handler for the SIGINT signal. To kill app through shell.

        :param signum:
        :param frame:
        :return:
        """
        # sys.stderr.write('\r')
        QApplication.exit()


    signal.signal(signal.SIGINT, sigint_handler)

    CONFIG.debug_layout = True

    qapp = QApplication([])

    # call the python loop periodically to catch interrupts from shell
    timer = QTimer()
    timer.start(1000)
    timer.timeout.connect(lambda: None)

    view = ChartView(orientation=ChartView.CARTESIAN)
    view.show()
    view.title = "A Title"


    # A line chart_tests item (again)
    l = LineChartItem()
    x = np.arange(-30, 300, 0.2, dtype=np.float)
    y = np.sin(2 * np.pi * 3 / float(max(x) - min(x)) * x)
    l.plot(y, x, "a sine")

    sec = SecondaryHorizontalAxis(x + 0.24, x * 2e14 - 12.67567)
    view.addSecondaryHorizontalAxis(sec)

    sec_vertical = SecondaryVerticalAxis(y, y * 10)
    view.centralWidget.addSecondaryVerticalAxis(sec_vertical)


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
    view.setLegendVisible(True)

    view.resize(300, 800)

    qapp.exec_()