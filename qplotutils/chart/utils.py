#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qplotutils.chart_tests.utils
----------------------------

Utility classes to aid proper vizualization.
"""
import logging

from PyQt5.QtGui import QBrush
from qtpy.QtCore import Qt
from qtpy.QtGui import QPen

from . import LOG_LEVEL

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


def makePen(color, lineWidth=1.0, lineStyle=Qt.SolidLine, cosmetic=True):
    """ Creates and returns a pen.

    :param color: Any value, the `QColor <http://doc.qt.io/qt-4.8/qcolor.html#QColor>`_
        constructor takes as argument
    :param lineWidth: line width
    :param lineStyle: see `http://doc.qt.io/qt-4.8/qt.html#PenStyle-enum`
    :param cosmetic: When set to true the pens with is transformation invariant
    :return: The constructed pen
    :rtype: `QPen <http://doc.qt.io/qt-4.8/qpen.html>`_
    """
    # qColor = QColor(color)
    pen = QPen(color, lineWidth, lineStyle)
    pen.setCosmetic(cosmetic)

    return pen

def makeBrush(color, style=Qt.SolidPattern):
    brush = QBrush(
        color,
        style
    )
    return brush

class ChartColors(object):
    """ Color sets for line charts, e.g.  """

    Set1 = [
        "#e41a1c",
        "#377eb8",
        "#4daf4a",
        "#984ea3",
        "#ff7f00",
        "#ffff33",
        "#a65628",
        "#f781bf",
    ]

    Set2 = [
        "#b3e2cd",
        "#fdcdac",
        "#cbd5e8",
        "#f4cae4",
        "#e6f5c9",
        "#fff2ae",
        "#f1e2cc",
        "#cccccc",
    ]
