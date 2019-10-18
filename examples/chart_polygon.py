#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart01
-------


"""
import logging
import os
import signal
import sys

import numpy as np
from qtpy.QtCore import QPointF
from qtpy.QtGui import QPicture, QPen, QBrush
from qtpy.QtCore import QTimer
from qtpy.QtCore import Qt, QRectF
from qtpy.QtGui import QColor, QPainter, QPainterPath
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import (
    QStyleOptionGraphicsItem,
)
from shapely.geometry import Polygon


PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.bench import Bench, Placement, Dock

from qplotutils.chart.utils import makePen
from qplotutils import Configuration, CONFIG
from qplotutils.chart.view import ChartView
from qplotutils.chart.items import LineChartItem, ChartItem


np.random.seed(42)

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

#: Module level logger
_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)

_cfg = CONFIG

osci_items = []
birdseye_items = []


class SignalDock(Dock):
    def __init__(self, title="OSCI", orientation=ChartView.CARTESIAN):
        super(SignalDock, self).__init__(title)

        self.view = ChartView(orientation=orientation)
        self.addWidget(self.view)

        # self.timeline = InteractiveVerticalLine()
        # self.view.addItem(self.timeline)

    def receiveTime(self, e):
        self.timeline.setX(e.position.x())




class PolyChartItem(ChartItem):
    """ Visualises the given data as line chart_tests.

    :param parent: Items parent
    """

    def __init__(self, parent=None):
        super(PolyChartItem, self).__init__(parent)
        # self._xData = None
        # self._yData = None
        self._label = None
        # self._color = None
        self._bRect = None
        self.markers = {}
        self._path = None

        self._showticks = False
        self._visible_range = None

        self._ordinate = None
        self._abscissa = None

        self._picture = None

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    # @property
    # def color(self):
    #     return self._color

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    def drawPolygon(self, polygon: Polygon):
        """

        :param polygon:
        :return:
        """
        self._path = QPainterPath()
        # self._path.moveTo(self._xData[0], self._yData[0])

        x, y = polygon.exterior.coords.xy

        self._path.moveTo(x[0], y[0])

        for xc, yc in zip(x,y):
            self._path.lineTo(xc, yc)

        self._bRect = self._path.boundingRect()

    def boundingRect(self):
        """ Returns the bounding rect of the chart_tests item
        :return: Bounding Rectangle
        :rtype: QRectF
        """
        return self._bRect

    def updatePicture(self):
        self._picture = QPicture()
        p = QPainter(self._picture)
        pen = makePen(self.color)
        p.setPen(pen)

        if self._path:
            p.drawPath(self._path)

        if CONFIG.debug_layout:
            p.setPen(makePen(Qt.yellow))
            p.setBrush(Qt.transparent)
            p.drawRect(self._bRect)

        p.end()

    def boundingRect(self):
        return self._bRect

    def shape(self):
        return self._path

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        if self._picture is None:
            self.updatePicture()
        self._picture.play(p)






class Track(object):
    """ Draws path from kinematics data. """

    WHEELBASE = 2.75

    def from_kinematics_data(self):
        pass

    def __init__(self, timestamps, velocity, acceleration, yaw_rate, slip_angle):
        self.timestamps = timestamps
        self.velocity = velocity
        self.acceleration = acceleration
        self.yaw_rate = yaw_rate
        self.slip_angle = slip_angle

        dt = np.diff(self.timestamps)
        ds = self.acceleration[1:] / 2 * dt ** 2 + self.velocity[1:] * dt
        psi = self.yaw_rate[1:] * dt
        self.psi_global = np.cumsum(psi)

        cp = np.cos(psi)
        sp = np.sin(psi)

        if self.slip_angle is not None:
            cs = np.cos(self.slip_angle[1:])
            ss = np.sin(self.slip_angle[1:])
        else:
            cs = 1
            ss = 0

        dx = ds * np.cos(psi)
        dy = ds * np.sin(psi)

        dx_g = (
                self.WHEELBASE * (np.cos(psi) - 1) +
                dx * (cs * cp + ss * sp) +
                dy * (ss * cp - cs * sp)
        )
        dy_g = (
                -self.WHEELBASE * np.sin(psi) +
                dx * (cs * sp + ss * cp) +
                dy * (cs * cp - ss * sp)
        )

        # TODO: check how to do this with einsum
        self.track_x = np.zeros(psi.shape, dtype=np.float)
        self.track_y = np.zeros(psi.shape, dtype=np.float)
        for k in range(1, len(psi)):
            nx = (
                    dx_g[k] +
                    cp[k - 1] * self.track_x[k - 1] -
                    sp[k] * self.track_y[k - 1]
            )
            ny = (
                    dy_g[k] +
                    sp[k - 1] * self.track_x[k - 1] +
                    cp[k] * self.track_y[k - 1]
            )

            self.track_x[k] = nx
            self.track_y[k] = ny

        self.sx = dx[0] / 2
        self.sy = dy[0] / 2

    def global_coordinates(self, y_shift=0):
        cx = (
                np.cos(self.psi_global) * self.track_x +
                np.sin(self.psi_global) * (self.track_y - y_shift) +
                self.WHEELBASE
        )
        cy = (
                np.sin(self.psi_global) * self.track_x -
                np.cos(self.psi_global) * (self.track_y - y_shift)
        )
        return np.array([cx, cy])


def lane_change(t0, t1, idx0, idx1):
    tt0 = t0.copy()
    tt1 = t1.copy()

    tt0[:,idx0:idx1] = (
            tt0[:,idx0:idx1] * np.linspace(1, 0, idx1 - idx0) +
            tt1[:,idx0:idx1] * np.linspace(0, 1, idx1 - idx0)
    )
    tt0[:,idx1:] = tt1[:,idx1:]
    return tt0


def ui():
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
    bench.resize(1800, 800)
    bench.show()

    # First dock
    dock_01 = SignalDock("Birdseye", ChartView.AUTOSAR)
    bi = dock_01.view
    bi.setAspectRatio(1)
    bench.addDock(dock_01)

    # Second dock
    dock_02 = SignalDock("OSCI")
    osci = dock_02.view
    bench.addDock(dock_02, placement=Placement.LEFT)

    for item in osci_items:
        osci.addItem(item)

    for item in birdseye_items:
        bi.addItem(item)

    # bi.force_layout()
    # osci.force_layout()
    # bi.autoRange()
    osci.autoRange()
    qapp.exec_()


def build_track():
    yaw_rate_max = 0.16
    yaw_rate_signal = np.array([0])

    for k in range(60):
        samples = np.random.randint(120, 600)
        yaw_rate = (np.random.ranf(1) * 2 - 1) * yaw_rate_max
        segment = np.ones(samples,
                          np.float) * yaw_rate  # + np.random.rand(samples) * 0.01
        yaw_rate_signal = np.concatenate((yaw_rate_signal, segment))

    blackmann = np.blackman(400)
    yaw_rate_signal_smoothed = np.convolve(blackmann / blackmann.sum(), yaw_rate_signal)
    noise = 0.001
    yaw_rate_final = yaw_rate_signal_smoothed + (
                np.random.randn(len(yaw_rate_signal_smoothed)) * noise - noise / 2)

    l = LineChartItem()
    l.plot(yaw_rate_signal)
    l.showTicks = True
    osci_items.append(l)

    l = LineChartItem()
    l.plot(yaw_rate_signal_smoothed)
    l.color = QColor(0, 255, 0, 255)
    l.showTicks = True
    osci_items.append(l)

    l = LineChartItem()
    l.plot(yaw_rate_final)
    l.color = QColor(0, 0, 255, 255)
    l.showTicks = True
    osci_items.append(l)

    # ---
    # Track
    # ---
    n_samples = len(yaw_rate_final)
    ts = np.arange(0, 1000, 0.02, np.float)
    ts = ts[:n_samples]
    velocity = np.ones(n_samples, np.float) * 20
    accel = np.zeros(n_samples, np.float)
    slip_angle = np.zeros(n_samples, np.float)

    t = Track(ts, velocity, accel, yaw_rate_final, slip_angle)
    track_1 = t.global_coordinates()
    track_2 = t.global_coordinates(3.75 / 2 + 3.5 / 2)



    track_3 = lane_change(track_1, track_2, 700, 800)
    track_4 = lane_change(track_3, track_1, 900, 1200)
    track_5 = lane_change(track_4, track_2, 2000, 2150)
    track_6 = lane_change(track_5, track_1, 2400, 2800)

    # max_samples = 3000
    # l = LineChartItem()
    # l.plot(track_6[1, :max_samples], track_6[0, :max_samples])
    # l.color = QColor(255, 0, 0, 255)
    # birdseye_items.append(l)

    return t

def build_lane(t):
    lane_width = 3.75
    lane_boundary_left0 = t.global_coordinates(y_shift=lane_width / 2.)
    lane_boundary_left1 = t.global_coordinates(y_shift=lane_width / 2. + 3.5)

    lane_boundary_right0 = t.global_coordinates(y_shift=-lane_width / 2.)
    lane_boundary_right1 = t.global_coordinates(y_shift=-lane_width / 2. - 3.5)

    def mk_box(left_coordinates, right_coordinates, k, step=30, noise=0.3):
        box = np.array([
            left_coordinates[:, k - step],
            left_coordinates[:, k],
            right_coordinates[:, k],
            right_coordinates[:, k - step],
        ]) + np.random.random(8).reshape((4, 2)) * noise
        return box

    track_0 = []
    track_1 = []

    for k in range(30, 3000, 30):
        # b = np.array([
        #     lane_boundary_left0[:, k - 30],
        #     lane_boundary_left0[:, k],
        #     lane_boundary_right0[:, k],
        #     lane_boundary_right0[:, k - 30],
        # ]) + np.random.random(8).reshape((4, 2)) * max_lane_noise
        b = mk_box(
            lane_boundary_left0,
            lane_boundary_right0,
            k
        )
        lane_segment1 = Polygon(b)
        track_0.append(lane_segment1)
        p = PolyChartItem()
        p.drawPolygon(lane_segment1)
        birdseye_items.append(p)

        # b = [
        #     lane_boundary_left0[:, k - 30],
        #     lane_boundary_left0[:, k],
        #     lane_boundary_left1[:, k],
        #     lane_boundary_left1[:, k - 30],
        #
        # ]
        b = mk_box(
            lane_boundary_left1,
            lane_boundary_left0,
            k
        )
        lane_segment2 = Polygon(b)
        track_1.append(lane_segment2)
        p = PolyChartItem()
        p.drawPolygon(lane_segment2)
        birdseye_items.append(p)

    return track_0, track_1

def simplify(track0, track1):

    # left ego x/y
    lex = []
    ley = []

    # by luck use the coord orientation points 0, 1, 4 are left box points and
    # 2,3 are right side

    for p, o in zip(track0[0:80], track1[0:80]):
        c = p.exterior.coords

        lex.extend(c.xy[0][0:2])
        ley.extend(c.xy[1][0:2])

    # for p in track1[0:10]:
        c = o.exterior.coords
        lex.extend(c.xy[0][2:4])
        ley.extend(c.xy[1][2:4])

    from scipy import interpolate

    xx = np.fromiter(lex, np.float)
    yy = np.fromiter(ley, np.float)

    coords = np.array([
        xx,
        yy
    ])

    sorted_coords = coords[:,coords[0,:].argsort()]

    # # tck, u = interpolate.splprep(sorted_coords)
    # min_x,  max_x = min(lex), max(lex)
    # unew = np.arange(min_x, max_x, 5)
    # # out = interpolate.splev(unew, tck)
    # #
    # from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
    # ius = InterpolatedUnivariateSpline(sorted_coords[0,:], sorted_coords[1,:])
    # yi = ius(unew)
    # #
    from scipy.signal import savgol_filter
    ywhat = savgol_filter(sorted_coords[1,:], 15, 2)


    # l = LineChartItem()
    # l.plot(coords[1,:], coords[0,:])
    # l.color = QColor(0, 255, 0, 255)
    # l.showTicks = True
    # birdseye_items.append(l)

    l = LineChartItem()
    l.plot(sorted_coords[1,:], sorted_coords[0,:])
    l.color = QColor(0, 0, 255, 255)
    l.showTicks = True
    birdseye_items.append(l)

    l = LineChartItem()
    l.plot(ywhat, sorted_coords[0,:])
    l.color = QColor(255, 0, 0, 255)
    l.showTicks = True
    birdseye_items.append(l)

    pass

if __name__ == "__main__":
    cfg = Configuration()
    cfg.debug = False



    lane_track = build_track()

    track_0, track_1 = build_lane(lane_track)
    simplify(track_0, track_1)

    ui()


