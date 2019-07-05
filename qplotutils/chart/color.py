#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Color
-----

Color and gradient definitions as well as colormap and normalization
generic to all qplotutils chart_tests types.
"""
import logging

import numpy as np

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)

# Format is compatible with the one from matplotlib
_autumn_data = {
    "red": ((0.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    "green": ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
    "blue": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
    "alpha": ((0.0, 0.5, 0.5), (1.0, 1.0, 1.0)),
    "masked": (0, 0, 1, 1),
}

_test_data = {
    "red": ((0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 0.0, 0.0)),
    "green": ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
    "blue": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
}

_jet_data = {
    "red": ((0.0, 0, 0), (0.35, 0, 0), (0.66, 1, 1), (0.89, 1, 1), (1, 0.5, 0.5)),
    "green": (
        (0.0, 0, 0),
        (0.125, 0, 0),
        (0.375, 1, 1),
        (0.64, 1, 1),
        (0.91, 0, 0),
        (1, 0, 0),
    ),
    "blue": ((0.0, 0.5, 0.5), (0.11, 1, 1), (0.34, 1, 1), (0.65, 0, 0), (1, 0, 0)),
}


class Colormap(object):
    """ Maps a value to the defined gradient.
    The gradient definitions is backward compatible to the one MPL is using.
    See: `Matplotlib _cm.py <https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/_cm.py>`_
    """

    #: LUT default size
    N = 256

    def __init__(self, data=_autumn_data):
        """ Constructor.

        :param data: gradient definition dict
        """
        self.lut = np.zeros((self.N, 4), dtype=np.float)

        if "masked" in data:
            self.masked_color = data["masked"]
        else:
            self.masked_color = (1, 1, 1, 0)

        r = self.__channel_gradient(data["red"])
        g = self.__channel_gradient(data["green"])
        b = self.__channel_gradient(data["blue"])
        if "alpha" in data:
            a = self.__channel_gradient(data["alpha"])
        else:
            a = np.ones(r.shape)

        self.lut[:, 0] = r
        self.lut[:, 1] = g
        self.lut[:, 2] = b
        self.lut[:, 3] = a

    def __channel_gradient(self, d):
        c = np.zeros(self.N, dtype=np.float)

        for l, r in zip(d[0:-1], d[1:]):
            l_idx = self.lut_index(l[0])
            l_sv = l[1]
            l_v = l[2]

            r_idx = self.lut_index(r[0])
            r_v = r[1]
            r_ev = r[2]

            c[l_idx:r_idx] = l_sv + (r_v - l_v) / (r_idx - l_idx * 1.0) * np.arange(
                0, r_idx - l_idx
            )
            c[r_idx] = r_ev

        return c

    @classmethod
    def lut_index(cls, v):
        if not 0 <= v <= 1:
            raise Exception("Value not normalized")
        return int(np.round(v * (cls.N - 1), 0))

    def __call__(self, v):
        if np.ma.is_masked(v):
            _log.debug("Masked")
            return self.masked_color

        idx = self.lut_index(v)
        return self.lut[idx, :]


class Normalize(object):
    def __init__(self, value_min, value_max, lower_bound=0.0, upper_bound=1.0):
        self.value_min = value_min
        self.value_max = value_max

    def __call__(self, values, dtype=np.float32):
        # if not self.value_min <= values <= self.value_max:
        #     return np.NaN  # Colormap can decide to what to do with these values
        out_of_bounds_greater = np.ma.masked_greater(values, self.value_max)
        out_of_bounds_less = np.ma.masked_less(values, self.value_min)

        invalids = np.logical_or(
            np.ma.getmask(out_of_bounds_less), np.ma.getmask(out_of_bounds_greater)
        )

        valid = np.ma.array(values, mask=invalids, dtype=dtype, copy=True)

        if self.value_max == self.value_min:
            return 0.5

        result = (valid - self.value_min) / (self.value_max - self.value_min * 1.0)
        return result
