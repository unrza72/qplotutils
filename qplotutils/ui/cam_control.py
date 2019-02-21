# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cam_control.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from qtpy import QtCore, QtGui, QtWidgets

class Ui_CamControl(object):
    def setupUi(self, CamControl):
        CamControl.setObjectName("CamControl")
        CamControl.resize(283, 156)
        self.verticalLayout = QtWidgets.QVBoxLayout(CamControl)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(CamControl)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(CamControl)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(CamControl)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.dial_distance = QtWidgets.QDial(CamControl)
        self.dial_distance.setMinimum(0)
        self.dial_distance.setMaximum(1000)
        self.dial_distance.setProperty("value", 0)
        self.dial_distance.setWrapping(True)
        self.dial_distance.setObjectName("dial_distance")
        self.gridLayout.addWidget(self.dial_distance, 1, 0, 1, 1)
        self.dial_azimuth = QtWidgets.QDial(CamControl)
        self.dial_azimuth.setMinimum(-180)
        self.dial_azimuth.setMaximum(180)
        self.dial_azimuth.setWrapping(True)
        self.dial_azimuth.setObjectName("dial_azimuth")
        self.gridLayout.addWidget(self.dial_azimuth, 1, 1, 1, 1)
        self.dial_elevation = QtWidgets.QDial(CamControl)
        self.dial_elevation.setMinimum(-90)
        self.dial_elevation.setMaximum(90)
        self.dial_elevation.setInvertedAppearance(False)
        self.dial_elevation.setWrapping(True)
        self.dial_elevation.setNotchesVisible(False)
        self.dial_elevation.setObjectName("dial_elevation")
        self.gridLayout.addWidget(self.dial_elevation, 1, 2, 1, 1)
        self.lineEdit_distance = QtWidgets.QLineEdit(CamControl)
        self.lineEdit_distance.setObjectName("lineEdit_distance")
        self.gridLayout.addWidget(self.lineEdit_distance, 2, 0, 1, 1)
        self.lineEdit_azimuth = QtWidgets.QLineEdit(CamControl)
        self.lineEdit_azimuth.setObjectName("lineEdit_azimuth")
        self.gridLayout.addWidget(self.lineEdit_azimuth, 2, 1, 1, 1)
        self.lineEdit_elevation = QtWidgets.QLineEdit(CamControl)
        self.lineEdit_elevation.setObjectName("lineEdit_elevation")
        self.gridLayout.addWidget(self.lineEdit_elevation, 2, 2, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 3, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(CamControl)
        QtCore.QMetaObject.connectSlotsByName(CamControl)

    def retranslateUi(self, CamControl):
        _translate = QtCore.QCoreApplication.translate
        CamControl.setWindowTitle(_translate("CamControl", "Form"))
        self.label.setText(_translate("CamControl", "Distance"))
        self.label_2.setText(_translate("CamControl", "Azimuth"))
        self.label_3.setText(_translate("CamControl", "Elecation"))
        self.lineEdit_distance.setText(_translate("CamControl", "0"))
        self.lineEdit_azimuth.setText(_translate("CamControl", "0"))
        self.lineEdit_elevation.setText(_translate("CamControl", "0"))

