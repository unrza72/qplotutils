#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arc
---


"""
import os
import signal
import sys
import numpy as np
import shapely
import pandas as pd
from qtpy.QtGui import QColor
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import QApplication

from examples.chart_polygon import Track
from qplotutils.bench import Bench, Dock, Placement

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)


from qplotutils import Configuration
from qplotutils.chart.view import ChartView
from qplotutils.chart.items import LineChartItem


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

    # Creating the bench
    bench = Bench()
    bench.resize(800, 1200)

    # First dock
    dock_01 = SignalDock("Birdseye", ChartView.AUTOSAR)
    bi = dock_01.view
    # bi.setAspectRatio(1)
    bench.addDock(dock_01)

    # Second dock
    # dock_02 = SignalDock("OSCI")
    # osci = dock_02.view
    # bench.addDock(dock_02, placement=Placement.BOTTOM)


    # RQ 43,5 (Breite der befestigten Fläche beträgt 2 × 18,25 Meter)

    r_min = 150  # m

    lane_width_emergency_lane = 2.5  # m
    lane_width_1 = 3.75  # m
    lane_width_2 = 3.75  # m


    # min radius ego path
    m = r_min
    x = np.arange(-m,m,0.01)
    y = -m + np.sqrt(m**2 - x**2)

    l = LineChartItem()
    l.plot(y, x)
    bi.addItem(l)

    # # ego lane right border
    # m = r_min - lane_width_1 / 2
    # x = np.arange(0, m, 1)
    # y = -r_min + np.sqrt(m ** 2 - x ** 2)
    #
    # l = LineChartItem()
    # l.plot(y, x)
    # l.color = QColor(255, 255, 255, 255)
    # bi.addItem(l)
    #
    # # emergency lane right edge
    # m = r_min - lane_width_1 / 2 - lane_width_emergency_lane
    # x = np.arange(0, m, 1)
    # y = -r_min + np.sqrt(m ** 2 - x ** 2)
    #
    # l = LineChartItem()
    # l.plot(y, x)
    # l.color = QColor(0, 255, 0, 255)
    # bi.addItem(l)
    #
    # # ego right broder
    # m = r_min + lane_width_1 / 2
    # x = np.arange(0, m, 1)
    # y = -r_min + np.sqrt(m ** 2 - x ** 2)
    #
    # l = LineChartItem()
    # l.plot(y, x)
    # l.color = QColor(255, 255, 255, 255)
    # bi.addItem(l)
    #
    # # right next to ego border
    # m = r_min + lane_width_1 / 2 + lane_width_2
    # x = np.arange(0, m, 1)
    # y = -r_min + np.sqrt(m ** 2 - x ** 2)
    #
    # l = LineChartItem()
    # l.plot(y, x)
    # l.color = QColor(255, 255, 255, 255)
    # bi.addItem(l)
    #
    # # left road edge / guarail middle
    # m = r_min + lane_width_1 / 2 + lane_width_2 + .75
    # x = np.arange(0, m, 1)
    # y = -r_min + np.sqrt(m ** 2 - x ** 2)
    #
    # l = LineChartItem()
    # l.plot(y, x)
    # l.color = QColor(0, 255, 0, 255)
    # bi.addItem(l)



    # now the craze stuff
    v_max = 105 / 3.6  # [m/s]
    print("Ego velocity: {}[m/s]".format(v_max))

    R_min = 2 * np.pi * r_min  # [m]
    print("Circumference at min radius: {}[m]".format(R_min))

    t_fc = R_min / v_max
    yaw_rate = 2 * np.pi / t_fc # in rad / s
    print("Constant Yaw rate: {}[rad/s]. Duration to drive full circle at v_max: {}".format(yaw_rate, t_fc))


    # compute the moved time for 155m
    t_at_vmax = 155 / v_max
    print("Duration to reach end of ODA at v_max: {}[s].".format(t_at_vmax))

    rad_at_vmax = yaw_rate * t_at_vmax
    print("Radians to reach end of ODA at v_max: {}[rad].".format(rad_at_vmax))

    T = 0.02
    cycles_at_vmax = t_at_vmax / T
    print("Cycles to reach end of ODA at v_max: {}.".format(cycles_at_vmax))

    for t in range(267):
        x = np.array([0, 255 * np.sin(T * t * yaw_rate)])
        y = np.array([0, 255 * np.cos(T * t * yaw_rate)]) - r_min

        # Mark the end of the ODA
        l = LineChartItem()
        l.plot(y, x)
        l.color = QColor(0, 0, 255, 255)
        bi.addItem(l)
        # bi.setAspectRatio(1)

    x = np.array([0, r_min * np.sin(yaw_rate * t_at_vmax)])
    y = np.array([0, r_min * np.cos(yaw_rate * t_at_vmax)]) - r_min

    # Mark the end of the ODA
    l = LineChartItem()
    l.plot(y, x)
    l.color = QColor(255, 0, 0, 255)
    bi.addItem(l)
    # bi.setAspectRatio(1)



    # build a track
    samples = np.ones(1500, dtype=np.float)
    ts = np.cumsum(samples * T)
    vel = samples * v_max
    acc = samples * 0.
    yaw = samples * -yaw_rate
    slip= samples * 0.

    track = Track(ts, vel, acc, yaw, slip)
    coordinates = track.global_coordinates()

    l = LineChartItem()
    l.plot(coordinates[1], coordinates[0])
    l.color = QColor(0, 0, 255, 255)
    l.showTicks = True
    bi.addItem(l)




    # # plot the rotation over time
    # t = np.arange(0, t_at_vmax, T) # in 50 Hz
    # psi_meas = -np.ones(t.shape, dtype=np.float) * psi * T
    # psi_meas[0] = 0 # !
    # psi_meas[1] = psi_meas[1] * 0.505  # !
    # psi_sum = np.cumsum(psi_meas)
    #
    #
    # # l = LineChartItem()
    # # l.plot(psi_meas, t)
    # # osci.addItem(l)
    # #
    # # l = LineChartItem()
    # # l.plot(psi_sum, t)
    # # osci.addItem(l)
    #
    # DISTANCE_TO_COG = 2.75
    #
    # v = 105 / 3.6  # m / s
    # ds = v * T  # m
    #
    # dx = ds * np.cos(psi_meas)
    # dy = ds * np.sin(psi_meas)
    #
    # cp = np.cos(psi_sum)
    # sp = np.sin(psi_sum)
    #
    # # dx_g = DISTANCE_TO_COG * (np.cos(psi_meas) - 1) + dx * cp - dy * sp
    # # dy_g = -DISTANCE_TO_COG * np.sin(psi_meas) + dx * sp + dy * cp
    #
    # # v = 105 / 3.6   # m / s
    # # ds = v * T  # m
    #
    # # dx = np.cos(psi_meas) * ds
    # # dy = np.sin(psi_meas) * ds
    #
    #
    # track_x = np.zeros(psi_meas.shape, dtype=np.float)
    # track_y = np.zeros(psi_meas.shape, dtype=np.float)
    #
    # # track_x_g = np.zeros(psi_meas.shape, dtype=np.float)
    # # track_y_g = np.zeros(psi_meas.shape, dtype=np.float)
    #
    # for k in range(1, len(psi_meas)):
    #     nx = track_x[k - 1] + cp[k-1] * dx[k] - sp[k-1] * dy[k]
    #     ny = track_y[k - 1] + sp[k-1] * dx[k] + cp[k-1] * dy[k]
    #
    #     # nx = dx[k-1] + cp[k-1] * track_x[k - 1] - sp[k] * track_y[k - 1]
    #     # ny = dy[k-1] + sp[k-1] * track_x[k - 1] + cp[k] * track_y[k - 1]
    #
    #     track_x[k] = nx
    #     track_y[k] = ny
    #
    #     # nx = dx_g[k - 1] + cp[k - 1] * track_x_g[k - 1] - sp[k] * track_y_g[k - 1]
    #     # ny = dy_g[k - 1] + sp[k - 1] * track_x_g[k - 1] + cp[k] * track_y_g[k - 1]
    #     #
    #     # track_x_g[k] = nx
    #     # track_y_g[k] = ny
    #
    # # l = LineChartItem()
    # # l.plot(track_y_g, track_x_g)
    # # l.color = QColor(0, 0, 255, 255)
    # # l.showTicks = True
    # # bi.addItem(l)
    #
    # l = LineChartItem()
    # l.plot(track_y, track_x)
    # l.color = QColor(0, 255, 0, 255)
    # l.showTicks = True
    # bi.addItem(l)
    #
    # y_shift = 0
    # cx = np.cos(psi_sum) * track_x + np.sin(psi_sum) * (track_y + y_shift)
    # cy = np.sin(psi_sum) * track_x - np.cos(psi_sum) * (track_y + y_shift)
    #
    # l = LineChartItem()
    # l.plot(cy, cx)
    # l.color = QColor(0, 255, 255, 255)
    # l.showTicks = True
    # bi.addItem(l)
    #
    # # y_shift = 0
    # # cx = np.cos(psi_sum) * track_x_g + np.sin(psi_sum) * (track_y_g + y_shift)
    # # cy = np.sin(psi_sum) * track_x_g - np.cos(psi_sum) * (track_y_g + y_shift)
    # #
    # # l = LineChartItem()
    # # l.plot(cy, cx)
    # # l.color = QColor(255, 255, 0, 255)
    # # l.showTicks = True
    # # bi.addItem(l)

    bench.show()
    qapp.exec_()
