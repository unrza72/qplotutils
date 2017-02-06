#!/usr/bin/python
"""
Region of interest
------------------

Example for a region of interest (ROI) with different handles.

"""
import logging
import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.chart.roi import RectangularRegion, ResizeHandle, HandlePosition, RotateHandle
from qplotutils.chart.view import ChartView


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015, 2017, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)


if __name__ == "__main__":
    """ Minimal example showing a bench with 2 docks.
    The docks can be resized and dragged around.
    """
    logging.basicConfig(level=logging.DEBUG)


    qapp = QApplication([])

    view = ChartView(orientation=ChartView.CARTESIAN)
    view.setWindowTitle("ROI Test")
    view.resize(500, 500)
    view.setAspectRatio(1.0)
    view.centralWidget.area.setRange(QRectF(-7, -7, 14, 14))
    # view.visibleRegion()
    view.show()

    roi = RectangularRegion(1, 0, 2, 1, 0.)
    roi.addHandle(ResizeHandle(roi, position=HandlePosition.TOP))
    roi.addHandle(ResizeHandle(roi, position=HandlePosition.LEFT))
    roi.addHandle(ResizeHandle(roi, position=HandlePosition.BOTTOM))
    roi.addHandle(ResizeHandle(roi, position=HandlePosition.RIGHT))
    roi.addHandle(RotateHandle(roi, position=HandlePosition.RIGHT | HandlePosition.TOP))
    view.addItem(roi)


    def contextMenu(pos):

        menu = QMenu()

        def remove_handle():
            h = roi.handles[1]
            roi.removeHandle(h)

        def rotate_90():
            roi.setRotation(roi.rotation() + 82.)

        rm_action = QAction('Remove handle', view)
        rm_action.triggered.connect(remove_handle)

        ro_action = QAction('Rotate by 82', view)
        ro_action.triggered.connect(rotate_90)

        menu.addAction(rm_action)
        menu.addAction(ro_action)
        menu.exec_(view.mapToGlobal(pos))


    view.customContextMenuRequested.connect(contextMenu)

    qapp.exec_()