#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Region of interest
------------------

Example for a region of interest (ROI) with different handles.

"""
import logging
import os
import signal
import sys
from qtpy.QtCore import QTimer, QRectF
from qtpy.QtWidgets import QApplication, QMenu, QAction


PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.chart.roi import RectangularRegion, ResizeHandle, HandlePosition, RotateHandle
from qplotutils.chart.view import ChartView


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


if __name__ == "__main__":
    """ Minimal example showing a bench with 2 docks.
    The docks can be resized and dragged around.
    """
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
    view.setWindowTitle("ROI Test")
    view.resize(500, 500)
    view.setAspectRatio(1.0)
    view.centralWidget.area.setRange(QRectF(-7, -7, 14, 14))
    # view.visibleRegion()
    view.show()

    roi = RectangularRegion(1, 0, 2, 1, 0.)
    roi.addHandle(ResizeHandle(position=HandlePosition.TOP))
    roi.addHandle(ResizeHandle(position=HandlePosition.LEFT))
    roi.addHandle(ResizeHandle(position=HandlePosition.BOTTOM))
    roi.addHandle(ResizeHandle(position=HandlePosition.RIGHT))
    roi.addHandle(RotateHandle(position=HandlePosition.RIGHT | HandlePosition.TOP))
    view.addItem(roi)



    def contextMenu(pos):

        menu = QMenu()

        def remove_handle():
            if len(roi.handles) > 0:
                h = roi.handles[0]
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