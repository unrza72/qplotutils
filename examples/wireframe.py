import os
import sys
import logging
import numpy as np
import signal

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtOpenGL import *
from qtpy.QtWidgets import *

from OpenGL.GL import *

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.wireframe.cam_control import CamControl
from qplotutils.wireframe.items import Box, CoordinateCross, Grid, MeshItem, Mesh
from qplotutils.wireframe.view import ChartView3d
from qplotutils.wireframe.base_types import Vector3d

_log = logging.getLogger(__name__)


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

    timer = QTimer()
    timer.start(100)  # You may change this if you wish.
    timer.timeout.connect(lambda: None)

    w = ChartView3d()
    w.show()
    w.props.distance = 5

    cc = CoordinateCross()
    cc.setGLOptions('opaque')
    w.addItem(cc)

    grid = Grid(20,)
    grid.setGLOptions('opaque')
    w.addItem(grid)

    # grid = Grid(edge_color=(0.7,0,0,1))
    # grid.setGLOptions('opaque')
    # grid.rotate(90, 1,0,0)
    # w.addItem(grid)


    b = MeshItem(Mesh.cube(2), shader='shaded')
    b.translate(2, 2, 0)
    b.setGLOptions('opaque')
    w.addItem(b)


    b = MeshItem(Mesh.sphere(20, 20, 1), shader='shaded', smooth=False)
    # b = MeshItem(Mesh.cube(), shader='shaded')
    b.translate(-2, 2, 0)
    b.setGLOptions('opaque')
    w.addItem(b)

    b = MeshItem(Mesh.sphere(20, 20, 1), shader='shaded', smooth=True)
    # b = MeshItem(Mesh.cube(), shader='shaded')
    b.translate(-2, -2, 0)
    b.setGLOptions('opaque')
    w.addItem(b)

    b = MeshItem(Mesh.cone(20, 1, 5), shader='shaded', smooth=True)
    # b = MeshItem(Mesh.cube(), shader='shaded')
    b.translate(2, -2, 0)
    b.setGLOptions('opaque')
    w.addItem(b)

    b = MeshItem(Mesh.sphere(20, 20, 1), shader='heightColor', face_color=(1,0,0,1), smooth=False)
    # b = MeshItem(Mesh.cube(), shader='shaded')
    b.translate(-6, -2, 0)
    b.setGLOptions('opaque')
    w.addItem(b)

    qapp.exec_()
