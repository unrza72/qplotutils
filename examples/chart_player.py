#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart with two horizontal axes
------------------------------

"""
import os
import pandas as pd
import numpy as np
import signal
import sys
import numpy as np
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from qtpy.QtCore import QTimer, QObject, Qt
from qtpy.QtWidgets import QApplication

import logging

from qplotutils.player import OsciPlayable, PlaybackWidget, Birdview, IBirdeyeItem

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.chart.interactive import InteractiveVerticalLine, InteractiveChangeEvent
from qplotutils.chart.view import ChartView
from qplotutils.chart.items import LineChartItem



np.random.seed(42)

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

    # w = OsciPlayable()
    w = QWidget()
    w.setLayout(QVBoxLayout())

    p = PlaybackWidget()
    w.layout().addWidget(p)

    iocsi = OsciPlayable()
    w.layout().addWidget(iocsi)

    bi = Birdview(prototyp=IBirdeyeItem)
    w.layout().addWidget(bi)

    p.ts_change.connect(iocsi.render_ts)
    iocsi.data_changed.connect(p.on_data_change)
    p.ts_change.connect(bi.render_ts)

    ts = np.arange(0, 65, 0.06, dtype=np.float)
    y = np.sin(2 * np.pi * 3 / float(max(ts) - min(ts)) * ts)
    s = pd.Series(y, ts)

    p.timeline = ts
    # p._step = int(1000 / 25) -5
    iocsi.add_data(s, "Sinus")



    guardrails_start_points = []
    # right
    for x in range(-5, 80, 7):
        guardrails_start_points.append([x, -4.2])
        guardrails_start_points.append([x, 12.9])
    # guardrails_start_points = np.fromiter(guardrails_start_points, dtype=np.float)


    obj_data = []
    for idx in ts:
        obj_data.append([
                    idx,
                    0,
                    idx, 1,
                    idx + 4, 1,
                    idx + 4, -1,
                    idx, -1,
        ])

        for k, gr in enumerate(guardrails_start_points):

            dx = gr[0] - idx * 0.3
            dy = gr[1]

            if dx < -5:
                continue

            obj_data.append([
                idx,
                k + 1,
                dx, dy + .5,
                dx + .5, dy + .5,
                dx + .5, dy -.5,
                dx, dy - .5,
            ])


    df = pd.DataFrame(obj_data, columns=[
                "ts",
                "obj_id",
                "x0", "y0",
                "x1", "y1",
                "x2", "y2",
                "x3", "y3",
            ])
    df.set_index("ts", drop=False, inplace=True)

    bi.add_data(df)
    iocsi.autoRange()




    w.show()
    qapp.exec_()


