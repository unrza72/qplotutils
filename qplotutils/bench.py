#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qplotutils.bench
----------------

Widgets to create IDE like workbenches with dock widgets that can be rearanged and resized freely.
"""
import json
import logging
import pickle
import uuid

import math
from qtpy.QtCore import (
    Qt,
    QPointF,
    QRectF,
    QRect,
    Signal,
    QPoint,
    QLine,
    QMargins,
    Property,
    QMimeData,
    QByteArray,
)
from qtpy.QtGui import (
    QPen,
    QBrush,
    QColor,
    QPainter,
    QPainterPath,
    QTransform,
    QPixmap,
    QDrag,
)
from qtpy.QtWidgets import (
    QWidget,
    QStyleOption,
    QHBoxLayout,
    QStyle,
    QVBoxLayout,
    QSplitter,
    QStackedLayout,
    QPushButton,
    QSizePolicy,
    QLabel,
    QMenu,
    QDialog,
    QAction,
    QApplication,
)

from . import LOG_LEVEL, MIME_TYPE, CONFIG
from .ui.dock_properties import Ui_DialogDockProperties

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


# TODO:  Equal sized adding
# TODO: Min Sizes configurable
# TODO: Detach / Reattach from Bench


class BenchItem(QWidget, object):
    """ Base class for all items that can be placed on the Bench.

    That are:
     * TabContainers,
     * SplitterContainers, and
     * Docks
    """

    def __init__(self):
        super(BenchItem, self).__init__()

        self._uid = str(uuid.uuid4())
        self._parent_container = None

    @property
    def uid(self):
        """ Unique Identifier of the item.

        :return: UUID4 string
        """
        return self._uid

    @property
    def parentContainer(self):
        """ Parent container of that item.

        :return: parent container
        """
        return self._parent_container

    @parentContainer.setter
    def parentContainer(self, value):
        """ Sets the parent container of that item.

        :param value: parent item
        """
        self._parent_container = value

    def paintEvent(self, event):
        """ Override from QWidget, needed to get stylesheets working

        :param event: paint event
        """
        # _log.debug("Tab: paint event.")
        opt = QStyleOption()
        opt.initFrom(self)

        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

        if CONFIG.debug_layout:
            painter.setPen(QPen(Qt.red, 1.0))
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
            painter.setPen(QPen(Qt.black, 1.0))
            painter.drawText(QPointF(5, 12), str(self))

    def __repr__(self):
        return "<{}.{}: uid='{}'>".format(
            self.__module__, self.__class__.__name__, self.uid
        )

    def __del__(self):
        if CONFIG.debug_layout:
            _log.debug("Finalize: {}".format(self))

    def saveLayout(self):
        layout = {
            "class": self.__class__.__name__,
            "module": self.__class__.__module__,
            "uid": self.uid,
        }

        return layout

    def loadLayout(self, layout):
        """ Restores the given layout of the item based on a layout directory.

        ..see: saveLayout()

        :param layout: dict with layout information.
        :return:
        """
        raise NotImplementedError()


class Placement(object):
    """ Enum of the available Placement options for docks. """
    options_list = ["Left", "Top", "Right", "Bottom", "Tab"]

    LEFT, TOP, RIGHT, BOTTOM, TAB = options_list #  ["Left", "Top", "Right", "Bottom", "Tab"]




class Bench(QWidget):
    """ Widget that provides the area on which docks can be added and moved around completely free

    :param parent: parent Widget
    """

    #: Signal that notifies connected slots about changes in layout or added/removed items.
    contentModified = Signal()

    def __init__(self, parent=None):

        super(Bench, self).__init__(parent)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(4)
        if CONFIG.debug_layout:
            self.layout.setContentsMargins(2, 16, 2, 2)
        self.setLayout(self.layout)

        self.root_container = SplitterContainer(self, None)
        self.root_container.contentModified.connect(self.__contentModified)
        self.layout.addWidget(self.root_container)

        # self._style = """
        #         Bench {
        #             background-color: #a0a0a1;
        #         }
        # """
        # self.setStyleSheet(self._style)

    @classmethod
    def __widgetIndex(cls, placement):
        if placement in [Placement.TOP, Placement.LEFT]:
            return 0

        return -1

    @classmethod
    def __widgetOrientation(cls, placement):
        if placement in [Placement.TOP, Placement.BOTTOM]:
            return Qt.Vertical

        return Qt.Horizontal

    def __contentModified(self):
        self.contentModified.emit()

    def addDock(self, dock, placement=Placement.BOTTOM, ref=None):
        """ Adds a dock to the bench.

        :param dock: The dock that is added
        :param placement: Absolute or relative placement on the bench
        :param ref: (Optional) if provided the placement is relative to that dock
        """
        _log.debug("Adding dock: {}".format(dock))
        dock.setVisible(True)

        if ref is None:
            if placement in [Placement.TAB, None]:
                raise BenchException("Cannot add tab without reference")

            if (
                self.root_container.orientation == self.__widgetOrientation(placement)
                or len(self.root_container.flatDockList) == 0
            ):
                # root container orientation is as needed to add the new dock to the
                # outer border of the bench.
                # Get the index from the requested placement and add the dock to
                # root container
                self.root_container.orientation = self.__widgetOrientation(placement)

                tab_container = TabContainer(self, self.root_container)
                tab_container.contentModified.connect(self.__contentModified)
                tab_container.closing.connect(self.root_container.closeChild)
                tab_container.addItem(-1, dock)

                self.root_container.addItem(
                    self.__widgetIndex(placement), tab_container
                )

            else:
                # Need to replace root container, orientation is different from
                # the requested placement

                # Yank the current root container
                temp_container = self.root_container

                # Add a new one
                self.root_container = SplitterContainer(
                    self, None, self.__widgetOrientation(placement)
                )
                self.root_container.contentModified.connect(self.__contentModified)
                self.layout.addWidget(self.root_container)

                # Add the previous root container to the new container, than add the dock
                self.root_container.addItem(0, temp_container)

                tab_container = TabContainer(self, self.root_container)
                tab_container.contentModified.connect(self.__contentModified)
                tab_container.closing.connect(self.root_container.closeChild)
                tab_container.addItem(-1, dock)
                self.root_container.addItem(
                    self.__widgetIndex(placement), tab_container
                )

        elif ref is not None and placement == Placement.TAB:
            # Adding tab to existing container, super simple
            tab_container = ref.parentContainer
            tab_container.addItem(-1, dock)

        else:
            # splitting the space currently used by the container of ref dock
            tab_container = ref.parentContainer
            parent_container = tab_container.parentContainer
            c_index = parent_container.indexOf(tab_container)

            # yank current tab
            tab_container.setParent(None)

            # Add new splitter, and add it in the location of the previous tab container
            container = SplitterContainer(
                self, parent_container, self.__widgetOrientation(placement)
            )
            container.contentModified.connect(self.__contentModified)
            parent_container.addItem(c_index, container)

            # add the current tab to new container and than place the new dock
            container.addItem(0, tab_container)

            new_container = TabContainer(self, container)
            new_container.contentModified.connect(self.__contentModified)
            new_container.closing.connect(container.closeChild)
            new_container.addItem(-1, dock)

            container.addItem(self.__widgetIndex(placement), new_container)

        self.contentModified.emit()

    def removeDock(self, dock):
        """ Removes the given dock from the bench.

        :param dock: Dock that should be removed.
        """
        _log.debug("Removing dock: {}".format(dock))
        dock.parentContainer.closeChild(dock.uid)
        self.contentModified.emit()

    def dockMove(self, dock_uid, placement, ref_uid):
        """ Moves the dock programatically.

        .. TODO:: Check if ref == None is possible.

        :param dock_uid: UID of the docks that should move
        :param placement: Placement relative to the reference dock or absolute if no reference given
        :param ref_uid: UID of the reference dock
        """
        _log.debug("Dock move: {}, {}, {}".format(dock_uid, placement, ref_uid))

        dock = None
        ref = None
        for d in self.root_container.flatDockList:
            if d.uid == dock_uid:
                dock = d
            elif d.uid == ref_uid:
                ref = d

        previous_container = dock.parentContainer
        self.addDock(dock, placement, ref)
        previous_container.closeChild(dock.uid)

    def getDock(self, uid):
        """ Returns the dock with the given UID if dock is part of this bench.

        :param uid: Dock UID
        :return: Dock instance if found else None
        """
        for d in self.root_container.flatDockList:
            if d.uid == uid:
                return d

        return None
        # raise BenchException("No such dock on bench")

    @property
    def docks(self):
        """ List a dock on the bench.

        :return: list with all docks
        """
        return self.root_container.flatDockList

    def saveLayout(self, filename=None):
        """ Saves the benches dock layout to filename

        :param filename: Full path to json
        :return: Layout as dict
        """
        layout = self.root_container.saveLayout()

        if filename is not None:
            with open(filename, "w") as fh:
                json.dump(layout, fh, indent=4)

        return layout

    def loadLayout(self, filename):
        """ Loads layout from file.

        :param filename: Full path to layout json file
        """
        self.clearAll()
        self.root_container.setParent(None)
        self.root_container.close()

        with open(filename, "r") as fh:
            layout = json.load(fh)

            module_str = layout["module"]
            class_str = layout["class"]

            # Bootstrap part II: Make the child containers
            mod = __import__(module_str, fromlist=[class_str])
            klass = getattr(mod, class_str)

            self.root_container = klass(self, None)
            self.root_container.contentModified.connect(self.__contentModified)
            self.layout.addWidget(self.root_container)

            self.root_container.loadLayout(layout)

    def clearAll(self):
        """ Removes all docks from the bench.
        """
        for dock in self.docks:
            self.removeDock(dock)


