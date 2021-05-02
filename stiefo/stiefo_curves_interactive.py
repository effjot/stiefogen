# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stiefo_curves_interactive.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_stiefo_curves(object):
    def setupUi(self, stiefo_curves):
        stiefo_curves.setObjectName("stiefo_curves")
        stiefo_curves.resize(858, 685)
        self.centralwidget = QtWidgets.QWidget(stiefo_curves)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.drawing_area = DrawingArea(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.drawing_area.sizePolicy().hasHeightForWidth())
        self.drawing_area.setSizePolicy(sizePolicy)
        self.drawing_area.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.drawing_area.setFrameShadow(QtWidgets.QFrame.Raised)
        self.drawing_area.setObjectName("drawing_area")
        self.verticalLayout.addWidget(self.drawing_area)
        self.text_entry = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.text_entry.setMaximumSize(QtCore.QSize(16777215, 40))
        self.text_entry.setObjectName("text_entry")
        self.verticalLayout.addWidget(self.text_entry)
        self.button_update = QtWidgets.QPushButton(self.centralwidget)
        self.button_update.setObjectName("button_update")
        self.verticalLayout.addWidget(self.button_update)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        stiefo_curves.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(stiefo_curves)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 858, 25))
        self.menubar.setObjectName("menubar")
        stiefo_curves.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(stiefo_curves)
        self.statusbar.setObjectName("statusbar")
        stiefo_curves.setStatusBar(self.statusbar)

        self.retranslateUi(stiefo_curves)
        QtCore.QMetaObject.connectSlotsByName(stiefo_curves)

    def retranslateUi(self, stiefo_curves):
        _translate = QtCore.QCoreApplication.translate
        stiefo_curves.setWindowTitle(_translate("stiefo_curves", "Stiefo Bezier Curves"))
        self.button_update.setText(_translate("stiefo_curves", "Update"))

from stiefo.render import DrawingArea
