#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User controls for interactivity.

"""
import logging
import datetime
import time
from collections import deque

import numpy as np
import pandas as pd
from PyQt5.QtCore import QPointF
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from qplotutils import CONFIG
from qplotutils.chart.interactive import InteractiveVerticalLine
from qplotutils.chart.items import LineChartItem, ChartItem, TextItem
from qplotutils.chart.utils import makePen, makeBrush
from qplotutils.chart.view import ChartView
from qplotutils.ui.playback import Ui_PlaybackControl

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


class IPlayable(object):

    data_changed = Signal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # when set to server to playable will send
        self.time_server = False
        self.time_agent = True
        self.time_agent_possible = True

    def render_ts(self, ts):
        pass

    # def render_idx(self, ts):
    #     pass


class OsciPlayable(IPlayable, ChartView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._displayed_data = pd.DataFrame()
        self._k = 0

        self._ivline = InteractiveVerticalLine()
        self._ivline.setX(0, "Current Timestamp", Qt.darkGreen)
        self.addItem(self._ivline)


    def add_data(self, signal: pd.Series, name=None):

        if name is None:
            self._k += 1
            name = "signal_{0:02d}".format(self._k)

        self._displayed_data[name] = signal

        l = LineChartItem()
        l.label = name
        l.plot(signal.values, signal.index.values)
        self.addItem(l)

        self.data_changed.emit(self._displayed_data.index.values)

    def render_ts(self, ts):
        # _log.debug("Osci update: {}".format(ts))
        self._ivline.setX(ts)


class IBirdeyeItem(ChartItem):
    def __init__(self, row, parent=None):
        super(ChartItem, self).__init__(parent=parent)
        self.row = None
        # self._brect = None
        self._path = None
        self.update_path(row)

    def update_path(self, row):
        self.row = row
        p = QPainterPath()
        p.moveTo(row["x0"], row["y0"])
        p.lineTo(row["x0"], row["y0"])
        p.lineTo(row["x1"], row["y1"])
        p.lineTo(row["x2"], row["y2"])
        p.lineTo(row["x3"], row["y3"])
        p.lineTo(row["x0"], row["y0"])

        if self._path is None:
            self.b_rect = p.boundingRect()
        else:
            # make sure the update will not produce a tail
            self.b_rect = self._path.boundingRect().united(p.boundingRect())
        self._path = p


        self.update()

    def boundingRect(self):
        return self.b_rect.adjusted(-.2, -.2, .4, .4)

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        p.setPen(makePen((Qt.white)))
        p.setBrush(makeBrush(Qt.white))
        p.drawPath(self._path)


class Birdview(IPlayable, ChartView):
    def __init__(self, prototyp: IBirdeyeItem, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        self.prototyp = prototyp
        self.df = None

        self.c_items = {}
        self.setVisibleRange(QRectF(-5, -10, 60, 10))
        self.setCoordinatesOrientation(self.AUTOSAR)

        # self._fps_t0 = None
        # self.fps_text = TextItem(QPointF(10, 10),"Test")
        # self.addItem(self.fps_text)
        self.setAspectRatio(1.)

    def add_data(self, df: pd.DataFrame):
        self.df = df
        self.df.set_index([ "ts", "obj_id"], drop=False, inplace=True)
        self.render_ts(df["ts"].values[0])

    def render_ts(self, ts):
        sub_df = self.df.loc[ts,:]

        deleted_obj_ids = [c for c in self.c_items.keys() if c not in sub_df["obj_id"]]
        for c in deleted_obj_ids:
            self.removeItem(self.c_items[c])
            del self.c_items[c]

        for idx, row in sub_df.iterrows():
            obj_id = row["obj_id"]
            if obj_id in self.c_items:
                # update existing
                self.c_items[obj_id].update_path(row)
            else:
                # add new
                obj = self.prototyp(row)
                self.c_items[obj_id] = obj
                self.addItem(obj)


class PlaybackWidget(QWidget):
    """ Playback control widget with the following button
        * toggle playback / pause
        * advance one step forward
        * advance one step back

    The current timestamp is inidcated by slider and a line edit.

    Models / Visualization that choose to be controlled through the playback
    widget should
    connect to :meth:`qplotutils.player.PlaybackWidget.timestamp_changed`.
    """

    #: emited whenever the timestamp is changed.
    # timestamp_changed = Signal(int, float)

    def __init__(self, parent=None):
        super(PlaybackWidget, self).__init__(parent)
        self.ui = Ui_PlaybackControl()
        self.ui.setupUi(self)

        self._timeline_df = pd.DataFrame()

        self.ui.button_play_pause.clicked.connect(self.play_pause)
        self.ui.button_back.clicked.connect(self.step_back)
        self.ui.button_next.clicked.connect(self.step_forward)

        self.ui.slider_index.valueChanged.connect(self._slider_value_changed)
        self.ui.slider_index.sliderPressed.connect(self._slider_pressed)
        # self.ui.edit_timestamp.textEdited.connect(self.jump_to_timestamp)
        self.ui.doubleSpinBox.valueChanged.connect(self._set_play_speed)

        self.__is_playing = False

        self._ts_format = "{0:02.4f}"

        self.render_delay = 1  # ms accounted for rendering

        self._step = 0
        self._filter_length = 10
        self._t = deque(maxlen=self._filter_length)

    def on_data_change(self, timeline):
        print("Data change")


    def _set_play_speed(self, value):
        samples = len(self.timeline)
        v = self._timeline_df["timeline"].values
        duration = v[-1] - v[0]

        true_step = duration / samples * 1000
        # _log.debug("Slack: {}ms".format(slack))
        step = true_step / value
        _log.debug("Adjusting step speed {0:02.2f}Hz / {3:01.3}ms by play speed "
                   "{1:02.1f} to {2:02.2f}Hz."
                   .format(1000 / true_step, value, 1000 / step, true_step))
        self._step = step
        self._t.clear()

    @property
    def timeline(self):
        return self._timeline_df.index.values

    @timeline.setter
    def timeline(self, values):
        self._timeline_df["timeline"] = values

        # self.ui.edit_timestamp.setText(self._ts_format.format(values[0]))
        self.ui.slider_index.setMinimum(0)
        self.ui.slider_index.setMaximum(len(values) - 1)
        self.ui.slider_index.setTickInterval(600)
        self.ui.slider_index.setValue(0)

        self._set_play_speed(self.ui.doubleSpinBox.value())
        self.ui.doubleSpinBox.setMinimum(0.1)
        self.ui.doubleSpinBox.setMaximum(10)

    def playable_changed(self, timeline):
        _log.debug("Playable changed")

    ts_change = Signal(float)

    def _slider_pressed(self):
        self.pause()

    def _slider_value_changed(self, value):
        try:
            ts = self._timeline_df.loc[value, "timeline"]
            # ts = self.timestamps[value]
            self.ui.edit_timestamp.setText(self._ts_format.format(ts))

            self.ts_change.emit(ts)
        except IndexError as e:
            _log.debug(e)

    def play_pause(self):
        if self.__is_playing:
            self.pause()
        else:
            self.play()

    def pause(self):
        if not self.__is_playing:
            return
        self.ui.button_play_pause.setIcon(
            QIcon(":/player/icons/media-playback-start.svg")
        )
        self.__is_playing = False

    def play(self):
        if self.__is_playing:
            return
        self.ui.button_play_pause.setIcon(
            QIcon(":/player/icons/media-playback-pause.svg")
        )
        self.__is_playing = True
        # self._t0 = time.perf_counter_ns()
        self.advance()

    def step_back(self):
        self.pause()
        self.advance(reverse=True)

    def step_forward(self):
        self.pause()
        self.advance()

    def advance(self, reverse=False):
        if reverse:
            next_index = self.ui.slider_index.value() - 1
        else:
            next_index = self.ui.slider_index.value() + 1

        if (
            not self._timeline_df.index.values[0]
            <= next_index
            <= self._timeline_df.index.values[-1]
        ):

            # if self._t0 is not None:
            #     td = (time.perf_counter_ns() - self._t0) * 1.0e-9
            #     _log.debug("Took {0:03.3f} seconds".format(td))
            #
            #     samples = len(self.timeline)
            #     v = self._timeline_df["timeline"].values
            #     duration = v[-1] - v[0]
            #     speed_adjusted_duration = duration / self.ui.doubleSpinBox.value()
            #
            #     _log.debug("Duration: {}, with playspeed adjusted: {}".format(duration, speed_adjusted_duration))
            #     slack = (td - speed_adjusted_duration) / samples * 1000
            #     _log.debug("Slack per frame: {}ms".format(slack))

            self.pause()
            return

        self.ui.slider_index.setValue(next_index)
        if self.__is_playing:
            QTimer.singleShot(self._step - self.render_delay, self.advance)
            # self._t.append(time.perf_counter_ns())

            if len(self._t) >= self._filter_length:
                measured_step = np.median(np.diff(self._t) * 1.0e-6)
                delta = measured_step - self._step
                # _log.debug("Delta: {}".format(delta))
                if delta > 1:
                    d = np.abs(np.round(delta, 0))
                    _log.warning("Adjusting delay, Delta is  {}".format(delta))
                    if (self._step - self.render_delay - d) < 1:
                        _log.warning("Reached max possible speed.")
                    else:
                        self.render_delay += d
                        self._t.clear()
                elif delta < -1:
                        d = np.abs(np.round(delta, 0))
                        _log.warning("Adjusting delay, Delta is  {}".format(delta))
                        self.render_delay -= d
                        self._t.clear()


            self._t.append(time.perf_counter_ns())

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    qapp = QApplication([])

    CONFIG.debug = True

    p = PlaybackWidget()
    p.show()
    p.timestamps = np.arange(0, 1000, 12) * 141000

    qapp.exec_()
