#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit test for the playback widget.

"""
import logging
import sys
import os
import numpy as np
import unittest

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qplotutils import CONFIG
from qplotutils.player import PlaybackWidget

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.bench import Bench, Dock, Placement

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015 - 2018, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)


class PlaybackTests(unittest.TestCase):

    app = None

    @classmethod
    def setUpClass(cls):
        PlaybackTests.app = QApplication([])

    def setUp(self):
        config = CONFIG
        config.debug_layout = True
        self.player = PlaybackWidget()

    def test_stub(self):
        pass









