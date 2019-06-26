#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
======================================
Test for qplotutils.chart.scatter_plot
======================================



Autogenerated package stub.
"""
import unittest
import logging
import sys
import os
import numpy as np

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtOpenGL import *
from qtpy.QtWidgets import *

from qplotutils.chart.scatter_plot import *

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)


class ColorbarTests(unittest.TestCase):

    app = None

    @classmethod
    def setUpClass(cls):
        ColorbarTests.app = QApplication([])

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = Colorbar(Colormap(), 0, 10)  # TODO: may fail!


class ScatterItemTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = ScatterItem(0,0)  # TODO: may fail!


class ScatterPlotViewTests(unittest.TestCase):

    app = None

    @classmethod
    def setUpClass(cls):
        ScatterPlotViewTests.app = QApplication([])


    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = ScatterPlotView(Colormap())  # TODO: may fail!