#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__TODO__


"""
import logging
import sys
import os
import numpy as np
import unittest

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtOpenGL import *
from qtpy.QtWidgets import *

from qplotutils import CONFIG

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


class BenchTests(unittest.TestCase):

    app = None

    @classmethod
    def setUpClass(cls):
        BenchTests.app = QApplication([])

    def setUp(self):
        config = CONFIG
        config.debug_layout = True
        self.bench = Bench()


        self.bench.setWindowTitle("Bench Example 01")
        self.bench.resize(300, 400)
        self.bench.show()

    def test_add_docks(self):
        self.assertAlmostEquals(len(self.bench.docks), 0)

        # First dock
        dock_01 = Dock()
        self.bench.addDock(dock_01)

        # Second dock
        dock_02 = Dock(title="Dock 2")
        self.bench.addDock(dock_02)

        self.bench.repaint()  # try to cover paintEvent
        self.bench.update()

        self.assertAlmostEquals(len(self.bench.docks), 2)

    def test_close_dock(self):
        self.assertAlmostEquals(len(self.bench.docks), 0)

        # First dock
        dock_01 = Dock()
        self.bench.addDock(dock_01)

        # Second dock
        dock_02 = Dock(title="Dock 2")
        self.bench.addDock(dock_02)
        self.assertAlmostEquals(len(self.bench.docks), 2)

        dock_02.close()
        self.assertAlmostEquals(len(self.bench.docks), 1)

    def test_move_dock(self):
        # First dock
        dock_01 = Dock()
        self.bench.addDock(dock_01)

        # Second dock
        dock_02 = Dock(title="Dock 2")
        self.bench.addDock(dock_02, placement=Placement.BOTTOM, ref=dock_01)

        self.bench.dockMove(dock_01.uid, placement=Placement.TAB, ref_uid=dock_02.uid)

        d = dock_02.parentContainer.docks
        self.assertEqual(len(d), 2)

    def test_close_dock(self):
        # First dock
        dock_01 = Dock()
        self.bench.addDock(dock_01)

        # Second dock
        dock_02 = Dock(title="Dock 2")
        self.bench.addDock(dock_02, placement=Placement.BOTTOM, ref=dock_01)


        dock_01.close()
        self.assertEqual(len(self.bench.docks), 1)









