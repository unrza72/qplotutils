#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========================
Test for qplotutils.player
==========================



Autogenerated package stub.
"""
import pytest
from pytestqt.qtbot import QtBot
import logging
import sys
import os
import numpy as np

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtOpenGL import *
from qtpy.QtWidgets import *

from qplotutils.player import *
from qplotutils.player import PlaybackWidget

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)


@pytest.fixture()
def dut(qtbot: QtBot):

    dut = PlaybackWidget()
    qtbot.addWidget(dut)
    dut.resize(800, 800)
    dut.show()
    return dut

class TestBirdview(object):

    def test_add_data(self):
        """ Tests for add_data
        
        """
        # Autogenerated test skeleton for add_data
        pass

    def test_render_ts(self):
        """ Tests for render_ts
        
        """
        # Autogenerated test skeleton for render_ts
        pass


class TestIBirdeyeItem(object):

    def test_boundingRect(self):
        """ Tests for boundingRect
        
        """
        # Autogenerated test skeleton for boundingRect
        pass

    def test_paint(self):
        """ Tests for paint
        
        """
        # Autogenerated test skeleton for paint
        pass

    def test_update_path(self):
        """ Tests for update_path
        
        """
        # Autogenerated test skeleton for update_path
        pass


class TestIPlayable(object):

    def test_render_ts(self):
        """ Tests for render_ts
        
        """
        # Autogenerated test skeleton for render_ts
        pass


class TestOsciPlayable(object):

    def test_add_data(self):
        """ Tests for add_data
        
        """
        # Autogenerated test skeleton for add_data
        pass

    def test_render_ts(self):
        """ Tests for render_ts
        
        """
        # Autogenerated test skeleton for render_ts
        pass


class TestPlaybackWidget(object):

    def test_set_play_speed(self, dut : PlaybackWidget):
        """ Tests for set_play_speed

        """
        # Autogenerated test skeleton for set_play_speed
        dut.timeline = np.arange(0, 120, 1 / 25) * 1.0E6
        dut._set_play_speed(2.)
        # step is in microseconds
        assert dut._step == 1 / 50. * 1000

    def test_timeline_scaling_factor(self, dut : PlaybackWidget):
        """ Tests for set_play_speed

        """
        # Autogenerated test skeleton for set_play_speed
        dut.timeline_scaling_factor = 1 # meaning format is in seconds
        dut.timeline = np.arange(0, 120, 1 / 25)
        dut._set_play_speed(2.)
        # step is in microseconds
        assert dut._step == 1 / 50. * 1000

    def test_slider_pressed(self,  dut : PlaybackWidget):
        """ Tests for slider_pressed

        """
        dut.timeline = np.arange(0, 120, 1 / 25)
        dut.play()
        assert dut._is_playing == True

        dut._slider_pressed()
        assert dut._is_playing == False



    def test_slider_value_changed(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for slider_value_changed

        """
        dut.timeline = np.arange(0, 120, 1 / 25)

        self.ts = None

        def ts_received(r):
            self.ts = r

        dut.ts_change.connect(ts_received)
        dut._slider_value_changed(10)

        assert self.ts is not None


    def test_advance(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for advance

        """
        dut.timeline = np.arange(0, 1, 1 / 25)
        dut.play()
        qtbot.wait(1200)
        assert dut.ui.slider_index.value() == len(dut.timeline) - 1

    def test_on_data_change(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for on_data_change

        """
        # Autogenerated test skeleton for on_data_change
        pass

    def test_pause(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for pause

        """
        dut.timeline = np.arange(0, 1, 1 / 25)
        dut.play()
        assert dut._is_playing
        qtbot.wait(20)
        dut.pause()
        assert not dut._is_playing
        qtbot.wait(20)
        dut.pause()
        assert not dut._is_playing

    def test_play(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for play

        """
        dut.timeline = np.arange(0, 1, 1 / 25)
        dut.play()
        assert dut._is_playing
        qtbot.wait(20)
        dut.play()
        assert dut._is_playing

    def test_play_pause(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for play_pause

        """
        dut.timeline = np.arange(0, 1, 1 / 25)
        dut.play_pause()
        assert dut._is_playing
        qtbot.wait(20)
        dut.play_pause()
        assert not dut._is_playing
        qtbot.wait(20)
        dut.play_pause()
        assert dut._is_playing

    def test_playable_changed(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for playable_changed

        """
        # Autogenerated test skeleton for playable_changed
        pass

    def test_step_back(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for step_back

        """
        # Autogenerated test skeleton for step_back
        pass

    def test_step_forward(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for step_forward

        """
        # Autogenerated test skeleton for step_forward
        pass

    def test_timeline(self, qtbot: QtBot, dut : PlaybackWidget):
        """ Tests for timeline

        """
        # Autogenerated test skeleton for timeline
        pass