#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=========================
Test for qplotutils.bench
=========================



Autogenerated package stub.
"""
import os
import sys

import pytest

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)

from qplotutils.common import *

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)


class TestVector2(object):
    def test_init(self):
        v = Vector2(1, 2)
        assert v is not None
        assert v.x == 1
        assert v.y == 2
        assert str(v).startswith("<Vector2:")

    def test_from_iter(self):
        v = Vector2.fromiter([1, 2])
        assert v is not None

        # Wrong length
        with pytest.raises(ValueError):
            Vector2.fromiter([1, 2, 4, 5, 6])

        v = Vector2.fromiter((1, 2))
        assert v is not None

        v = Vector2.fromiter(np.array([1, 2]))
        assert v is not None

        # String missuse
        with pytest.raises(ValueError):
            Vector2.fromiter("ab")

    def test_setter(self):
        v = Vector2.fromiter([1, 2])
        v.x = 0
        v.y = 0

        assert v.norm == 0

    def test_add(self):
        v1 = Vector2(1, 2)
        v2 = Vector2(1.1, 3)

        v3 = v1 + v2
        assert isinstance(v3, Vector2)
        assert v3.x == 2.1
        assert v3.y == 5

    def test_vector_mul(self):
        # dot product
        v1 = Vector2(1, 2)
        v2 = Vector2(1.1, 3)

        v3 = v1 * v2
        assert isinstance(v3, Vector2)
        assert v3.x == 1 * 1.1
        assert v3.y == 2 * 3

        # scalar multiplication
        v4 = v1 * -2
        assert isinstance(v4, Vector2)
        assert v4.x == 1 * -2
        assert v4.y == 2 * -2

    def test_rotate(self):
        v1 = Vector2(1, 0)
        v2 = v1.rotate(45 * np.pi / 180)
        assert isinstance(v2, Vector2)
        assert v2.x == np.sqrt(2) / 2
        assert v2.y - np.sqrt(2) / 2 < 0.0000001

    def test_angle(self):
        v1 = Vector2(1, 0)
        v2 = v1.rotate(45 * np.pi / 180)

        angle = v1.angle(v2)
        assert angle == -45 * np.pi / 180

        v2 = Vector2(0, 0)
        angle = v1.angle(v2)
        assert angle == 0

    def test_unit_vector(self):
        v = Vector2(0, 5)
        assert v.unit_vector.x == 0
        assert v.unit_vector.y == 1


class TestVector3(object):
    def test_init(self):
        v = Vector3(1, 2, 3)
        assert isinstance(v, Vector3)
        assert v.x == 1
        assert v.y == 2
        assert v.z == 3

        assert str(v).startswith("<Vector3:")

    def test_from_iter(self):
        v = Vector3.fromiter([1, 2, 3])
        assert isinstance(v, Vector3)
        assert v.x == 1
        assert v.y == 2
        assert v.z == 3

    def test_setter(self):
        v = Vector3.fromiter([1, 2, 3])
        v.x = 0
        v.y = 0
        v.z = 0

        assert v.norm == 0

    def test_norm(self):
        v = Vector3(3, 0, 0)
        assert v.norm == 3.0

        v_u = v.unit_vector
        assert v_u.norm == 1
        assert v_u.x == 1

    def test_cross(self):
        v1 = Vector3(1, 0, 0)
        v2 = Vector3(0, 1, 0)

        v3 = v1.cross(v2)
        assert v3.z == 1
