# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'playback.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
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

class Ui_PlaybackControl(object):
    def setupUi(self, PlaybackControl):
        PlaybackControl.setObjectName(_fromUtf8("PlaybackControl"))
        PlaybackControl.resize(805, 40)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(PlaybackControl)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, -1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.button_back = QtGui.QPushButton(PlaybackControl)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_back.sizePolicy().hasHeightForWidth())
        self.button_back.setSizePolicy(sizePolicy)
        self.button_back.setMaximumSize(QtCore.QSize(32, 32))
        self.button_back.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/player/icons/media-seek-backward.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_back.setIcon(icon)
        self.button_back.setIconSize(QtCore.QSize(32, 32))
        self.button_back.setFlat(True)
        self.button_back.setObjectName(_fromUtf8("button_back"))
        self.horizontalLayout.addWidget(self.button_back)
        self.button_play_pause = QtGui.QPushButton(PlaybackControl)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_play_pause.sizePolicy().hasHeightForWidth())
        self.button_play_pause.setSizePolicy(sizePolicy)
        self.button_play_pause.setMinimumSize(QtCore.QSize(36, 32))
        self.button_play_pause.setMaximumSize(QtCore.QSize(36, 32))
        self.button_play_pause.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/player/icons/media-playback-start.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_play_pause.setIcon(icon1)
        self.button_play_pause.setIconSize(QtCore.QSize(24, 24))
        self.button_play_pause.setFlat(True)
        self.button_play_pause.setObjectName(_fromUtf8("button_play_pause"))
        self.horizontalLayout.addWidget(self.button_play_pause)
        self.button_next = QtGui.QPushButton(PlaybackControl)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_next.sizePolicy().hasHeightForWidth())
        self.button_next.setSizePolicy(sizePolicy)
        self.button_next.setMaximumSize(QtCore.QSize(32, 32))
        self.button_next.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/player/icons/media-seek-forward.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_next.setIcon(icon2)
        self.button_next.setIconSize(QtCore.QSize(32, 32))
        self.button_next.setFlat(True)
        self.button_next.setObjectName(_fromUtf8("button_next"))
        self.horizontalLayout.addWidget(self.button_next)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.slider_index = QtGui.QSlider(PlaybackControl)
        self.slider_index.setMaximum(600)
        self.slider_index.setOrientation(QtCore.Qt.Horizontal)
        self.slider_index.setTickPosition(QtGui.QSlider.TicksBelow)
        self.slider_index.setTickInterval(100)
        self.slider_index.setObjectName(_fromUtf8("slider_index"))
        self.horizontalLayout_2.addWidget(self.slider_index)
        self.edit_timestamp = QtGui.QLineEdit(PlaybackControl)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_timestamp.sizePolicy().hasHeightForWidth())
        self.edit_timestamp.setSizePolicy(sizePolicy)
        self.edit_timestamp.setMaximumSize(QtCore.QSize(90, 16777215))
        self.edit_timestamp.setObjectName(_fromUtf8("edit_timestamp"))
        self.horizontalLayout_2.addWidget(self.edit_timestamp)

        self.retranslateUi(PlaybackControl)
        QtCore.QMetaObject.connectSlotsByName(PlaybackControl)

    def retranslateUi(self, PlaybackControl):
        PlaybackControl.setWindowTitle(_translate("PlaybackControl", "Form", None))

import resources_rc