class Dock(BenchItem):
    closing = Signal(object)
    """ Signal that is emited when the dock is about to be closed. """

    activated = Signal(object)
    """ Signal that is emited when the dock is activated and thus becomes visible in the tabcontainer. """

    def __init__(self, title="Dock"):
        """ Widget that can freely placed and re-sized on the bench.

        :param title: docks title
        """
        super(Dock, self).__init__()

        self._tab = Tab(self, title)

        self._style = """
        Dock {
            border: 1px solid #475057;

        }
        """
        self.setStyleSheet(self._style)
        self.setLayout(QVBoxLayout())

    def addWidget(self, widget):
        """ Adds the given widget to the docks central layout.

        :param widget: a widget
        """
        self.layout().addWidget(widget)

    @property
    def title(self):
        return self._tab.title

    @title.setter
    def title(self, value):
        self._tab.title = value

    @property
    def tab(self):
        return self._tab

    def saveLayout(self):
        layout = super(Dock, self).saveLayout()
        layout["title"] = self.title

        return layout

    def loadLayout(self, layout):
        self.title = layout["title"]

    def closeEvent(self, event):
        _log.debug("Close event")
        self.closing.emit(self.uid)


class AbstractContainer(BenchItem):
    closing = Signal(object)
    contentModified = Signal()

    def __init__(self, bench, parent_container):
        """ Base class for all containers.

        :param bench: bench to which the container belongs
        :param parent_container: parent container
        """
        super(AbstractContainer, self).__init__()

        self._bench = bench
        self._parent_container = parent_container

    @property
    def flatContainerList(self):
        """ Returns a flatten list of all containers recursively.

        :return: list of all children
        """
        return []


    @property
    def containers(self):
        """ Returns a list of direct child containers.

        :return: list of containers
        """
        return []
        # raise NotImplementedError()

    def addItem(self, index, item):
        """

        :param index:
        :param item:
        :return:
        """
        raise NotImplementedError()

    @property
    def flatDockList(self):
        """ Return a list of all docks from this an all child containers recursively.

        :return: list of all docks
        """
        raise NotImplementedError()

    @property
    def docks(self):
        """ Returns a list of docks which are directly attached to that container

        :return: list of docks
        """
        raise NotImplementedError()


