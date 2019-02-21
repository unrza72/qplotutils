# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dock_properties.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogDockProperties(object):
    def setupUi(self, DialogDockProperties):
        DialogDockProperties.setObjectName("DialogDockProperties")
        DialogDockProperties.resize(329, 88)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogDockProperties)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(DialogDockProperties)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.lineEditDockName = QtWidgets.QLineEdit(DialogDockProperties)
        self.lineEditDockName.setObjectName("lineEditDockName")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEditDockName)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButtonOk = QtWidgets.QPushButton(DialogDockProperties)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.horizontalLayout.addWidget(self.pushButtonOk)
        self.pushButtonCancel = QtWidgets.QPushButton(DialogDockProperties)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogDockProperties)
        self.pushButtonOk.clicked.connect(DialogDockProperties.accept)
        self.pushButtonCancel.clicked.connect(DialogDockProperties.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogDockProperties)

    def retranslateUi(self, DialogDockProperties):
        _translate = QtCore.QCoreApplication.translate
        DialogDockProperties.setWindowTitle(_translate("DialogDockProperties", "Dialog"))
        self.label.setText(_translate("DialogDockProperties", "Title:"))
        self.pushButtonOk.setText(_translate("DialogDockProperties", "Ok"))
        self.pushButtonCancel.setText(_translate("DialogDockProperties", "Cancel"))

