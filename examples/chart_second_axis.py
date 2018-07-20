#!/usr/bin/python
"""
Chart with two horizontal axes
------------------------------

"""
import os
import sys
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import logging

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.chart.view import ChartView, SecondaryHorizontalAxis
from qplotutils.chart.items import LineChartItem, HLine, VLine

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2017, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    qapp = QApplication([])

    view = ChartView(orientation=ChartView.CARTESIAN)
    view.show()

    # A line chart_tests item (again)
    l = LineChartItem()
    x = np.arange(-30, 300, 0.2, dtype=np.float)
    y = np.sin(2 * np.pi * 3 / float(max(x) - min(x)) * x)
    l.plot(y, x, "a sine")

    sec = SecondaryHorizontalAxis(x + 0.24, x * 2e14 - 12.67567)
    view.centralWidget.addSecondaryHorizontalAxis(sec)


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

    qapp.exec_()