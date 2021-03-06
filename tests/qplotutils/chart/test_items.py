#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================
Test for qplotutils.chart.items
===============================



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

from qplotutils.chart.items import *

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)


class BaseMixinTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = BaseMixin()  # TODO: may fail!


class ChartItemTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = ChartItem()  # TODO: may fail!


class ChartItemFlagsTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = ChartItemFlags()  # TODO: may fail!


class ChartItemGroupTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = ChartItemGroup()  # TODO: may fail!


class ChartWidgetItemTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = ChartWidgetItem()  # TODO: may fail!


class ColorSetTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = ColorSet()  # TODO: may fail!


class CoordCrossTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = CoordCross()  # TODO: may fail!


class HLineTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = HLine()  # TODO: may fail!


class LineChartItemTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = LineChartItem()  # TODO: may fail!


class RectMarkerTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = RectMarker(QPointF(0,0))  # TODO: may fail!


class TextItemTests(unittest.TestCase):

    app = None

    @classmethod
    def setUpClass(cls):
        TextItemTests.app = QApplication([])

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = TextItem(QPointF(0,0), "Text")  # TODO: may fail!


class VLineTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = VLine()  # TODO: may fail!


class WireItemTests(unittest.TestCase):

    def setUp(self):
        """ Autogenerated. """
        pass
        
    def test_instantiate(self):
        """ Autogenerated. """
        obj = WireItem()  # TODO: may fail!