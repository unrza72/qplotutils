import logging

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget

from qplotutils.ui.cam_control import Ui_CamControl

_log = logging.getLogger(__name__)


class CamControl(QWidget):

    def __init__(self, cam_properties, parent=None):
        super(CamControl, self).__init__(parent)

        self.setWindowFlags(0 | Qt.Tool | Qt.WindowStaysOnTopHint | Qt.WindowTitleHint)

        self.cam_properties = cam_properties
        self.cam_properties.changed.connect(self.cam_changed)

        self.setWindowFlags(self.windowFlags() | Qt.Tool)

        self._ui = Ui_CamControl()
        self._ui.setupUi(self)

        self._ui.dial_distance.valueChanged.connect(self.dial_distance_changed)
        self._ui.lineEdit_distance.editingFinished.connect(self.edit_distance_changed)
        self._ui.dial_azimuth.valueChanged.connect(self.dial_azimuth_changed)
        self._ui.dial_elevation.valueChanged.connect(self.dial_elevation_changed)

        self._ui.dial_distance.setMinimum(1)
        self._ui.dial_distance.setMaximum(20 * 1000)
        self._ui.dial_distance.setSingleStep(1000)
        self._ui.dial_distance.setPageStep(1000)
        self._ui.dial_distance.setWrapping(False)

        self.cam_changed()

    def cam_changed(self):
        self._ui.dial_distance.setValue(self.cam_properties.distance * 1000)
        self._ui.lineEdit_distance.setText("{0:2.2f}".format(self.cam_properties.distance))
        self._ui.dial_azimuth.setValue(self.cam_properties.azimuth_angle)
        self._ui.lineEdit_azimuth.setText("{0:2.2f}".format(self.cam_properties.azimuth_angle))
        self._ui.dial_elevation.setValue(self.cam_properties.elevation_angle)
        self._ui.lineEdit_elevation.setText("{0:2.2f}".format(self.cam_properties.elevation_angle))

    def edit_distance_changed(self):
        try:
            f = float(self._ui.lineEdit_distance.text())
            self.cam_properties.distance = f
        except Exception as ex:
            _log.exception(ex)

    def dial_distance_changed(self, value):
        self.cam_properties.distance = value / 1000.

    def dial_azimuth_changed(self, value):
        self.cam_properties.azimuth_angle = value

    def dial_elevation_changed(self, value):
        self.cam_properties.elevation_angle = value