class SplitterContainer(AbstractContainer):
    def __init__(self, bench, parent_container, orientation=Qt.Horizontal):
        """ A container which layouts all child items on a splitter layout with the given orientation.

        :param bench: bench to which the container belongs
        :param parent_container: parent container
        :param orientation: the splitters orientation
        """
        super(SplitterContainer, self).__init__(bench, parent_container)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        if CONFIG.debug_layout:
            self.layout.setContentsMargins(2, 16, 2, 2)
        self.setLayout(self.layout)

        self._splitter = QSplitter()
        self._splitter.setOrientation(orientation)
        self._splitter.setHandleWidth(2)

        self.layout.addWidget(self._splitter)

        self._sizes = []

    @property
    def orientation(self):
        return self._splitter.orientation()

    @orientation.setter
    def orientation(self, value):
        self._splitter.setOrientation(value)

    def indexOf(self, container):
        return self._splitter.indexOf(container)

    @property
    def flatDockList(self):
        dock_list = []

        for k in range(self._splitter.count()):
            widget = self._splitter.widget(k)
            child_docks = widget.flatDockList
            dock_list.extend(child_docks)

        return dock_list

    @property
    def flatContainerList(self):
        container_list = []

        for k in range(self._splitter.count()):
            widget = self._splitter.widget(k)
            container_list.append(widget)
            child_containers = widget.flatContainerList
            container_list.extend(child_containers)

        return container_list

    @property
    def containers(self):
        container_list = []

        for k in range(self._splitter.count()):
            widget = self._splitter.widget(k)
            container_list.append(widget)

        return container_list

    def addItem(self, index, item):
        if not isinstance(item, (TabContainer, SplitterContainer)):
            raise BenchException("Misuse")

        item.closing.connect(self.closeChild)
        item.parentContainer = self
        self._splitter.insertWidget(index, item)

        number_of_items = float(len(self._splitter.sizes()))

        if self.orientation == Qt.Horizontal:
            widget_size = self.width()
        else:
            widget_size = self.height()

        item_size = int(math.floor(widget_size / number_of_items))
        new_sizes = [item_size for _ in self._splitter.sizes()]
        _log.debug(new_sizes)
        self._splitter.setSizes(new_sizes)

    def closeChild(self, uid):
        for k in range(self._splitter.count()):
            widget = self._splitter.widget(k)

            if widget.uid == uid:
                _log.debug("Removing container: {}".format(uid))

                widget.parentContainer = None
                widget.close()
                widget.setParent(None)
                break

        self.contentModified.emit()
        if self._splitter.count() == 0:
            _log.debug("Splitter {} is empty. propagate.".format(uid))
            self.closing.emit(self.uid)

    def saveLayout(self):
        layout = super(SplitterContainer, self).saveLayout()
        layout["orientation"] = self.orientation
        layout["item_sizes"] = self._splitter.sizes()

        children = []
        for container in self.containers:
            children.append(container.saveLayout())
        layout["children"] = children

        return layout

    def loadLayout(self, layout):
        for k, child in enumerate(layout["children"]):
            module_str = child["module"]
            class_str = child["class"]

            # Bootstrap part II: Make the child containers
            mod = __import__(module_str, fromlist=[class_str])
            klass = getattr(mod, class_str)

            child_obj = klass(self._bench, self)
            self.addItem(k, child_obj)

            child_obj.loadLayout(child)

        self.orientation = layout["orientation"]
        self._splitter.setSizes(layout["item_sizes"])


