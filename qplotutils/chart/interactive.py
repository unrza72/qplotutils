"""
Interactive Item
================

Item can be changed from the UI.

"""
import logging

from qtpy.QtCore import Signal, Qt, QPointF, QRectF, QLineF
from qtpy.QtGui import QPen, QBrush, QColor, QPainter
from qtpy.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem
from qplotutils.chart.items import ChartItemFlags, ChartWidgetItem

from .. import CONFIG

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2017, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)


class InteractiveChangeEvent(object):
    def __init__(self):
        self.position = None


class InteractiveVerticalLine(ChartWidgetItem):
    """ Vertical Line which can be moved by mouse interaction. Usefull for timelines. """

    positionChange = Signal(object)

    def __init__(self, parent=None):
        super(InteractiveVerticalLine, self).__init__(parent)
        self.setFlags(
            QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges
        )
        self.chartItemFlags = ChartItemFlags.FLAG_NO_AUTO_RANGE
        self.setZValue(1e6)

        self.setAcceptHoverEvents(True)

        self._x = None
        self._label = None

        self._pen = QPen(QBrush(Qt.green), 1.0, Qt.SolidLine)
        self._pen.setCosmetic(True)
        self._brush = QBrush(QColor(255, 255, 255, 0))

    @property
    def label(self):
        return self._label

    def setX(self, x, label=None, color=None):
        """ Sets the line's x value.

        :param x: abscissa value.
        :param label:
        :param color:
        """
        if label is not None:
            self._label = label

        if color is not None:
            self._color = color
            self._pen = QPen(QBrush(color), 1.0, Qt.SolidLine)
            self._pen.setCosmetic(True)
        # self._brush = QBrush(QColor(255, 255, 255, 0))

        if self._x != x:
            self._x = x
            self.setPos(QPointF(self._x, 0))

    def visibleRangeChanged(self, rect):
        t = self.parentItem().transform()
        bb = 4 / t.m11()
        _log.debug("{}, {} -> {}".format(rect.bottom(), rect.height(), bb))

        b = min(rect.bottom(), rect.top())
        self.b_rect = QRectF(-bb, b, 2 * bb, rect.height())
        self.prepareGeometryChange()

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        # p.setRenderHint(QPainter.Antialiasing)
        p.setPen(self._pen)
        p.setBrush(self._brush)

        p.drawLine(
            QLineF(QPointF(0, self.b_rect.bottom()), QPointF(0, self.b_rect.top()))
        )

        p.setPen(Qt.transparent)
        p.drawRect(self.b_rect)

        if CONFIG.debug:
            p.setPen(Qt.yellow)
            p.drawRect(self.b_rect)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            old_pos = self.pos()
            # value = value #.toPointF()

            e = InteractiveChangeEvent()
            e.position = value
            self.positionChange.emit(e)

            return QPointF(value.x(), old_pos.y())

        return super(InteractiveVerticalLine, self).itemChange(change, value)

    def hoverEnterEvent(self, e):
        super(InteractiveVerticalLine, self).hoverEnterEvent(e)
        self._brush = QBrush(QColor(255, 255, 255, 40))
        self.update()

    def hoverLeaveEvent(self, e):
        super(InteractiveVerticalLine, self).hoverLeaveEvent(e)
        self._brush = QBrush(QColor(255, 255, 255, 0))
        self.update()

    def __del__(self):
        _log.debug("Finalize Interactive vLine {}".format(self))
