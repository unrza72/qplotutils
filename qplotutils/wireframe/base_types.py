#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__TODO__


"""
import os
import sys
import logging
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtOpenGL import *
from qtpy.QtWidgets import *

import numpy as np

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015 - 2018, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)


class Vector3d(np.ndarray):

    @classmethod
    def fromiter(cls, v):
        return Vector3d(v[0], v[1], v[2])

    def __new__(cls, x,y,z): # , info=None):
        obj = np.asarray([x, y, z]).view(cls)
        return obj

    def __init__(self, x, y, z):
        super(Vector3d, self).__init__() # x,y,z)

    # def __array_finalize__(self, obj):
    #     print('In __array_finalize__:')
    #     print('   self is %s' % repr(self))
    #     print('   obj is %s' % repr(obj))
    #     # if obj is None: return
    #     # self.info = getattr(obj, 'info', None)

    # def __array_wrap__(self, out_arr, context=None):
    #     print('In __array_wrap__:')
    #     print('   self is %s' % repr(self))
    #     print('   arr is %s' % repr(out_arr))
    #     # then just call the parent
    #     return super(Vector3d, self).__array_wrap__(self, out_arr, context)

    # def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
    #     print "In ufunc", ufunc, method, inputs, kwargs
    #
    #     return super(Vector3d, self).__array_ufunc__(ufunc, method, *inputs, **kwargs)

    def __str__(self):
        return "<Vector3d x={}, y={}, z={}>".format(self[0], self[1], self[2])

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = value

    @property
    def norm(self):
        return np.linalg.norm(self)

    def normalize(self):
        return self / self.norm

    def cross(self, b):
        return self.fromiter(np.cross(self, b))