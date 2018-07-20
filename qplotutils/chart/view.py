"""
qplotutils.chart.view
---------------------

Base widget that provides the view for all charts including axis, legend and zooming and panning capabilities.
"""
import math
import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from .. import CONFIG
from . import LOG_LEVEL
from .utils import makePen
from .items import ChartItem, ChartItemFlags

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2015 - 2018, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"


_log = logging.getLogger(__name__)
_log.setLevel(LOG_LEVEL)


class Style(object):
    """ Borg for global styling.

    TODO: Not yet implemented
    """
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        self.grid_color = QColor(90, 90, 90, 255)


class ChartLegend(ChartItem):
    """ Legend for chart views. """

    def __init__(self):
        """ Displays the chart item in a legend table. """
        super(ChartLegend, self).__init__()  # Pycharm / pyLint inspection error. Please ignore
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIgnoresTransformations)

        self._picture = None
        self._bRect = QRectF(0, 0, 200, 50)

        self._entries = []

        self.font = QFont("Helvetica [Cronyx]", 10, QFont.Normal)
        self.fontFlags = Qt.TextDontClip | Qt.AlignLeft | Qt.AlignVCenter
        self.setVisible(False)

    def addEntry(self, chart_item):
        """ Slot. Adds an entry for the given chart item to the legend.

        :param chart_item:
        """
        _log.debug("Add entry chart item: {}".format(chart_item.label))
        self._entries.append(chart_item)

        self._updateBoundingRect()
        self._updatePicture()

        # self.setVisible(True)

    def removeEntry(self, chart_item):
        """ Slot. Removes the entry for the given chart item to the legend.

        :param chart_item: chart item such as line chart item, e.g.
        """

        _log.debug("Remove chart item entry: {}".format(chart_item.label))
        self._entries.remove(chart_item)

        self._updateBoundingRect()
        self._updatePicture()

    def _updateBoundingRect(self):
        metrics = QFontMetrics(self.font)
        runWidth = 0

        for entry in self._entries:

            # (text, color, width, tick) = entry
            if entry.label is not None:
                w = metrics.width(entry.label)
                if w > runWidth:
                    runWidth = w

        self._bRect.setWidth(runWidth + 40)
        self._bRect.setHeight(len(self._entries) * 20 + 8)

    def _updatePicture(self):
        self._picture = QPicture()
        painter = QPainter(self._picture)
        self._generatePicture(painter)
        painter.end()

    def _generatePicture(self, p=QPainter()):
        p.setPen(QPen(QColor("#aaaaaa")))
        p.setBrush(QBrush(QColor(255, 255, 255, 80), Qt.SolidPattern))
        p.drawRoundedRect(self._bRect, 2, 2)

        for k, entry in enumerate(self._entries):
            # (text, color, width, tick) = entry

            p.setBrush(QBrush(entry.color, Qt.SolidPattern))
            p.setPen(QPen(Qt.transparent))

            p.drawRect(6, 8 + k * 20, 11, 11)

            p.setBrush(QBrush(Qt.transparent))
            p.setPen(QPen(QColor("#FFFFFF")))
            tickRect = QRectF(24, 8 + k * 20, self._bRect.width() - 24, 11)
            p.drawText(tickRect, self.fontFlags, "{}".format(entry.label))

    def boundingRect(self):
        return self._bRect

    def shape(self):
        path = QPainterPath()
        path.addRect(self._bRect)
        return path

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        if self._picture is None:
            return
        self._picture.play(p)

    def __del__(self):
        _log.debug("Finalizing: {}".format(self))


