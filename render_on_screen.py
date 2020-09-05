#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui
#import stiefo
from stiefo import Ui_stiefo_curves  # stiefo_curves_interactive


class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_stiefo_curves()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.button_update,
                               QtCore.SIGNAL("clicked()"), self.update_stiefo)

    def update_stiefo(self):
        self.ui.text_entry.insertPlainText('aaaaaaaaaa')


app = QtGui.QApplication(sys.argv)
myapp = StartQT4()
myapp.show()
sys.exit(app.exec_())

#stiefo.render_screen(["t e st", "h a l o", "f l o r i a n"])

