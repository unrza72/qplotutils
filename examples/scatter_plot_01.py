#!/usr/bin/python
"""
Scatter plot example
--------------------




"""
import logging
import os
import random
import signal
import sys
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication



PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)


from qplotutils import Configuration
from qplotutils.bench import Bench, Dock, Placement
from qplotutils.chart import color
from qplotutils.chart.color import Colormap
from qplotutils.chart.scatter_plot import ScatterPlotView, ScatterItem


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015-2018 Philipp Baust"
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
    logging.basicConfig(level=logging.DEBUG)

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

    bench = Bench()
    bench.resize(900, 400)

    # First dock
    cm_01 = Colormap()
    view_01 = ScatterPlotView(cm_01)

    s = ScatterItem(0, 3, -1)
    view_01.addItem(s)
    dock_01 = Dock(title="Add items dynamic range")
    dock_01.addWidget(view_01)
    bench.addDock(dock_01)

    items = []
    for k in range(10000):
        s = ScatterItem(random.randint(-100, 100), random.randint(-100, 100), k)
        items.append(s)

    view_01.addItems(items)

    # Second
    cm_02 = Colormap()
    view_02 = ScatterPlotView(cm_02, 0, 500)
    dock_02 = Dock(title="Add items fixed range")
    dock_02.addWidget(view_02)
    bench.addDock(dock_02, Placement.RIGHT)

    s = ScatterItem(0, 3, -1)
    view_02.addItem(s)

    for k in range(50):
        s = ScatterItem(random.randint(-100, 100), random.randint(-100, 100), k)
        view_02.addItem(s)


    # Third
    cm_03 = Colormap(color._jet_data)
    view_03 = ScatterPlotView(cm_03)
    dock_03 = Dock(title="Add items dynamic range (slow)")
    dock_03.addWidget(view_03)
    bench.addDock(dock_03, Placement.RIGHT)

    s = ScatterItem(0, 3, -1)
    view_03.addItem(s)

    # bag = []
    for k in range(60):
        s = ScatterItem(random.randint(-100, 100), random.randint(-100, 100), k)
        view_03.addItem(s)

    # view_01.autoRange()
    # view_02.autoRange()
    # view_03.autoRange()
    bench.show()
    qapp.exec_()