class ChartView(QGraphicsView):
    """ Widget that display chart items.
    """

    #: point of origin upper left corner, x axis to the right, y axis to the bottom
    DEFAULT_ORIENTATION = QTransform(1, 0, 0, 1, 0, 0)

    #: point of origin lower left corner, x axis to the right, y axis to the top
    CARTESIAN = QTransform(1, 0, 0, -1, 0, 0)

    #: point of origin lower right corner, x axis to the top, y axis to the left
    AUTOSAR = QTransform(0, -1, -1, 0, 0, 0)

    #: Reference corner for map keys (e.g. legend)
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


    def __init__(self, parent=None, orientation=DEFAULT_ORIENTATION):
        super(ChartView, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFrameShape(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)

        self.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.on_context_menu)

        self.setAcceptDrops(False)

        scene = QGraphicsScene()
        self.setScene(scene)

        self.centralWidget = ChartWidget()
        self.scene().addItem(self.centralWidget)

        b_rect = QRectF(0, 0, self.size().width() - 2, self.size().height() - 2)
        self.centralWidget.setGeometry(b_rect)

        self.setBackgroundBrush(QBrush(Qt.black, Qt.SolidPattern))

        self.centralWidget.area.getRootItem().setTransform(orientation)

        self._map_keys = []

        # Legend
        self._make_legend()

        # Toggle chart legend
        self.legendAction = QAction("Legend", self)
        self.legendAction.setCheckable(True)
        self.legendAction.triggered.connect(self.__toggle_legend)

        # Force aspect ratio
        self.apect1by1Action = QAction("Aspect ratio 1:1", self)
        self.apect1by1Action.setCheckable(True)
        self.apect1by1Action.toggled.connect(self.__toggle_apect1by1)

        self._dbg_box_color = Qt.blue

    def __toggle_legend(self, checked):
        self._legend.setVisible(checked)

    def resizeEvent(self, event):
        b_rect = QRectF(0, 0, self.size().width() - 3, self.size().height() - 3)
        self.centralWidget.setGeometry(b_rect)
        # self.autoRange()
        self.centralWidget.area.axisChange()
        self.__layout_map_keys()

    def __layout_map_keys(self):
        a = self.centralWidget.area.size()
        b = self.centralWidget.area.pos()

        for r in self._map_keys:
            c, dx, dy, item = r["corner"], r["x"], r["y"], r["Item"]
            if c == self.TOP_RIGHT:
                x = self.width() - item.boundingRect().width() - dx
                y = dy
            elif c == self.BOTTOM_LEFT:
                x = b.x() + dx
                y = b.y() + a.height() - item.boundingRect().height() - dy
            elif c == self.BOTTOM_RIGHT:
                x = self.width() - item.boundingRect().width() - dx
                y = b.y() + a.height() - item.boundingRect().height() - dy
            else:
                x = dx
                y = dy

            item.setPos(x, y)

    def showEvent(self, event):
        self.centralWidget.area.axisChange()
        self.__layout_map_keys()

    def setCoordinatesOrientation(self, orientation=DEFAULT_ORIENTATION):
        self.centralWidget.area.getRootItem().setTransform(orientation)
        self.centralWidget.area.axisChange()

    def setVisibleRange(self, rect):
        self.centralWidget.area.setRange(rect)

    def addItem(self, item=ChartItem()):
        item.setParentItem(self.centralWidget.area.getRootItem())
        self.centralWidget.area.visibleRangeChange.connect(item.visibleRangeChanged)
        # self.connect(self.centralWidget.area, SIGNAL("visibleRangeChange"), item.visibleRangeChanged)

        if not item.chartItemFlags & ChartItemFlags.FLAG_NO_LABEL:
            self.legend.addEntry(item)

    def removeItem(self, item):
        if self.legend and not item.chartItemFlags & ChartItemFlags.FLAG_NO_LABEL:
            self.legend.removeEntry(item)
        item.setParentItem(None)

    def _make_legend(self):
        legend = ChartLegend()
        self.scene().addItem(legend)

        # parent_w = self.size().width()
        # legend.setPos(parent_w - legend.boundingRect().width() - 15, 40)
        # return legend
        self._map_keys.append({
            "corner": self.TOP_RIGHT,
            "x": 10,
            "y": 10,
            "Item": legend,
        })

    def autoRange(self):
        self.centralWidget.area.autoRange()

    def setRange(self, rect):
        self.centralWidget.area.setRange(rect)

    def __toggle_apect1by1(self, checked):
        _log.debug("Aspect 1:1")
        if checked:
            self.centralWidget.area.setAspectRatio(1.0)

        else:
            self.centralWidget.area.setAspectRatio(None)

    @property
    def aspectRatio(self):
        return self.centralWidget.area.aspectRatio

    def setAspectRatio(self, value):
        self.centralWidget.area.setAspectRatio(value)

    def setLegendVisible(self, visible, corner=TOP_RIGHT):
        if visible:
            self._map_keys[0]["corner"] = corner
            self.__layout_map_keys()

        self._map_keys[0]["Item"].setVisible(visible)

    @property
    def legend(self):
        return self._map_keys[0]["Item"]

    def add_chart_key(self, key_item, corner):
        self.scene().addItem(key_item)
        self._map_keys.append({
            "corner": corner,
            "x": 10,
            "y": 10,
            "Item": key_item,
        })
        self.__layout_map_keys()

    # @property
    # def legend(self):
    #     return self._legend.isVisible()
    #
    # @legend.setter
    # def legend(self, value):
    #     # TODO: legend should track its position by itself and relative to parent
    #     parent_w = self.size().width()
    #     self._legend.setPos(parent_w - self._legend.boundingRect().width() - 15, 40)
    #     self._legend.setVisible(value)

    def setMaxVisibleRange(self, rect):
        self.centralWidget.area.setMaxVisibleRange(rect)

    @property
    def title(self):
        return self.centralWidget.title

    @title.setter
    def title(self, value):
        self.centralWidget.title = value
        self.__layout_map_keys()

    @property
    def horizontalLabel(self):
        return self.centralWidget.horizontalLabel

    @horizontalLabel.setter
    def horizontalLabel(self, value):
        self.centralWidget.horizontalLabel = value
        self.__layout_map_keys()

    @property
    def verticalLabel(self):
        return self.centralWidget.verticalLabel

    @verticalLabel.setter
    def verticalLabel(self, value):
        self.centralWidget.verticalLabel = value
        self.__layout_map_keys()

    def __repr__(self):
        return "<ChartView>"

    def __del__(self):
        _log.debug("Finalizing: {}".format(self))