class TabContainer(AbstractContainer):
    dockMove = Signal(object, object, object)

    class Point(object):
        def __init__(self, x, y):
            self.__x = x
            self.__y = y

        def x(self):
            return self.__x

        def y(self):
            return self.__y

    def __init__(self, bench, parent_container):
        """ Container which layouts its child items on stacked layout and provides a tab bar.

        :param bench:
        :param parent_container:
        """
        super(TabContainer, self).__init__(bench, parent_container)

        self.setAcceptDrops(True)
        self.refDropRegions = None
        self.absDropRegions = None
        self.overlay = DropOverlay(self)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        if CONFIG.debug_layout:
            self.layout.setContentsMargins(2, 16, 2, 2)
        self.setLayout(self.layout)

        self._tabbar = TabHeader()
        self.layout.addWidget(self._tabbar)

        self._dockstack = QStackedLayout()
        self._dockstack.setContentsMargins(0, 0, 0, 0)
        self._dockstack.setSpacing(0)
        self.layout.addLayout(self._dockstack)

    def activateTab(self, uid):
        _log.debug("Activating tab for dock: {}".format(uid))

        for d in self.flatDockList:
            if d.uid == uid:
                self._dockstack.setCurrentWidget(d)
                d.tab.setActive(True)
            else:
                d.tab.setActive(False)

    def closeChild(self, uid):
        _log.debug("Closing dock: {}".format(uid))

        was_active = False
        for d in self.flatDockList:
            if d.uid == uid:
                _log.debug("Removing dock: {}".format(d))

                was_active = d.tab.active

                d.tab.setParent(None)
                d.tab._dock = None
                d.parentContainer = None
                d.close()
                d.deleteLater()
                d.setParent(None)

        self.contentModified.emit()
        if self._dockstack.count() == 0:
            # Container is empty, close and propagate
            self.closing.emit(self._uid)
        elif was_active:
            dock = self.flatDockList[0]
            self.activateTab(dock.uid)

    @property
    def flatDockList(self):
        return [
            self._dockstack.itemAt(k).widget() for k in range(self._dockstack.count())
        ]

    @property
    def docks(self):
        return self.flatDockList

    def addItem(self, index, item):

        # _config.debug check
        if not isinstance(item, Dock):
            raise BenchException("Misuse")

        item.parentContainer = self
        item.closing.connect(self.closeChild)
        item.activated.connect(self.activateTab)

        self._tabbar.addTab(index, item)
        self._dockstack.insertWidget(index, item)
        self.activateTab(item.uid)

        item.setVisible(True)
        item.tab.setVisible(True)

    @classmethod
    def __checkEventMimeTypeData(cls, event):
        """ Checks the drag events MIME type, and that at least two dockbench items on the area.

        :param event: drag event / drop event
        :return: true when the MIME type can be handled
        """
        if not event.mimeData().hasFormat(MIME_TYPE):
            event.ignore()
            return False

        event.accept()
        return True

    def dragEnterEvent(self, event):
        _log.debug("TabContainer: Drag enter event")
        if not self.__checkEventMimeTypeData(event):
            return

        data = event.mimeData().data(MIME_TYPE).data()
        dock_uid = pickle.loads(data)
        _log.debug("ETID: {}".format(dock_uid))

        for d in self.flatDockList:
            if d.uid == dock_uid and len(self.flatDockList) == 1:
                _log.debug("Tab in container")
                event.ignore()
                return

        if self.rect().width() < 180 or self.rect().height() < 180:
            _log.debug("To less widget left...")
            event.ignore()
            return

        if self.overlay.isHidden():
            _log.debug("Drop overlay")
            self.overlay.raise_()
            self.overlay.show()
            w = self._dockstack.currentWidget()
            pos = w.mapTo(self, QPoint(0, 0))
            rect = QRect(pos.x(), pos.y(), w.width(), w.height())
            self.overlay.setGeometry(rect)

            xc = pos.x() + w.width() / 2.0
            yc = pos.y() + w.height() / 2.0

            self.refDropRegions = {
                TabContainer.Point(xc - 34, yc): Placement.LEFT,
                TabContainer.Point(xc + 34, yc): Placement.RIGHT,
                TabContainer.Point(xc, yc - 34): Placement.TOP,
                TabContainer.Point(xc, yc + 34): Placement.BOTTOM,
                TabContainer.Point(xc, yc): Placement.TAB,
            }
            self.absDropRegions = {
                TabContainer.Point(xc - 68, yc): Placement.LEFT,
                TabContainer.Point(xc + 68, yc): Placement.RIGHT,
                TabContainer.Point(xc, yc - 68): Placement.TOP,
                TabContainer.Point(xc, yc + 68): Placement.BOTTOM,
            }

    def dragMoveEvent(self, event):
        if not self.__checkEventMimeTypeData(event):
            return

        pos = event.pos()
        x = pos.x()
        y = pos.y()

        for region in self.refDropRegions:
            if abs(region.x() - x) <= 12 and abs(region.y() - y) <= 12:
                _log.debug("Drop ref over: {}".format(self.refDropRegions[region]))
                event.accept()
                self.overlay.setActiveDropRegion(self.refDropRegions[region])
                return

        for region in self.absDropRegions:
            if abs(region.x() - x) <= 12 and abs(region.y() - y) <= 12:
                _log.debug("Drop abs over: {}".format(self.absDropRegions[region]))
                event.accept()
                self.overlay.setActiveDropRegion(self.absDropRegions[region], True)
                return

        self.overlay.setActiveDropRegion(None)
        event.ignore()

    def dragLeaveEvent(self, event):
        _log.debug("TabContainer: Drag leave event")

        if not self.overlay.isHidden():
            self.overlay.hide()

            self.refDropRegions = None
            self.absDropRegions = None

    def dropEvent(self, event):
        _log.debug("TabContainer: Drop event")

        if not self.__checkEventMimeTypeData(event):
            event.ignore()
            return

        data = event.mimeData().data(MIME_TYPE).data()
        dock_uid = pickle.loads(data)
        _log.debug("ETID: {}".format(dock_uid))

        pos = event.pos()
        x = pos.x()
        y = pos.y()

        for region in self.refDropRegions:
            if abs(region.x() - x) <= 12 and abs(region.y() - y) <= 12:
                _log.debug("Drop ref over: {}".format(self.refDropRegions[region]))

                ref = self._dockstack.currentWidget()
                # self.dockMove.emit(dock_uid, self.refDropRegions[region], ref.uid)
                self._bench.dockMove(dock_uid, self.refDropRegions[region], ref.uid)
                break

        if self.absDropRegions is not None:
            for region in self.absDropRegions:
                if abs(region.x() - x) <= 12 and abs(region.y() - y) <= 12:
                    _log.debug("Drop abs over: {}".format(self.absDropRegions[region]))

                    # self.dockMove.emit(dock_uid, self.absDropRegions[region], None)
                    self._bench.dockMove(dock_uid, self.absDropRegions[region], None)
                    break

        if not self.overlay.isHidden():
            self.overlay.hide()

            self.refDropRegions = None
            self.absDropRegions = None

    def saveLayout(self):
        layout = super(TabContainer, self).saveLayout()

        children = []
        for dock in self.flatDockList:
            children.append(dock.saveLayout())
        layout["children"] = children

        return layout

    def loadLayout(self, layout):

        for k, child in enumerate(layout["children"]):
            module_str = child["module"]
            class_str = child["class"]

            # Bootstrap part II: Make the child containers
            mod = __import__(module_str, fromlist=[class_str])
            klass = getattr(mod, class_str)

            child_obj = klass()
            self.addItem(k, child_obj)

            child_obj.loadLayout(child)


