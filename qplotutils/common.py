#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qplotutils.bench
----------------

Widgets to create IDE like workbenches with dock widgets that can be rearanged and resized freely.
"""
import logging
import numpy as np
import math
from collections.abc import Iterable

from qtpy.QtCore import Qt, QPointF

from qplotutils import QPlotUtilsException
from . import LOG_LEVEL, MIME_TYPE, CONFIG

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)
_log.setLevel(LOG_LEVEL)


class Vector3(np.ndarray):
    @classmethod
    def fromiter(cls, v):
        return Vector3(v[0], v[1], v[2])

    def __new__(cls, x, y, z):  # , info=None):
        obj = np.asarray([x, y, z], dtype=np.float).view(cls)
        return obj

    def __init__(self, x, y, z):
        super(Vector3, self).__init__()  # x,y,z)

    def __str__(self):
        return "<Vector3: x={}, y={}, z={}>".format(self[0], self[1], self[2])

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
        """ Euclidian norm """
        return np.linalg.norm(self)

    @property
    def unit_vector(self):
        return self / self.norm

    def cross(self, b):
        """ Returns the cross product with other vector3.

        :param b:
        :return:
        """
        return self.fromiter(np.cross(self, b))


class Vector2(np.ndarray):
    """ Representation of a 2-d vector.
    Acts as a bridge between Qt's QpointF and numpy.
    """

    @classmethod
    def fromiter(cls, v):
        if not isinstance(v, Iterable) or len(v) != 2:
            msg = "Cannot build vector from non-iterable or length other than 2."
            raise ValueError(msg)
        return Vector2(v[0], v[1])

    def __new__(cls, x, y):
        obj = np.asarray([x, y], dtype=np.float).view(cls)
        return obj

    def __init__(self, x, y):
        super(Vector2, self).__init__()

    def __str__(self):
        return "<Vector2: x={}, y={}>".format(self[0], self[1])

    def rotate(self, a):
        """ Rotates the vector by given value in radians.

        :param a: rotation in radians
        :return: rotated point as Vec2
        """
        rotation_matrix = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        result = self.fromiter(np.dot(rotation_matrix, self))
        return result

    def angle(self, other):
        """ Calculates the inner angle between self and the other vector with directionality.

        :param other: Vec2
        :return: rotation in radians with directionality
        """
        if 0 in [self.norm, other.norm]:
            _log.debug("Zero vector provided")
            return 0

        v = np.dot(self, other) / (self.norm * other.norm)
        if not -1 <= v <= 1:
            # May happen due to floating point rounding
            return 0
        delta = np.arccos(v)

        # cross product to determine the turning direction
        k = np.cross(other, self)
        _log.debug("Change by {}, {}".format(delta * 180 / np.pi, k))
        v = np.sign(k) * delta

        return v

    @property
    def x(self):
        """ X coordinate. """
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        """ Y coordinate. """
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def norm(self):
        """ Euclidian norm """
        return np.linalg.norm(self)

    @property
    def unit_vector(self):
        return self / self.norm

    @property
    def qpointF(self):
        """ Returns a QpointF representation.

        :return: QPointF
        """
        return QPointF(self[0], self[1])

    @classmethod
    def fromQpointF(cls, qp):
        """ Initializes Vec from QPointF

        :param qp: QPointF
        :return: a Vec2
        """
        return Vector2(qp.x(), qp.y())

    # def __add__(self, other):
    #     """ Vector addition.
    #
    #     :param other:
    #     :return:
    #     """
    #     # Element-wise addition
    #     result = Vec2()
    #     result._v = self.array * other.array
    #     return result
    #
    # def __sub__(self, other):
    #     """ Vector substraction
    #
    #     :param other:
    #     :return:
    #     """
    #     # Element-wise subtraction
    #     result = Vec2()
    #     result._v = self.array * other.array
    #     return result
    #
    # def __mul__(self, scalar_or_vec2):
    #     """ Either scalar multiplication in case of other is a scalar, or in case of other Vec2 the
    #     Hadamard product.
    #
    #     The Hadamard product is used to scale handle very easily.
    #     TODO: Kinda dirty...
    #
    #     :param scalar_or_vec2: scalar or vec2
    #     :return: Vec2
    #     """
    #     # Very unclean
    #     result = Vec2()
    #     if isinstance(scalar_or_vec2, Vec2):
    #         # hadamard
    #         result._v = self.array * scalar_or_vec2.array
    #     else:
    #         # Multiply by scalar
    #         result._v = self.array * scalar_or_vec2
    #     return result
