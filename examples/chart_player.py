#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart with two horizontal axes
------------------------------

"""
import os
import sys
import numpy as np
import pandas as pd

import logging

PKG_DIR = os.path.abspath(os.path.join(__file__, "..", ".."))

print(PKG_DIR)
if PKG_DIR not in sys.path:
    sys.path.append(PKG_DIR)


__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


if __name__ == "__main__":

    idx1 = np.arange(1, 10, 1)
    v1 = np.ones(idx1.shape)

    p1 = pd.DataFrame(index=idx1)
    p1["v1"] = v1

    idx2 = np.arange(1, 10, 0.41)
    v2 = np.ones(idx2.shape) * 2

    p2 = pd.DataFrame(index=idx2)
    p2["v2"] = v2

    ts_merge = pd.merge(p1, p2, left_index=True, right_index=True, how="outer")

    print(p1.head(), p2.head())
    print(ts_merge.head(20))

    ts_merge.reindex()
