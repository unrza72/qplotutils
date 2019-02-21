#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__TODO__


"""
import logging
import numpy as np
import sys
import os
import weakref
import unittest

# from PyQt4.QtCore import *
# from PyQt4.QtGui import *

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.wireframe.base_types import Vector3d

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015 - 2018, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)


# class Vector3dTests(unittest.TestCase):
#
#     def test_base(self):
if __name__ == "__main__":

        v1 = Vector3d(1,0,0)
        v2 = Vector3d(0, 1, 0)

        v3 = Vector3d.fromiter(np.array([0, 0, 1]))

        # v4 = v1 + v2 + v3
        # print type(v4), v4
        #
        # v5 = v1 - v2
        # print type(v5), v5
        #
        # v6 = v1 * Vector3d(2,2,2)
        # print type(v6), v6
        #
        # v7 = np.dot(v1, v2)
        # print type(v7), v7

        v8 = v1.cross(v2)
        # print type(v8), v8

        # print v1.x, v3.z

        # print v2.norm

        v4 =  np.dot(v2, v1)
        # print v4

        v5 = np.cross(v1, v2)
        # print v5

        v6 = np.outer(v1, v2)
        # print v6