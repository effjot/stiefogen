# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stiefo_curves_interactive.ui'
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

class Ui_stiefo_curves(object):
    def setupUi(self, stiefo_curves):
        stiefo_curves.setObjectName(_fromUtf8("stiefo_curves"))
        stiefo_curves.resize(800, 600)
        self.centralwidget = QtGui.QWidget(stiefo_curves)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 781, 541))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.drawing_area = QtGui.QFrame(self.verticalLayoutWidget)
        self.drawing_area.setMinimumSize(QtCore.QSize(400, 200))
        self.drawing_area.setFrameShape(QtGui.QFrame.StyledPanel)
        self.drawing_area.setFrameShadow(QtGui.QFrame.Raised)
        self.drawing_area.setObjectName(_fromUtf8("drawing_area"))
        self.verticalLayout.addWidget(self.drawing_area)
        self.text_entry = QtGui.QPlainTextEdit(self.verticalLayoutWidget)
        self.text_entry.setMaximumSize(QtCore.QSize(16777215, 40))
        self.text_entry.setObjectName(_fromUtf8("text_entry"))
        self.verticalLayout.addWidget(self.text_entry)
        self.button_update = QtGui.QPushButton(self.verticalLayoutWidget)
        self.button_update.setObjectName(_fromUtf8("button_update"))
        self.verticalLayout.addWidget(self.button_update)
        stiefo_curves.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(stiefo_curves)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        stiefo_curves.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(stiefo_curves)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        stiefo_curves.setStatusBar(self.statusbar)

        self.retranslateUi(stiefo_curves)
        QtCore.QMetaObject.connectSlotsByName(stiefo_curves)

    def retranslateUi(self, stiefo_curves):
        stiefo_curves.setWindowTitle(_translate("stiefo_curves", "Stiefo Bezier Curves", None))
        self.button_update.setText(_translate("stiefo_curves", "Update", None))

