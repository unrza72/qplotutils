#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User controls for interactivity.

"""
import logging
import time
from collections import deque

import numpy as np
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from qplotutils import CONFIG
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
    """ Playback for things that are considered realtime data. """

    data_changed = Signal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render_timestamp(self, ts):
        """ Slot that is called on change of the current timestamp.
        Simplest case when rendering on every timestamp is possible without
        to much computational effort.

        :param ts:
        :return:
        """
        pass

    def on_state_change(self, state):
        """ Gets notified whenever the play stae changes.
        Currently only playback / paused.
        Needed when the playback device is optimized for playback but
        on timestamp rendering is expensive or too slow

        :param state:
        :return:
        """
        pass

    def on_playback_speed_change(self, playback_speed):
        """ Gets notified when the playback speed changes

        :param playback_speed:
        :return:
        """
        pass

    def on_playback_timeline_change(self, timeline):
        """ Gets notified whenever the player timeline changes.

        :param timeline:
        :return:
        """
        pass


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

    class State(object):
        Playback = "playback"
        Paused = "paused"

    def __init__(self, parent=None):
        super(PlaybackWidget, self).__init__(parent)
        self.ui = Ui_PlaybackControl()
        self.ui.setupUi(self)

        # self._timeline_df = pd.DataFrame()
        self._timeline = np.array([])

        self.ui.button_play_pause.clicked.connect(self.play_pause)
        self.ui.button_back.clicked.connect(self.step_back)
        self.ui.button_next.clicked.connect(self.step_forward)

        self.ui.slider_index.valueChanged.connect(self._slider_value_changed)
        self.ui.slider_index.sliderPressed.connect(self._slider_pressed)
        # self.ui.edit_timestamp.textEdited.connect(self.jump_to_timestamp)
        self.ui.doubleSpinBox.valueChanged.connect(self._set_play_speed)

        self._is_playing = False
        self._ts_format = "{0:2.0f}"

        self.render_delay = 1  # ms accounted for rendering

        # State variables to monitor the actual playback-speed
        self._step = 0
        self._filter_length = 40
        self._t = deque(maxlen=self._filter_length)

        self._timeline_scaling_factor = 1.0E-6

    @property
    def timeline_scaling_factor(self):
        return self._timeline_scaling_factor

    @timeline_scaling_factor.setter
    def timeline_scaling_factor(self, value):
        self._timeline_scaling_factor = value

    def _set_play_speed(self, value):
        samples = len(self.timeline) - 1
        v = self.timeline * self.timeline_scaling_factor
        duration = v[-1] - v[0]  # in seconds

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
        """ List of timestamps.
        Pay attention to the timestamp scaling factor, default is 1.0E-6.
        Meaning the timeline is expected to be given in micro seconds.
        """
        return self._timeline

    @timeline.setter
    def timeline(self, values):
        self._timeline = values # _df["timeline"] = values

        # self.ui.edit_timestamp.setText(self._ts_format.format(values[0]))
        self.ui.slider_index.setMinimum(0)
        self.ui.slider_index.setMaximum(len(values) - 1)
        self.ui.slider_index.setTickInterval(600)
        self.ui.slider_index.setValue(0)

        self._set_play_speed(self.ui.doubleSpinBox.value())
        self.ui.doubleSpinBox.setMinimum(0.1)
        self.ui.doubleSpinBox.setMaximum(5)

    def register_playable(self, playable: IPlayable):
        _log.debug("Playable registered")

        name = playable.__module__ + "." +  playable.__class__.__name__

        # if name in self._timeline_df:
        #     # update df
        #
        # else:
        #     s = pd.Series(data=playable.)
        #
        #     self._timeline_df[name]


    def unregister_playable(self, playable: IPlayable):
        _log.debug("Playable un-registered")


    ts_change = Signal(float)

    def _slider_pressed(self):
        self.pause()

    def _slider_value_changed(self, value):
        try:
            ts = self.timeline[value]
            # ts = self.timestamps[value]
            self.ui.edit_timestamp.setText(self._ts_format.format(ts))

            self.ts_change.emit(ts)
        except IndexError as e:
            _log.debug(e)

    def play_pause(self):
        if self._is_playing:
            self.pause()
        else:
            self.play()

    def pause(self):
        if not self._is_playing:
            return
        self.ui.button_play_pause.setIcon(
            QIcon(":/player/icons/media-playback-start.svg")
        )
        self.ui.button_play_pause.setIconSize(QSize(32,32))
        self._is_playing = False

    def play(self):
        if self._is_playing:
            return
        self.ui.button_play_pause.setIcon(
            QIcon(":/player/icons/media-playback-pause.svg")
        )
        self.ui.button_play_pause.setIconSize(QSize(32, 32))
        self._is_playing = True
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

        if not (0 <= next_index <= len(self.timeline)):

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
        if self._is_playing:
            d = self._step - self.render_delay
            if d <= 0:
                d = 0
            QTimer.singleShot(d, self.advance)
            # self._t.append(time.perf_counter_ns())

            if d > 2 and  len(self._t) >= self._filter_length:
                measured_step = np.median(np.diff(self._t) * 1.0e-6)
                delta = measured_step - self._step
                # _log.debug("Delta: {}".format(delta))
                if delta > 2:
                    d = np.abs(np.round(delta, 0))
                    # _log.warning("Adjusting delay, Delta is  {}".format(delta))
                    if (self._step - self.render_delay - d) < 1:
                        _log.warning("Reached max possible speed.")
                    else:
                        self.render_delay += d
                        self._t.clear()
                elif delta < -2:
                        d = np.abs(np.round(delta, 0))
                        # _log.warning("Adjusting delay, Delta is  {}".format(delta))
                        self.render_delay -= d
                        self._t.clear()


            self._t.append(time.perf_counter_ns())
