#!/usr/bin/python
"""
Chart04
-------

Example for legend placement
"""
import os
import signal
import sys
import numpy as np
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtOpenGL import *
from qtpy.QtWidgets import *


PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)


from qplotutils.bench import Dock, Bench, Placement
from qplotutils.chart.view import ChartView
from qplotutils.chart.items import LineChartItem

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015, 2017, 2018, Philipp Baust"
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

        # self.timeline = InteractiveVerticalLine()
        # self.view.addItem(self.timeline)

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
    dock_01 = SignalDock("OSCI 1 - Top, Left")
    dock_01.view.setLegendVisible(True, ChartView.TOP_LEFT)
    bench.addDock(dock_01)

    # Second dock
    dock_02 = SignalDock("OSCI 2 - Top, Right")
    dock_02.view.setLegendVisible(True, ChartView.TOP_RIGHT)
    bench.addDock(dock_02)

    # Third dock
    dock_03 = SignalDock("OSCI 3 - Bottom, Left")
    dock_03.view.setLegendVisible(True, ChartView.BOTTOM_LEFT)
    bench.addDock(dock_03, Placement.TAB, ref=dock_02)

    # Fourth dock
    dock_04 = SignalDock("OSCI 4 -  Bottom, Right")
    dock_04.view.setLegendVisible(True, ChartView.BOTTOM_RIGHT)

    # Make a context menu, to toggle legend visibility
    action = QAction("Toggle legend", dock_04.view)
    action.setCheckable(True)
    action.setChecked(True)

    def toggle(s):
        dock_04.view.setLegendVisible(s, ChartView.BOTTOM_RIGHT)
        return True

    action.toggled.connect(toggle)

    def context_menu(pos):
        menu = QMenu()
        menu.addAction(action)
        menu.exec_(dock_04.view.mapToGlobal(pos))

    dock_04.view.customContextMenuRequested.connect(context_menu)
    bench.addDock(dock_04)

    bench.setWindowTitle("Legend Example")

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

    l = LineChartItem()
    x = np.arange(0.1, 10, 0.1, dtype=np.float)
    y = np.log(x)
    l.plot(y, x, "logarithmn")
    dock_03.view.addItem(l)
    dock_03.view.autoRange()

    l = LineChartItem()
    x = np.arange(0.1, 10, 0.1, dtype=np.float)
    y = np.e ** x
    l.plot(y, x, "exponential")
    dock_04.view.addItem(l)
    dock_04.view.autoRange()

    bench.show()
    qapp.exec_()

