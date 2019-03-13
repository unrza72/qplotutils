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
from qplotutils.wireframe.items import Box, CoordinateCross, Grid, ShaderBox
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
    timer.start(1000)  # You may change this if you wish.
    timer.timeout.connect(lambda: None)

    w = ChartView3d()
    w.show()
    w.props.distance = 5

    cc = CoordinateCross()
    cc.setGLOptions('opaque')
    w.addItem(cc)

    grid = Grid()
    grid.setGLOptions('opaque')
    w.addItem(grid)

    # import random
    # k = 0
    # for x in range(-10,10,2):
    #     y = 1
    #     for y in range(-10,10,2):
    #         for z in range(-10, 10, 2):
    #             b = ShaderBox()
    #             b.translate(x, y, z)
    #
    #             f1 = random.random()
    #             f2 = random.random()
    #             f3 = random.random()
    #             b.scale(f1, f2, f3)
    #             b.setGLOptions('opaque')
    #             w.addItem(b)
    #
    #     k += 1
    # print(k)

    b = ShaderBox()
    b.translate(1.1, 1.1, 0)
    b.scale(0.5,0.5,0.5)
    # b.setGLOptions('translucent')
    b.setGLOptions('opaque')
    w.addItem(b)

    b = ShaderBox(shader='balloon', face_color=(0.6, 0.1, 0.1, 0.3))
    b.translate(2.1, 1.1, 0)
    b.scale(0.5, 0.5, 0.5)
    b.setGLOptions('translucent')
    # b.setGLOptions('opaque')
    w.addItem(b)

    b = ShaderBox(shader='shaded')
    b.translate(3.1, 1.1, 0)
    b.scale(0.5, 0.5, 0.5)
    # b.setGLOptions('translucent')
    b.setGLOptions('opaque')
    w.addItem(b)

    b = ShaderBox(shader='edge_highlight')
    b.translate(4.1, 1.1, 0)
    b.scale(0.5, 0.5, 0.5)
    # b.setGLOptions('translucent')
    b.setGLOptions('opaque')
    w.addItem(b)


    qapp.exec_()
