#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User controls for interactivity.

"""
import logging

import numpy as np
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from qplotutils import CONFIG
from .ui.playback import Ui_PlaybackControl

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015-2018, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


class PlaybackWidget(QWidget):
    """ Playback control widget with the following button
        * toggle playback / pause
        * advance one step forward
        * advance one step back

    The current timestamp is inidcated by slider and a line edit.

    Models / Visualization that choose to be controlled through the playback widget should
    connect to :meth:`qplotutils.player.PlaybackWidget.timestamp_changed`.
    """

    #: emited whenever the timestamp is changed.
    timestamp_changed = Signal(int, float)

    def __init__(self, parent=None):
        super(PlaybackWidget, self).__init__(parent)
        self.ui = Ui_PlaybackControl()
        self.ui.setupUi(self)

        self.__is_playing = False

        self.__timestamps = None
        self.__last_index = None

        self.ui.button_play_pause.clicked.connect(self.play_pause)
        self.ui.button_back.clicked.connect(self.step_back)
        self.ui.button_next.clicked.connect(self.step_forward)

        self.ui.slider_index.valueChanged.connect(self._slider_value_changed)
        self.ui.slider_index.sliderPressed.connect(self._slider_pressed)
        self.ui.edit_timestamp.textEdited.connect(self.jump_to_timestamp)

        if CONFIG.debug:
            self.timestamp_changed.connect(self.debug_slider)

    def jump_to_timestamp(self, text):
        try:
            _log.debug(text)
            ts = float(text)
            idx, = np.where(self.timestamps == ts)
            self.ui.slider_index.setValue(idx[0])
        except Exception as ex:
            _log.info("Could not set timestamp. Format no recognized or out of interval.")
            _log.debug("Exception %s", ex)

    def debug_slider(self, index, timestamp):
        _log.debug("{}: {}".format(index, timestamp))

    @property
    def timestamps(self):
        return self.__timestamps

    @timestamps.setter
    def timestamps(self, value):
        self.__timestamps = value
        self.__last_index = len(value)
        self.ui.slider_index.setMinimum(0)
        self.ui.slider_index.setMaximum(self.__last_index)
        self.ui.slider_index.setValue(0)

    def _slider_pressed(self):
        self.pause()

    def _slider_value_changed(self, value):
        ts = self.timestamps[value]
        self.ui.edit_timestamp.setText("{}".format(ts))
        self.timestamp_changed.emit(value, ts)

    def play_pause(self):
        if self.__is_playing:
            self.pause()
        else:
            self.play()

    def pause(self):
        if not self.__is_playing:
            return
        self.ui.button_play_pause.setIcon(QIcon(":/player/icons/media-playback-start.svg"))
        self.__is_playing = False

    def play(self):
        if self.__is_playing:
            return
        self.ui.button_play_pause.setIcon(QIcon(":/player/icons/media-playback-pause.svg"))
        self.__is_playing = True
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

        if not 0 < next_index < self.__last_index:
            self.pause()
            return

        self.ui.slider_index.setValue(next_index)
        if self.__is_playing:
            QTimer.singleShot(10, self.advance)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    qapp = QApplication([])

    CONFIG.debug = True

    p = PlaybackWidget()
    p.show()
    p.timestamps = np.arange(0, 1000, 12) * 141000

    qapp.exec_()
