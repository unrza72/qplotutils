#!/usr/bin/python
"""
Bench01
-------

Minimal Example opening two dock widgets.
"""
import os
import sys
from PyQt4.QtGui import *

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.bench import Dock, Bench


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015, 2017, Philipp Baust"
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
    qapp = QApplication([])

    # Creating the bench
    bench = Bench()

    # First dock
    dock_01 = Dock()
    bench.addDock(dock_01)

    # Second dock
    dock_02 = Dock(title="Dock 2")
    bench.addDock(dock_02)

    bench.setWindowTitle("Bench Example 01")
    bench.resize(300, 400)
    bench.show()
    qapp.exec_()

