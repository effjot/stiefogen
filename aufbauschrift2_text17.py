import stiefo
from PyQt4 import QtGui, QtCore

filenamebase = "Aufbauschrift2_Text17"

with open(filenamebase + '.txt', "r", encoding="utf-8") as f:
    text = f.read()

st = stiefo.text_to_list(text)

stiefo.render_pdf(st, filenamebase + ".pdf", papersize = QtGui.QPrinter.A4)