class DropOverlay(QWidget):
    Blue = QColor(77, 137, 247)
    BlueAccent = QColor(43, 109, 231)
    BlueDim = QColor(77, 137, 247, 128)
    BlueAccentDim = QColor(43, 109, 231, 128)

    Yellow = QColor(255, 247, 175)
    YellowAccent = QColor(255, 242, 131)
    YellowDim = QColor(255, 247, 175, 128)
    YellowAccentDim = QColor(255, 242, 131, 128)

    def __init__(self, parent):
        super(DropOverlay, self).__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()
        self._activeAbsoluteRegion = None
        self._activeRelativeRegion = None

    def paintEvent(self, event):
        """ Adds a frame and the splitters internal id to the UI if debug is enabled.

        :param event: paint event
        """
        painter = QPainter(self)

        if CONFIG.debug_layout:
            painter.setPen(QPen(Qt.yellow, 4.0))
            painter.drawRect(self.rect().adjusted(1, 1, -2, -2))
            painter.setPen(QPen(Qt.black, 1.0))
            painter.drawText(QPointF(5, 12), str(self))

        # Relative drop cross and icons
        dock_center_x = self.width() / 2.0
        dock_center_y = self.height() / 2.0
        d_transform = QTransform()
        transform = d_transform.fromTranslate(dock_center_x, dock_center_y)
        painter.setTransform(transform)
        self._paintBackgroundCross(painter)

        transform = d_transform.fromTranslate(dock_center_x - 34, dock_center_y)
        painter.setTransform(transform)
        self._paintRefDropIcon(painter, Placement.LEFT)

        transform = d_transform.fromTranslate(dock_center_x - 68, dock_center_y)
        painter.setTransform(transform)
        self._paintAbsDropIcon(painter, Placement.LEFT)

        transform = d_transform.fromTranslate(dock_center_x, dock_center_y - 34)
        painter.setTransform(transform)
        self._paintRefDropIcon(painter, Placement.TOP)

        transform = d_transform.fromTranslate(dock_center_x, dock_center_y - 68)
        painter.setTransform(transform)
        self._paintAbsDropIcon(painter, Placement.TOP)

        transform = d_transform.fromTranslate(dock_center_x + 34, dock_center_y)
        painter.setTransform(transform)
        self._paintRefDropIcon(painter, Placement.RIGHT)

        transform = d_transform.fromTranslate(dock_center_x + 68, dock_center_y)
        painter.setTransform(transform)
        self._paintAbsDropIcon(painter, Placement.RIGHT)

        transform = d_transform.fromTranslate(dock_center_x, dock_center_y + 34)
        painter.setTransform(transform)
        self._paintRefDropIcon(painter, Placement.BOTTOM)

        transform = d_transform.fromTranslate(dock_center_x, dock_center_y + 68)
        painter.setTransform(transform)
        self._paintAbsDropIcon(painter, Placement.BOTTOM)

        transform = d_transform.fromTranslate(dock_center_x, dock_center_y)
        painter.setTransform(transform)
        self._paintRefDropIcon(painter, Placement.TAB)

    @classmethod
    def _configureBrushAndPen(cls, painter, brushColor, penColor, penWidth=1):
        painter.setBrush(QBrush(brushColor))
        painter.setPen(QPen(penColor, penWidth))

    def _paintAbsDropIcon(self, painter, placement):
        self._configureBrushAndPen(painter, Qt.white, Qt.white)
        r = QRectF(-14, -14, 28, 28)
        painter.drawRoundedRect(r, 2, 2)

        self._configureBrushAndPen(painter, self.Blue, self.BlueAccent)

        title = {
            Placement.LEFT: QRectF(-10, -10, 10, 4),
            Placement.RIGHT: QRectF(0, -10, 10, 4),
            Placement.TOP: QRectF(-10, -10, 20, 4),
            Placement.BOTTOM: QRectF(-10, -2, 20, 4),
            Placement.TAB: None,
        }
        if title[placement] is not None:
            painter.drawRect(title[placement])

        if placement == self._activeAbsoluteRegion:
            self._configureBrushAndPen(painter, self.Yellow, self.BlueAccent)
        else:
            self._configureBrushAndPen(painter, self.BlueDim, self.BlueAccentDim)

        bg = {
            Placement.LEFT: QRectF(-10, -5, 10, 14),
            Placement.RIGHT: QRectF(0, -5, 10, 14),
            Placement.TOP: QRectF(-10, -5, 20, 7),
            Placement.BOTTOM: QRectF(-10, 2, 20, 7),
            Placement.TAB: None,
        }
        if bg[placement] is not None:
            painter.drawRect(bg[placement])

        if placement == Placement.LEFT:
            painter.setBrush(QBrush(self.Blue))
            painter.setPen(QPen(self.BlueAccent, 1))

            path = QPainterPath()
            path.moveTo(6, 0)
            path.lineTo(10, -4)
            path.lineTo(10, 4)
            path.closeSubpath()
            painter.drawPath(path)

        elif placement == Placement.TOP:
            painter.setBrush(QBrush(self.Blue))
            painter.setPen(QPen(self.BlueAccent, 1))

            path = QPainterPath()
            path.moveTo(0, 6)
            path.lineTo(-4, 10)
            path.lineTo(4, 10)
            path.closeSubpath()
            painter.drawPath(path)

        elif placement == Placement.RIGHT:
            painter.setBrush(QBrush(self.Blue))
            painter.setPen(QPen(self.BlueAccent, 1))

            path = QPainterPath()
            path.moveTo(-6, 0)
            path.lineTo(-10, -4)
            path.lineTo(-10, 4)
            path.closeSubpath()
            painter.drawPath(path)

        elif placement == Placement.BOTTOM:
            painter.setBrush(QBrush(self.Blue))
            painter.setPen(QPen(self.BlueAccent, 1))

            path = QPainterPath()
            path.moveTo(0, -6)
            path.lineTo(-4, -10)
            path.lineTo(4, -10)
            path.closeSubpath()
            painter.drawPath(path)

    def setActiveDropRegion(self, placement, absolute=False):
        _log.debug("Set active drop region")
        self._activeAbsoluteRegion = None
        self._activeRelativeRegion = None

        if absolute:
            self._activeAbsoluteRegion = placement
        else:
            self._activeRelativeRegion = placement

        self.update()

    def _paintRefDropIcon(self, painter, placement):
        self._configureBrushAndPen(painter, Qt.white, Qt.white)
        r = QRectF(-14, -14, 28, 28)
        painter.drawRoundedRect(r, 2, 2)

        self._configureBrushAndPen(painter, self.Blue, self.BlueAccent)
        r = QRectF(-10, -10, 20, 4)
        painter.drawRect(r)

        if placement == self._activeRelativeRegion:
            self._configureBrushAndPen(painter, self.Blue, self.BlueAccent)
        else:
            self._configureBrushAndPen(painter, self.BlueDim, self.BlueAccentDim)

        r = QRectF(-10, -6, 20, 16)
        painter.drawRect(r)

        if placement == self._activeRelativeRegion:
            self._configureBrushAndPen(painter, self.Yellow, self.YellowAccent)
        else:
            self._configureBrushAndPen(painter, self.YellowDim, self.YellowAccentDim)

        accent_rect = {
            Placement.LEFT: QRectF(-9, -5, 9, 14),
            Placement.RIGHT: QRectF(0, -5, 9, 14),
            Placement.TOP: QRectF(-9, -5, 18, 7),
            Placement.BOTTOM: QRectF(-9, 2, 18, 7),
            Placement.TAB: QRectF(-9, -5, 18, 14),
        }

        r = accent_rect[placement]
        if r is not None:
            painter.drawRect(r)

        painter.setPen(QPen(self.BlueAccent, 1.0, style=Qt.DotLine))
        splitter_line = {
            Placement.LEFT: QLine(0, -5, 0, 9),
            Placement.RIGHT: QLine(0, -5, 0, 9),
            Placement.TOP: QLine(-9, 2, 9, 2),
            Placement.BOTTOM: QLine(-9, 2, 9, 2),
            Placement.TAB: None,
        }

        l = splitter_line[placement]
        if l is not None:
            painter.drawLine(l)

    @classmethod
    def _paintBackgroundCross(cls, painter):
        grey = QColor(220, 220, 220)
        greyAccent = QColor(180, 180, 180)

        painter.setBrush(QBrush(grey))
        painter.setPen(QPen(greyAccent, 1))

        path = QPainterPath()
        h0 = -86
        h1 = -18
        h2 = 18
        h3 = 86
        v0 = -86
        v1 = -18
        v2 = 18
        v3 = 86
        c = 7

        path.moveTo(v0, h1)
        path.lineTo(v1 - c, h1)
        path.lineTo(v1, h1 - c)
        path.lineTo(v1, h0)
        path.lineTo(v2, h0)
        path.lineTo(v2, h1 - c)
        path.lineTo(v2 + c, h1)
        path.lineTo(v3, h1)
        path.lineTo(v3, h2)
        path.lineTo(v2 + c, h2)
        path.lineTo(v2, h2 + c)
        path.lineTo(v2, h3)
        path.lineTo(v1, h3)
        path.lineTo(v1, h2 + c)
        path.lineTo(v1 - c, h2)
        path.lineTo(v0, h2)
        path.closeSubpath()
        painter.drawPath(path)

    # def __del__(self):
    #     _log.debug("Finalize: {}".format(self))