class ChartWidget(QGraphicsWidget):
    """ Provides the base layout and adds the axis to bottom and left side.

    .. note:: Is instantiated and connected by the parent chart view.

    :param parent: the Chart view
    """
    def __init__(self, parent=None):

        super(ChartWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setLayout(QGraphicsGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setHorizontalSpacing(-1)
        self.layout().setVerticalSpacing(-1)

        # optional title
        self.title_widget = ChartLabel(self)
        self.title_widget.font = QFont("Helvetica [Cronyx]", 14, QFont.Bold)
        self.layout().addItem(self.title_widget, 0, 0, 1, 3)
        self.layout().setRowFixedHeight(0, 0)
        self.title_widget.setVisible(False)


        # optional left axis label
        self.vertical_axis_label = VerticalChartLabel(self)
        self.layout().addItem(self.vertical_axis_label, 1, 0)
        self.layout().setColumnFixedWidth(0, 0)
        self.vertical_axis_label.setVisible(False)

        self.main_vertical_axis = VerticalAxis(self)
        self.layout().addItem(self.main_vertical_axis, 1, 1)
        self.layout().setColumnFixedWidth(1, 60)

        self.main_horizontal_axis = HorizontalAxis(self)
        self.layout().addItem(self.main_horizontal_axis, 2, 2)
        self.layout().setRowFixedHeight(2, 30)

        # optional bottom axis label
        self.horizontal_axis_label = ChartLabel(self)
        self.layout().addItem(self.horizontal_axis_label, 3, 1, 1, 2)
        self.layout().setRowFixedHeight(3, 0)
        self.horizontal_axis_label.setVisible(False)

        # canvas for the items
        self.area = ChartArea(self)
        self.layout().addItem(self.area, 1, 2)

        self.area.vAxisChange.connect(self.main_vertical_axis.axisChange)
        self.area.hAxisChange.connect(self.main_horizontal_axis.axisChange)

        self._dbg_box_color = Qt.green

    @property
    def title(self):
        return self.title_widget.label

    @title.setter
    def title(self, value):
        if value is None:
            self.title_widget.setVisible(False)
            self.layout().setRowFixedHeight(0, 0)
        else:
            self.title_widget.label = value
            self.title_widget.setVisible(True)
            self.layout().setRowFixedHeight(0, 20)

    @property
    def verticalLabel(self):
        return self.vertical_axis_label.label

    @verticalLabel.setter
    def verticalLabel(self, value):
        if value is None:
            self.vertical_axis_label.setVisible(False)
            self.layout().setColumnFixedWidth(0, 0)
        else:
            self.vertical_axis_label.label = value
            self.vertical_axis_label.setVisible(True)
            self.layout().setColumnFixedWidth(0, 20)

    @property
    def horizontalLabel(self):
        return self.horizontal_axis_label.label

    @horizontalLabel.setter
    def horizontalLabel(self, value):
        if value is None:
            self.horizontal_axis_label.setVisible(False)
            self.layout().setRowFixedHeight(3, 0)
        else:
            self.horizontal_axis_label.label = value
            self.horizontal_axis_label.setVisible(True)
            self.layout().setRowFixedHeight(3, 20)

    def addSecondaryHorizontalAxis(self, axis):
        """ Adds a second horizontal axis on top to the plot.

        :param axis: secondary Axis
        :return:
        """
        axis.setParent(self)

        # Unfortunately we need to re-layout everything
        self.layout().removeItem(self.main_vertical_axis)
        self.layout().removeItem(self.main_horizontal_axis)
        self.layout().removeItem(self.area)

        self.layout().addItem(axis, 0, 1)
        self.layout().setRowFixedHeight(0, 30)
        self.area.hAxisChange.connect(axis.axisChange)

        self.layout().addItem(self.main_vertical_axis, 1, 0)
        self.layout().setColumnFixedWidth(0, 60)

        self.layout().addItem(self.area, 1, 1)

        self.layout().addItem(self.main_horizontal_axis, 2, 1)
        self.layout().setRowFixedHeight(2, 30)



    def boundingRect(self):
        b_rect = QRectF(0, 0, self.size().width(), self.size().height())
        return b_rect

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        if CONFIG.debug:
            # b_rect = QRectF(0, 0, self.size().width(), self.size().height())
            p.setPen(QPen(self._dbg_box_color))
            p.drawRect(self.boundingRect())

    def __repr__(self):
        return "<ChartWidget>"

    def __del__(self):
        _log.debug("Finalizing: {}".format(self))

    def wheelEvent(self, e):
        e.accept()  # but do nothing
        _log.debug("Wheel on axis is ignored")


class ChartLabel(QGraphicsWidget):

    def __init__(self, label="", parent=None):
        super(ChartLabel, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setFlags(QGraphicsItem.ItemClipsChildrenToShape)  # | QGraphicsItem.ItemIsFocusable)

        self.font = QFont("Helvetica [Cronyx]", 11, QFont.Normal)
        self.font_flags = Qt.TextDontClip | Qt.AlignHCenter | Qt.AlignVCenter
        self.color = QColor(110, 110, 110, 255)

        self.label = label

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        p.setRenderHint(QPainter.Antialiasing, False)
        if self._picture is None:
            self._refreshPicture()
        self._picture.play(p)

        if CONFIG.debug:
            p.setPen(QPen(self._dbg_box_color))
            p.drawRect(self.boundingRect())

    def _refreshPicture(self):
        """ Repaints the picture that is played in the paint method. """
        self._picture = QPicture()
        painter = QPainter(self._picture)
        self._generatePicture(painter)
        painter.end()

    def resizeEvent(self, event):
        _log.debug("Resize Event")
        self._refreshPicture()

    def _generatePicture(self, p=QPainter()):
        p.setBrush(QBrush(Qt.transparent))
        p.setPen(QPen(self.color))
        p.setFont(self.font)
        p.drawText(self.boundingRect(), self.font_flags, "{}".format(self.label))

    def __repr__(self):
        return "<ChartLabel>"

    def __del__(self):
        _log.debug("Finalizing: {}".format(self))


class VerticalChartLabel(ChartLabel):

    def __init__(self, label="", parent=None):
        super(VerticalChartLabel, self).__init__(label, parent)

    def _generatePicture(self, p=QPainter()):
        r = self.boundingRect()
        p.rotate(-90)
        rr = QRectF(-r.height(), 0, r.height(), r.width())

        if CONFIG.debug:
            p.setPen(QPen(Qt.red))
            p.drawRect(rr)

        p.setBrush(QBrush(Qt.transparent))
        p.setPen(QPen(self.color))
        p.setFont(self.font)
        p.drawText(rr, self.font_flags, "{}".format(self.label))
        p.rotate(90)


class ChartAxis(QGraphicsWidget):
    """ Base implementation for all chart axes.

     :param parent: a chart widget.
     """
    def __init__(self, parent=None):

        super(ChartAxis, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setFlags(QGraphicsItem.ItemClipsChildrenToShape) #  | QGraphicsItem.ItemIsFocusable)

        self.font = QFont("Helvetica [Cronyx]", 11, QFont.Normal)
        self.flags = Qt.TextDontClip | Qt.AlignRight | Qt.AlignVCenter
        self.gridColor = QColor(80, 80, 80, 255)

        self.tickFormat = "{0:G}"

        self._areaTransform = None
        self._picture = None

        self._dbg_box_color = Qt.yellow


    def boundingRect(self):
        return QRectF(QPointF(0, 0), self.size())

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        p.setRenderHint(QPainter.Antialiasing, False)
        if self._picture is None:
            self._refreshPicture()
        self._picture.play(p)

        if CONFIG.debug:
            p.setPen(QPen(self._dbg_box_color))
            p.drawRect(self.boundingRect())

    def _refreshPicture(self):
        """ Repaints the picture that is played in the paint method. """
        self._picture = QPicture()
        painter = QPainter(self._picture)
        self._generatePicture(painter)
        painter.end()

    def resizeEvent(self, event):
        _log.debug("Resize Event")
        self._refreshPicture()

    def axisChange(self, transform):
        # _log.debug("Axis change: {}".format(transform))
        self._areaTransform = transform
        self._refreshPicture()
        self.update()

    def _generatePicture(self, p=QPainter()):
        p.setPen(QPen(Qt.green))
        p.drawRect(self.boundingRect())

    def calcTicks(self, shift, scaling, displayRange, maxGridSpace=80, minGridSpace=40):
        """ Calculates the axis ticks.
         The ticks are calculated along the logarithm of the base 10 of the displayed value range.
         The resulting exponent for the ticks is than scaled with respect to the preferred number of
         ticks and the value range.
         In case the value range would cause more ticks as previously determined the exponent is incremented
         by 1. Otherwise if the exponent results in to less ticks, the exponent is divided by 2.

        :param shift: offset from point of origin along the current axis (m31 / m32 from transform)
        :param scaling: scaling of scene (m11 / m12 / m21 / m22 from transform)
        :param displayRange: range of visible pixels
        :param maxGridSpace: maximum space between gridlines
        :param minGridSpace: minimum space between gridlines
        :return: list of ticks (tuple of position and label) and the required tick with
        """
        # first lets see how many ticks can be placed on the axis
        minNumberOfGridLines = displayRange / float(maxGridSpace)
        maxNumberOfGridLines = displayRange / float(minGridSpace)

        # Calculate the up most and lowest value on axis
        upperValue = -shift / scaling
        lowerValue = (displayRange - shift) / scaling

        valueRange = abs(upperValue - lowerValue)
        # _log.debug("Value range: {}".format(valueRange))

        if valueRange == 0:
            _log.debug("Value range is 0")
            log10Exponent = 0
        else:
            log10Exponent = math.floor(math.log10(valueRange)) - 1

        # Fulfill the minimum gridline constraint
        while valueRange / 10 ** log10Exponent > maxNumberOfGridLines:
            log10Exponent += 1

        # fulfill the max gridlines constraint
        tickDistance = 10 ** log10Exponent
        while valueRange / tickDistance < minNumberOfGridLines:
            tickDistance *= 0.5

        # _log.debug("Tick info: log10 {}".format(log10Exponent))
        first_pos_idx = int(upperValue / tickDistance)
        last_pos_idx = int(lowerValue / tickDistance)

        if first_pos_idx < last_pos_idx:
            d = 1
            last_pos_idx += 1
        else:
            d = -1
            last_pos_idx -= 1

        required_tick_width = 0
        metrics = QFontMetrics(self.font)
        ticks = []

        for k in range(first_pos_idx, last_pos_idx, d):
            pos = round(k * tickDistance * scaling + shift)
            value = k * tickDistance
            tickString = self.tickFormat.format(value)

            ticks.append((pos, tickString))

            cur_tick_width = metrics.width(tickString)
            if cur_tick_width > required_tick_width:
                required_tick_width = cur_tick_width

        return ticks, required_tick_width

    def __repr__(self):
        return "<ChartAxis>"

    def __del__(self):
        _log.debug("Finalizing: {}".format(self))


class VerticalAxis(ChartAxis):
    """ Vertical chart axis. """

    def boundingRect(self):
        parent = self.parentWidget().size()
        s = self.size()
        b_rect = QRectF(0, 0, parent.width(), s.height())
        return b_rect

    def _generatePicture(self, p=QPainter()):
        p.setBrush(Qt.transparent)
        p.setPen(makePen(self.gridColor))
        p.setFont(self.font)

        if self._areaTransform is None:
            return

        parent_w = self.parentWidget().size().width()
        parent_h = self.parentWidget().size().height()

        translation = self._areaTransform.m32()
        scaling = self._areaTransform.m12() + self._areaTransform.m22()  # only for rotations along 90 degrees

        if scaling == 0:
            _log.debug("????")
            return

        ticks, run_width = self.calcTicks(translation, scaling, parent_h)

        self.parentWidget().layout().setColumnFixedWidth(1, run_width + 10)

        p.drawLine(self.size().width(), 0, self.size().width(), self.size().height())
        for pos, tickString in ticks:
            if 10 < pos < self.size().height():
                p.drawLine(run_width + 6, round(pos), parent_w, round(pos))

                tickRect = QRectF(0, pos - 4, run_width + 2, 10)
                p.drawText(tickRect, self.flags, tickString)


class HorizontalAxis(ChartAxis):
    """ Horizontal chart axis. """

    def __init__(self, parent=None):
        """

        :param parent:
        :return:
        """
        super(HorizontalAxis, self).__init__(parent)
        self.flags = Qt.TextDontClip | Qt.AlignCenter | Qt.AlignVCenter

    def boundingRect(self):
        parent = self.parentWidget().area.size()
        v_axis = self.parentWidget().main_vertical_axis.size()
        s = self.size()
        b_rect = QRectF(-v_axis.width(), -parent.height(), s.width()+v_axis.width(), parent.height() + s.height())
        return b_rect

    def _generatePicture(self, p=QPainter()):
        p.setBrush(Qt.transparent)

        pen = QPen(QBrush(self.gridColor), 1.0)
        pen.setCosmetic(True)

        p.setPen(pen)
        p.setFont(self.font)

        if self._areaTransform is None:
            return

        parent_h = self.parentWidget().area.size().height()

        shift = self._areaTransform.m31()
        scaling = self._areaTransform.m11() + self._areaTransform.m21()
        displayRange = self.size().width()

        ticks, run_width = self.calcTicks(shift, scaling, displayRange, maxGridSpace=100, minGridSpace=80)
        rw = run_width / 2.

        p.drawLine(0, 0, self.size().width(), 0)
        for pos, tickString in ticks:
            if 0 < pos < self.size().width() - 30:
                p.drawLine(round(pos), 5,  round(pos), -parent_h)

                tickRect = QRectF(pos - rw, 8, run_width, 10)
                p.drawText(tickRect, self.flags, tickString)


class SecondaryHorizontalAxis(HorizontalAxis):
    """ Horizontal axis with a different tick scale.

    This is useful if e.g. your data is sampled on its own timescale but could also be represented in UTC time.
    And you want to see both abscissa values.
    """

    def __init__(self, main_axis_values, secondary_axis_values, parent=None):
        """ Due to free zooming and ranging on the

        :param main_axis_values: values on the main axis.
        :param secondary_axis_values: corresponding value on the main axis.
        :param parent: parent item
        """
        super(SecondaryHorizontalAxis, self).__init__(parent)
        # self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.main_axis_values = main_axis_values
        self.secondary_axis_values = secondary_axis_values

        self._dbg_box_color = Qt.magenta

    def boundingRect(self):
        area = self.parentWidget().area.size()
        v_axis = self.parentWidget().mainVerticalAxis.size()
        s = self.size()
        b_rect = QRectF(-v_axis.width(), 0, s.width()+v_axis.width(), area.height() + s.height())
        return b_rect

    def _generatePicture(self, p=QPainter()):
        p.setBrush(Qt.transparent)
        pen = QPen(QBrush(self.gridColor), 1.0)
        pen.setCosmetic(True)
        p.setPen(pen)
        p.setFont(self.font)

        p.drawLine(0, self.size().height(), self.size().width(), self.size().height())

        pen = QPen(QBrush(QColor(188, 136, 184, 255)), 1.0, style = Qt.DotLine)
        pen.setCosmetic(True)
        p.setPen(pen)


        if self._areaTransform is None:
            return

        parent_h = self.parentWidget().area.size().height()

        shift = self._areaTransform.m31()
        scaling = self._areaTransform.m11() + self._areaTransform.m21()
        displayRange = self.size().width()

        ticks, run_width = self.calcTicks(shift, scaling, displayRange, maxGridSpace=100, minGridSpace=80)
        rw = run_width / 2.


        for pos, tickString in ticks:
            if 0 < pos < self.size().width() - 30:
                p.drawLine(round(pos), self.size().height() - 5,  round(pos), parent_h + self.size().height())

                tickRect = QRectF(pos - rw, self.size().height() - 18, run_width, 10)
                p.drawText(tickRect, self.flags, tickString)

    def calcTicks(self, shift, scaling, displayRange, maxGridSpace=80, minGridSpace=40):
        """ Calculates the axis ticks.
         The ticks are calculated along the logarithm of the base 10 of the displayed value range.
         The resulting exponent for the ticks is than scaled with respect to the preferred number of
         ticks and the value range.
         In case the value range would cause more ticks as previously determined the exponent is incremented
         by 1. Otherwise if the exponent results in to less ticks, the exponent is divided by 2.

        :param shift: offset from point of origin along the current axis (m31 / m32 from transform)
        :param scaling: scaling of scene (m11 / m12 / m21 / m22 from transform)
        :param displayRange: range of visible pixels
        :param maxGridSpace: maximum space between gridlines
        :param minGridSpace: minimum space between gridlines
        :return: list of ticks (tuple of position and label) and the required tick with
        """
        # first lets see how many ticks can be placed on the axis
        minNumberOfGridLines = displayRange / float(maxGridSpace)
        maxNumberOfGridLines = displayRange / float(minGridSpace)

        # Calculate the up most and lowest value on axis
        lowerValue = -shift / scaling
        upperValue = (displayRange - shift) / scaling

        valueRange = abs(upperValue - lowerValue)
        # _log.debug("Value range: {}".format(valueRange))

        if valueRange == 0:
            _log.debug("Value range is 0")
            log10Exponent = 0
        else:
            log10Exponent = math.floor(math.log10(valueRange)) - 1

        # Fulfill the minimum gridline constraint
        while valueRange / 10 ** log10Exponent > maxNumberOfGridLines:
            log10Exponent += 1

        # fulfill the max gridlines constraint
        tickDistance = 10 ** log10Exponent
        while valueRange / tickDistance < minNumberOfGridLines:
            tickDistance *= 0.5

        required_tick_width = 0
        metrics = QFontMetrics(self.font)
        ticks = []

        for k, main_tick in enumerate(self.main_axis_values):
            if main_tick < lowerValue or main_tick > upperValue:
                continue

            pos = round(main_tick * scaling + shift)
            if ticks and ticks[-1][0]:
                last_pos = ticks[-1][0]
                d = pos -last_pos
                if d < minGridSpace:
                    continue

            value = self.secondary_axis_values[k]
            tickString = self.tickFormat.format(value)

            ticks.append((pos, tickString))

            cur_tick_width = metrics.width(tickString)
            if cur_tick_width > required_tick_width:
                required_tick_width = cur_tick_width

        return ticks, required_tick_width


class ScaleBox(QGraphicsItem):

    def __init__(self, parent=None):
        """ Overlay tha is visible when a zooming operation is in progress to give the user feedback
        about the region that is zoomed in to.

        :param parent: Optional parent widget
        """
        super(ScaleBox, self).__init__(parent)

        self._topLeft = None
        self._bottomRight = None

    def boundingRect(self):
        return QRectF(self._topLeft, self._bottomRight)

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        pen = QPen(Qt.yellow, 2.0, Qt.DotLine)
        pen.setCosmetic(True)
        brush = QBrush(QColor(255, 255, 0, 127), Qt.SolidPattern)
        p.setBrush(brush)
        p.setPen(pen)
        r = self.boundingRect().adjusted(1, 1, -2, -2)
        # _log.debug("SB: {},{} {},{}".format(r.x(), r.y(), r.width(), r.height()))
        p.drawRect(r)


class ChartArea(QGraphicsWidget):

    # Used to update axis,
    hAxisChange = pyqtSignal(object)
    vAxisChange = pyqtSignal(object)

    # Notifies interested parties
    visibleRangeChange = pyqtSignal(object)

    def __init__(self, parent=None):
        """ Hosts all items that are placed on the chart basically the visible area of
        the chart.
        Handles pan and zoom and updates the axis accordingly.

        .. note:: Instantiated along with the ChartView

        :param parent: ChartWidget
        """
        super(ChartArea, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setFlags(QGraphicsItem.ItemClipsChildrenToShape | QGraphicsItem.ItemIsFocusable)

        self.__rootItem = ChartItem(self)  # invisible root item

        self.__initZoomPrepare = False
        self.__initZoom = False
        self.__mouseMode = None

        self.__visibleRange = None
        self.__scaleBox = None

        self.__maxVisibleRange = None

        self.__aspectRatio = None

        self._dbg_box_color = Qt.red

    @property
    def aspectRatio(self):
        return self.__aspectRatio

    def setAspectRatio(self, value):
        self.__aspectRatio = value
        if value is not None:
            self.adjustRange()

    def setMaxVisibleRange(self, rect):
        self.__maxVisibleRange = rect.normalized()

    def getRootItem(self):
        return self.__rootItem

    def boundingRect(self):
        # Override
        b_rect = QRectF(0, 0, self.size().width()-1, self.size().height()-1)
        return b_rect

    def paint(self, p=QPainter(), o=QStyleOptionGraphicsItem(), widget=None):
        # Override
        if CONFIG.debug:  # _log.getEffectiveLevel() < logging.INFO:
            p.setPen(QPen(self._dbg_box_color))
            p.drawRect(self.boundingRect())

    def resizeEvent(self, event):
        _log.debug("Received resize")
        if self.__visibleRange is None:
            self._calcVisibleRange()
        self.axisChange()
        # self.adjustRange()

    def showEvent(self, event):
        _log.debug("Show event")
        self.adjustRange()

    PAN_MODE, ZOOM_BOX_MODE = range(2)

    def mousePressEvent(self, event):
        _log.debug("Mouse press event")

        # self.__mouseMode = ChartArea.PAN_MODE
        if Qt.ControlModifier == event.modifiers():
            _log.debug("CTRL key pressed")
            self.__mouseMode = ChartArea.ZOOM_BOX_MODE
            # Part 1 of 2: initialize Scale Box, but that event could be an dbl click
            self.__initZoomPrepare = True
        # elif Qt.ShiftModifier == event.modifiers():
        #     self.__mouseMode = ChartArea.PAN_MODE
        #
        # else:
        #     # _log.debug("Calling defaults")
        #     super(ChartArea, self).mousePressEvent(event)
        else:
            self.__mouseMode = ChartArea.PAN_MODE
        # super(ChartArea, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mouseMode == ChartArea.ZOOM_BOX_MODE and self.__initZoom:

            r = self.__scaleBox.boundingRect().normalized()
            _log.debug("SB: {},{} {},{}".format(r.x(), r.y(), r.width(), r.height()))
            _log.debug(r)

            invTransform, invertible = self.__rootItem.transform().inverted()

            if not invertible:
                self.__initZoomPrepare = False
                self.__initZoom = False
                self.__mouseMode = None
                return

            self.__visibleRange = invTransform.mapRect(r)
            self.adjustRange()
            self.scene().removeItem(self.__scaleBox)

            _log.debug("Emitting Bounds Changed from: mouseReleaseEvent(...)")
            self.visibleRangeChange.emit(self.__visibleRange)

        self.__initZoomPrepare = False
        self.__initZoom = False
        self.__mouseMode = None

    def mouseMoveEvent(self, event):
        if self.__mouseMode == ChartArea.ZOOM_BOX_MODE and self.__initZoom:
            # _log.debug("Zoom box ")
            self.__scaleBox._bottomRight = event.pos()
            self.scene().update()
        elif self.__mouseMode == ChartArea.ZOOM_BOX_MODE and self.__initZoomPrepare:
            # Part 1 of 2: initialize Scale Box
            # _log.debug("Init zoombox")
            self.__initZoom = True

            self.__scaleBox = ScaleBox(self)
            self.__scaleBox._topLeft = event.pos()
            self.__scaleBox._bottomRight = event.pos()
            self.__initZoomPrepare = False

            # set focus to receive key events during scale box drag in order to cancel by pressing excape
            self.setFocus()

        if self.__mouseMode == ChartArea.PAN_MODE:
            self.__pan(event)
            self.visibleRangeChange.emit(self.__visibleRange)

    def __pan(self, event):
        pos = event.pos()
        lastPos = event.lastPos()
        dif = pos - lastPos

        t = self.__rootItem.transform()
        n = QTransform(
            t.m11(), t.m12(),
            t.m21(), t.m22(),
            t.m31() + dif.x(), t.m32() + dif.y()
        )

        # Limit to boundries
        if self.__maxVisibleRange is not None:
            r = self.boundingRect()
            invTransform, invertible = n.inverted()

            if not invertible:
                _log.error("Transform cannot be inverted.")
                return

            visibleRange = invTransform.mapRect(r)

            if (visibleRange.top() < self.__maxVisibleRange.top() or
                    visibleRange.bottom() > self.__maxVisibleRange.bottom() or
                    visibleRange.left() < self.__maxVisibleRange.left() or
                    visibleRange.right() > self.__maxVisibleRange.right()):
                return

        # self._logTransform(n, desc="Pan")
        self.__rootItem.setTransform(n)

        self._calcVisibleRange()
        self.axisChange()

    def _calcVisibleRange(self):
        r = self.boundingRect()
        invTransform, invertible = self.__rootItem.transform().inverted()

        if not invertible:
            _log.error("Transform cannot be inverted.")
            return

        self.__visibleRange = invTransform.mapRect(r)

    def keyPressEvent(self, event):
        _log.debug("Key event")
        if event.key() == Qt.Key_Escape and self.__initZoom:
            _log.debug("Canceling scalebox zoom")
            self.scene().removeItem(self.__scaleBox)
            self.__initZoom = False
            self.update()

    def wheelEvent(self, event):
        _log.debug("Wheel on area")

        t = self.__rootItem.transform()

        inv_t, invertible = t.inverted()
        if not invertible:
            _log.error("Transformation not invertible!")
            return

        if self.__visibleRange is None:
            # _log.debug("No visible range")
            self._calcVisibleRange()
            # return

        # Calculate coords under mouse
        coords = inv_t.map(event.pos())
        _log.debug("Coords: {}, {}".format(coords.x(), coords.y()))

        bbox = self.__visibleRange
        _log.debug("Visible Range: {}".format(bbox))

        # Percentages in visible range, hopefully this is rotation invariant
        pct_left = (coords.x() - bbox.left()) / bbox.width()
        pct_top = (coords.y() - bbox.top()) / bbox.height()

        _log.debug("Percentage from x/y: {:2.2f}/{:2.2f}".format(pct_left * 100.0, pct_top * 100.0))

        if not 0 <= pct_left <= 1.0 or not 0 <= pct_top <= 1.0:
            _log.error("Percentages OUT of bounds...")

        if event.delta() < 0:
            zoom_factor = 1.2
        else:
            zoom_factor = 1 / 1.2

        new_width = bbox.width() * zoom_factor
        # deltaWidth = new_width - bbox.width()
        new_height = bbox.height() * zoom_factor
        # deltaHeight = new_height - bbox.height()

        _log.debug("New sizes: {}, {}".format(new_width, new_height))
        # _log.debug("Size change: {}, {}".format(deltaWidth, deltaHeight))

        newLeft = coords.x() - new_width * pct_left
        newTop = coords.y() - new_height * pct_top

        newBbox = QRectF(QPointF(newLeft, newTop), QSizeF(new_width, new_height)).normalized()
        _log.debug("New Visible Range: {}".format(newBbox))

        self.__visibleRange = newBbox
        self.adjustRange()

        self.visibleRangeChange.emit(self.__visibleRange)

    @classmethod
    def _logTransform(cls, t, desc=None):
        """ Dumps the QTransform values, used for development.

        :param t:
        :param desc:
        :return:
        """
        if desc is None:
            _log.debug("[")
        else:
            _log.debug("{} = [".format(desc))
        _log.debug("{:2.2f},\t{:2.2f},\t{:2.2f};".format(t.m11(), t.m12(), t.m13()))
        _log.debug("{:2.2f},\t{:2.2f},\t{:2.2f};".format(t.m21(), t.m22(), t.m23()))
        _log.debug("{:2.2f},\t{:2.2f},\t{:2.2f}".format(t.m31(), t.m32(), t.m33()))
        _log.debug("]")

    def mouseDoubleClickEvent(self, event):
        self.autoRange()
        # self.visibleRangeChange.emit(self.__visibleRange)

    def axisChange(self):
        t = self.__rootItem.transform()
        self.vAxisChange.emit(t)
        self.hAxisChange.emit(t)

    def autoRange(self):
        children = self.__rootItem.childItems()

        if len(children) == 0:
            return

        bbox = None
        for c in children:
            if int(c.flags()) & int(QGraphicsItem.ItemIgnoresTransformations):
                rect = QRectF(-.5e-8, -.5e-8, 1e-8, 1e-8)
            else:
                rect = c.boundingRect()

            if c.chartItemFlags & ChartItemFlags.FLAG_NO_AUTO_RANGE:
                continue

            if bbox is None:
                bbox = rect.normalized()
                bbox.moveCenter(bbox.center() + c.pos())
            else:
                other = rect.normalized()
                other.moveCenter(other.center() + c.pos())
                bbox = bbox.united(other)

        _log.debug("bbox: {}".format(bbox))
        if bbox is None:
            return

        if bbox.height() == 0:
            bbox.adjust(0, -.5, 0, .5)

        h_pad = bbox.height() * 0.005  # add 0.5 % to the visible range.
        w_pad = bbox.width() * 0.005
        bbox.adjust(-w_pad, -h_pad, w_pad, h_pad)

        self.__visibleRange = bbox
        self.adjustRange()
        self.visibleRangeChange.emit(self.__visibleRange)

    def adjustRange(self):
        if self.__visibleRange is None:
            return

        if self.__maxVisibleRange:
            # TODO: Feels shitty when paning against the bounds
            _log.debug("Max visible: {}".format(self.__maxVisibleRange))

            if self.__visibleRange.top() < self.__maxVisibleRange.top():
                self.__visibleRange.setTop(self.__maxVisibleRange.top())

            if self.__visibleRange.bottom() > self.__maxVisibleRange.bottom():
                self.__visibleRange.setBottom(self.__maxVisibleRange.bottom())

            if self.__visibleRange.left() < self.__maxVisibleRange.left():
                self.__visibleRange.setLeft(self.__maxVisibleRange.left())

            if self.__visibleRange.right() > self.__maxVisibleRange.right():
                self.__visibleRange.setRight(self.__maxVisibleRange.right())

        area = self.size()
        bbox = self.__visibleRange
        _log.debug(bbox)

        def sign(v):
            """ Signum function, python does not have it

            :param v:
            :return:
            """
            if v == 0.0:
                return 0.0
            elif v > 0.0:
                return 1.0
            else:
                return -1.0

        t = self.__rootItem.transform()

        _log.debug("Area Aspect: {} / {} = 1:{}".format(area.width(), area.height(), area.height() / area.width()))
        _log.debug("View Aspect: {} / {} = 1:{}".format(bbox.width(), bbox.height(), bbox.width() / bbox.height()))

        # Enforce fixed aspect ratio
        if self.__aspectRatio is not None:
            if t.m12() != 0:
                # AUTOSAR width and height flipped
                bbox.setWidth(self.__aspectRatio * area.height() / area.width() * bbox.height())
            else:
                bbox.setWidth(self.__aspectRatio * area.width() / area.height() * bbox.height())

        s11 = (area.width()) / bbox.width() * sign(t.m11())
        s12 = (area.height()) / bbox.width() * sign(t.m12())
        s21 = (area.width()) / bbox.height() * sign(t.m21())
        s22 = (area.height()) / bbox.height() * sign(t.m22())

        _log.info("{}, {}; {}, {}".format(s11, s12, s21, s22))

        # The following shift works for not transformed, flipped y, flipped y and rotated 90 degrees
        # and yes this still is ugly....
        if s11 > 0 or s21 > 0:
            dx = -bbox.left() * s11
        else:
            dx = -bbox.bottom() * s21

        if s22 > 0 or s12 > 0:
            dy = -bbox.top() * s22
        else:
            dy = -bbox.bottom() * s22 + -bbox.right() * s12

        # Update and apply the new transform to the chart items.
        n = QTransform()
        n.setMatrix(
            s11, s12, 0,
            s21, s22, 0,
            dx, dy, 1
        )

        self.__rootItem.setTransform(n)
        self.axisChange()

    def setRange(self, bbox):
        r = bbox.normalized()
        _log.debug("Set range")
        _log.debug("bbox: {}".format(r))
        self.__visibleRange = r
        self.adjustRange()

    def __repr__(self):
        return "<ChartArea>"

    def __del__(self):
        _log.debug("Finalizing: {}".format(self))

