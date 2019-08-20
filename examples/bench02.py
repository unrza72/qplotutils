#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bench02
-------

Example with more containers
"""
import os
import sys
import signal
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication

from qplotutils import CONFIG

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.bench import Dock, Bench, Placement

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
    CONFIG.debug_layout = True

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

    # First dock
    dock_01 = Dock(title="Dock 1")
    bench.addDock(dock_01)

    dock_02 = Dock(title="Dock 2")
    bench.addDock(dock_02, placement=Placement.RIGHT)  # TAB, ref=dock_01)

    # dock_03 = Dock(title="Dock 3")
    # bench.addDock(dock_03, placement=Placement.TOP)
    #
    # dock_04 = Dock(title="Dock 4")
    # bench.addDock(dock_04, placement=Placement.BOTTOM, ref=dock_01)

    bench.setWindowTitle("Bench Example 02")
    bench.resize(800, 800)
    bench.show()
    qapp.exec_()
