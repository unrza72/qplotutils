#!/usr/bin/python
"""
Chart with two horizontal axes
------------------------------

"""
import os
import signal
import sys
import numpy as np
from qtpy.QtCore import QTimer, QObject, Qt
from qtpy.QtWidgets import QApplication

import logging

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.chart.interactive import InteractiveVerticalLine, InteractiveChangeEvent
from qplotutils.chart.view import ChartView
from qplotutils.chart.items import LineChartItem


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2017, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


class AWidget(QObject):

    def __init__(self, parent=None):
        super(AWidget, self).__init__(parent)

    def report(self, e=InteractiveChangeEvent):
        _log.debug(e.position)


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

    qapp = QApplication([])

    # call the python loop periodically to catch interrupts from shell
    timer = QTimer()
    timer.start(1000)
    timer.timeout.connect(lambda: None)

    view = ChartView(orientation=ChartView.CARTESIAN)
    view.resize(600, 600)
    view.show()

    # A line chart_tests item (again)
    l = LineChartItem()
    x = np.arange(-30, 300, 0.2, dtype=np.float)
    y = np.sin(2 * np.pi * 3 / float(max(x) - min(x)) * x)
    l.plot(y, x, "a sine")
    view.addItem(l)

    ivline = InteractiveVerticalLine()
    ivline.setX(5, "Current Timestamp", Qt.darkGreen)
    view.addItem(ivline)

    # # Set legend visible
    view.setLegendVisible(True)
    view.autoRange()
    # view.setRange(QRectF(0,0,30,1))
    # view.setMaxVisibleRange(QRectF(-100,-10000,600,20000))


    a = AWidget()
    ivline.positionChange.connect(a.report)


    qapp.exec_()