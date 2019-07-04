#!/usr/bin/python
"""
Wire frame
----------



"""
import os
import sys
import logging
import signal

from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication

from qplotutils import CONFIG
from qplotutils.wireframe.base_types import DefaultGlOptions

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.wireframe.items import Box, CoordinateCross, Grid, MeshItem, Mesh
from qplotutils.wireframe.view import ChartView3d


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015-2018 Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"


_log = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    CONFIG.debug = True


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

    w = ChartView3d()
    w.show()
    w.props.distance = 5

    cc = CoordinateCross()
    w.addItem(cc)

    grid = Grid(20,)
    w.addItem(grid)

    grid = Grid(edge_color=(0.7,0,0,1))
    grid.setGLOptions(DefaultGlOptions.TRANSLUCENT)
    grid.rotate(90, 1,0,0)
    w.addItem(grid)

    b = MeshItem(Mesh.cube(2), shader='shaded')
    b.translate(2, 2, 0)
    w.addItem(b)

    b = MeshItem(Mesh.sphere(20, 20, 1), shader='shaded', smooth=False)
    b.translate(-2, 2, 0)
    w.addItem(b)

    b = MeshItem(Mesh.sphere(20, 20, 1), shader='shaded', smooth=True)
    b.translate(-2, -2, 0)
    w.addItem(b)

    b = MeshItem(Mesh.cone(20, 1, 5), shader='shaded', smooth=True)
    b.translate(2, -2, 0)
    w.addItem(b)

    b = MeshItem(Mesh.sphere(20, 20, 1), shader='heightColor', faceColor=(1, 0, 0, 1), smooth=False)
    b.translate(-6, -2, 0)
    w.addItem(b)

    # Annoying bug, will destroy correct z apeareance
    b = MeshItem(Mesh.sphere(20, 20, 1), shader='balloon', faceColor=(1, 0, 0, 0.3), smooth=False)
    b.translate(-6, 2, 0)
    w.addItem(b)

    qapp.exec_()