class TabHeader(QWidget):
    def __init__(self):
        super(TabHeader, self).__init__()  # QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.setLayout(self.layout)

    # def __del__(self):
    #     _log.debug("Finalize: {}".format(self))

    def addTab(self, index, item):
        self.layout.insertWidget(index, item.tab)

    @property
    def tabs(self):
        return [self.layout.itemAt(k).widget() for k in range(self.layout.count())]

    def getTab(self, dock):
        for k in range(self.layout.count()):
            w = self.layout.itemAt(k).widget()
            if w.uid == dock.uid:
                return w

        return None


class Tab(QWidget):

    # closing = pyqtSignal(object)
    # activated = pyqtSignal(object)

    def __init__(self, dock, title):
        super(Tab, self).__init__()  # QWidget.__init__(self)

        self._clickPos = None
        self._dock = dock
        self._active = False

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customContextMenu)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.setLayout(self.layout)

        self.titleLabel = QLabel()
        self.titleLabel.setText(title)

        self.titleLabel.setMinimumWidth(10)
        self.titleLabel.setContentsMargins(QMargins(5, 3, 5, 3))
        size_policy_1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        size_policy_1.setHorizontalStretch(0)
        size_policy_1.setVerticalStretch(0)
        size_policy_1.setHeightForWidth(
            self.titleLabel.sizePolicy().hasHeightForWidth()
        )
        self.titleLabel.setSizePolicy(size_policy_1)
        self.layout.addWidget(self.titleLabel)

        self.close_button = QPushButton()
        size_policy_2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        size_policy_2.setHorizontalStretch(0)
        size_policy_2.setVerticalStretch(0)
        size_policy_2.setHeightForWidth(
            self.close_button.sizePolicy().hasHeightForWidth()
        )
        self.close_button.setSizePolicy(size_policy_2)
        self.layout.addWidget(self.close_button)

        self.close_button.clicked.connect(self._closeClick)

        self._style = """
        Tab {
            background-color: #a0a0a1;
            border: 0px solid green;
            border-top-left-radius: 2px;
            border-top-right-radius: 2px;
            padding: 2px;
        }
        Tab[active="true"] {
            background-color: #475057;
            border: 0px solid green;
            border-top-left-radius: 2px;
            border-top-right-radius: 2px;
            padding: 2px;
        }
        Tab QLabel {color: #cecece; }
        Tab  > QPushButton {
            background-color: transparent;
            border: 0px solid green;
            qproperty-icon: none;
            image: url(":/bench/new_close1");
            width: 12px;
            height: 12px;
            padding: 4px; 
        }
        Tab  > QPushButton:hover {
            background-color: transparent;
            border: 0px solid green;
            qproperty-icon: none;
            image: url(":/bench/new_close1");
            width: 12px;
            height: 12px;
            padding: 4px; 
        }
        """
        self.setStyleSheet(self._style)

        self.closeAction = QAction("Close", self)
        self.closeAction.triggered.connect(self._closeClick)
        self.dockProperties = QAction("Properties", self)
        self.dockProperties.triggered.connect(self._dockProperties)

    def _customContextMenu(self, pos):

        menu = QMenu(self)
        menu.addAction(self.closeAction)
        menu.addSeparator()
        menu.addAction(self.dockProperties)
        menu.popup(self.mapToGlobal(pos))

    def _dockProperties(self):
        _log.debug("Dock Properties")

        class PropertiesDialog(QDialog):
            def __init__(self, parent=None):
                super(PropertiesDialog, self).__init__(parent)
                self.ui = Ui_DialogDockProperties()
                self.ui.setupUi(self)

        properties = PropertiesDialog(self)
        properties.ui.lineEditDockName.setText(self.title)

        if properties.exec_() == QDialog.Accepted:
            new_title = str(properties.ui.lineEditDockName.text())
            if new_title:
                self.title = new_title

    @property
    def title(self):
        return str(self.titleLabel.text())

    @title.setter
    def title(self, value):
        self.titleLabel.setText(value)

    @Property(bool)
    def active(self):
        """ Returns the tabs state. If active the parent tabcontainer displays the contents of
        that tabs dockbench.

        :return: True if active
        """
        return self._active

    def setActive(self, value):
        """ Sets the activation state.

        :param value:
        """
        self._active = value
        self.style().polish(self)

    @property
    def uid(self):
        return self._dock.uid

    def mouseReleaseEvent(self, event):
        _log.debug("Mouse release event on tab")
        self._dock.activated.emit(self.uid)

    def _closeClick(self):
        _log.debug("Close button clicked")
        self._dock.closing.emit(self.uid)

    def paintEvent(self, event):
        """ Needed to get Stylesheets working  :-(

        :param event: paint event
        """
        # _log.debug("Tab: paint event.")
        opt = QStyleOption()
        opt.initFrom(self)

        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    # Drag and drop support for docks
    def mousePressEvent(self, event):
        _log.debug("Mouse press event.")
        if event.button() == Qt.LeftButton:
            _log.debug("Mouse left click")
            self._clickPos = event.pos()

    def mouseMoveEvent(self, event):
        if (
            self._clickPos is None
            or (event.pos() - self._clickPos).manhattanLength()
            < QApplication.startDragDistance()
        ):
            return

        # _log.debug("Drag move")
        # render before detachment otherwise it might look ugly
        pixmap = QPixmap(self.size())
        self.render(pixmap)

        self.setVisible(False)
        if len(self._dock.parentContainer.flatDockList) == 1:
            self._dock.parentContainer.setVisible(False)

        # Build drag object
        event.accept()
        drag = QDrag(self)
        mimeData = QMimeData()
        encodedData = QByteArray(pickle.dumps(self._dock.uid))
        mimeData.setData(MIME_TYPE, encodedData)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        action = drag.exec_(Qt.MoveAction)

        _log.debug("After drag. Action: {}".format(action))
        if Qt.IgnoreAction == action:
            _log.debug("D'n'D canceled")
            self.setVisible(True)
            self._dock.parentContainer.setVisible(True)


class BenchException(Exception):
    """ Wrapper for all exceptions. """

    pass
