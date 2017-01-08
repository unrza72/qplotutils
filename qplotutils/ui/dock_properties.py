# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dock_properties.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DialogDockProperties(object):
    def setupUi(self, DialogDockProperties):
        DialogDockProperties.setObjectName(_fromUtf8("DialogDockProperties"))
        DialogDockProperties.resize(329, 88)
        self.verticalLayout = QtGui.QVBoxLayout(DialogDockProperties)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(DialogDockProperties)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.lineEditDockName = QtGui.QLineEdit(DialogDockProperties)
        self.lineEditDockName.setObjectName(_fromUtf8("lineEditDockName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEditDockName)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtGui.QSpacerItem(20, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButtonOk = QtGui.QPushButton(DialogDockProperties)
        self.pushButtonOk.setObjectName(_fromUtf8("pushButtonOk"))
        self.horizontalLayout.addWidget(self.pushButtonOk)
        self.pushButtonCancel = QtGui.QPushButton(DialogDockProperties)
        self.pushButtonCancel.setObjectName(_fromUtf8("pushButtonCancel"))
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(DialogDockProperties)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL(_fromUtf8("clicked()")), DialogDockProperties.accept)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL(_fromUtf8("clicked()")), DialogDockProperties.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogDockProperties)

    def retranslateUi(self, DialogDockProperties):
        DialogDockProperties.setWindowTitle(_translate("DialogDockProperties", "Dialog", None))
        self.label.setText(_translate("DialogDockProperties", "Title:", None))
        self.pushButtonOk.setText(_translate("DialogDockProperties", "Ok", None))
        self.pushButtonCancel.setText(_translate("DialogDockProperties", "Cancel", None))

