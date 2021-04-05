#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt5.QtCore import Qt

import stiefo


stiefoHeightPrint = 30
stiefoHeightScreen = 50

zeichneHilfslinien = False

def render_pdf(words, filename):
    app = QtWidgets.QApplication(sys.argv)
    window = BezierDrawer(words, filename)
    window.show()
    sys.exit(app.exec_())


def render_screen(words):
    app = QtWidgets.QApplication(sys.argv)
    window = BezierDrawer(words, [])
    window.show()
    sys.exit(app.exec_())


class print_renderer:
    def __init__(self, printer, painter):
        self.printer = printer
        self.painter = painter
        self.h = stiefoHeightPrint  # base unit of vertical and horizontal space
        self.pageRect = printer.pageRect(QtPrintSupport.QPrinter.DevicePixel)
        self.x0 = int(self.pageRect.left())
        self.y0 = int(self.pageRect.top() + 3 * self.h)
        self.x1 = int(self.pageRect.right() - 200)
        self.y1 = int(self.pageRect.bottom() - 200)

        self.l1Pen = QtGui.QPen(QtGui.QColor(100, 100, 100))
        self.l2Pen = QtGui.QPen(QtGui.QColor(180, 180, 180))
        self.blackPen = QtGui.QPen(QtCore.Qt.black, 4,
                                  join=QtCore.Qt.RoundJoin, cap=QtCore.Qt.RoundCap)
        self.font = QtGui.QFont("Times", self.h * 72/300 * 1.6)
        self.pgNr = 1
        self.sx = self.h
        self.sy = self.h
        self.px, self.py = self.x0, self.y0
        self.lineatur(self.pgNr)

    def lineatur(self, pgnr = None):
        for y in range(self.y0, self.y1 + 2*self.h, 4 * self.h):
            self.painter.setPen(self.l1Pen)
            self.painter.drawLine(self.x0, y, self.x1, y)
            if (zeichneHilfslinien):
                self.painter.setPen(self.l2Pen)
                self.painter.drawLine(self.x0, y - self.h, self.x1, y - self.h)
                self.painter.drawLine(self.x0, y - 2 * self.h, self.x1, y - 2 * self.h)
                self.painter.drawLine(self.x0, y - 3 * self.h, self.x1, y - 3 * self.h)
        if pgnr:
            self.painter.setPen(self.blackPen)
            self.painter.setFont(self.font)
            self.painter.drawText((self.x1 - self.x0)/2, self.y1 + 100, str(pgnr))

    def line_break(self):
        self.px = self.x0
        self.py += 4*self.h

    def new_page(self):
        self.px, self.py = self.x0, self.y0
        self.printer.newPage()
        self.pgNr += 1
        self.lineatur(self.pgNr)

    def measure_str(self, word):
        fontMetrics = self.painter.fontMetrics()
        return fontMetrics.width(word + " ")

    def draw_text(self, word):
        self.painter.setPen(self.blackPen)
        self.painter.drawText(self.px, self.py, "" + word + " ")
        fontMetrics = self.painter.fontMetrics()
        w = fontMetrics.width(word + " ")
        self.px += w

    def draw_dot_cross(self):
        self.painter.setPen(self.blackPen)
        c = 0.2*self.h
        self.painter.drawLine(self.px - c, self.py - c, self.px + c, self.py + c)
        self.painter.drawLine(self.px - c, self.py + c, self.px + c, self.py - c)
        self.px = self.px + 0.5*self.h

    def draw_curve(self, crv):
        for w, c, _ in crv:
            cc = [(self.px + x * self.sx, self.py - y * self.sy) for x, y in c]
            pp = QtGui.QPainterPath()
            pp.moveTo(*cc[0])
            for i in range(1, len(cc), 3):
                pp.cubicTo(*(cc[i] + cc[i + 1] + cc[i + 2]))
            self.painter.setPen(self.blackPen)
            self.painter.drawPath(pp)
            self.px = self.px + w*self.sx + self.h

    def space_on_line(self):
        return self.x1 - self.px

    def advance(self, d):
        self.px = self.px + d

    # render items are tuples:  (command_code, width_pixels, data, line_breaking)
    # commands:
    #      ('text', width, literal text)   render in normal font
    #      ('curve', width, curve points)  render as Stiefo outlines
    #      ('space', width, None)          horizontal space
    #      ('period', width, None)         period (full stop) mark
    #      ('line', 0, None)               line break
    #      ('page', 0, None)               page break
    # line_breaking:
    #      0   normal line breaking: new line before and after this command allowed
    #      -1  no line break between this and previous command (e.g. interpunction)
    #      +1  no line break between this and next command (opening quotes)

    def prepare(self, words):
        """Build list of render commands from Stiefo-Code words"""
        short = 100  # FIXME use symbol widths instead of pixels
        res = []
        for word in words:
            if word.startswith('~~'):  # literal text, esp. for opening quotes
                word = word[2:]
                w = self.measure_str(word)
                if (w < short):  # keep short text, i.e. quotes, connected to next word
                    res.append(('text', w, word, +1))
                else:
                    res.append(('text', w, word, 0))
            elif word.startswith('~'):  # literal text elsewhere, including after word
                word = word[1:]
                w = self.measure_str(word)
                if (w < short):  # keep short text (closing quotes, interpunction) connected to previous word
                    res.append(('text', w, word, -1))
                else:
                    res.append(('text', w, word, 0))
            else:
                if word == ',':
                    pass
                elif word == 'spc1':
                    res.append(('space', 10.7*self.h, None, 0))
                elif word == 'spc2':
                    res.append(('space', 5*self.h, None, 0))
                elif word == '.':
                    res.append(('period', 0.5*self.h, None, -1))
                elif word == '§§':
                    res.append(('page', 0, None, 0))
                elif word == '§':
                    res.append(('line', 0, None, 0))
                else:
                    crv = stiefo.stiefoWortZuKurve(word)
                    w = 0
                    for dw, _, _ in crv:
                        w += dw
                    res.append(('curve', w * self.sx, crv, 0))

        ## redistribute widths (required space) for protecting against line breaking
        spcreq = [w for _, w, _, _ in res]
        d = 0
        for i in range(len(res) - 1, -1, -1):
            _, w, _, line_breaking = res[i]
            if line_breaking == 0:
                spcreq[i] += d
                d = 0
            elif line_breaking == -1:
                spcreq[i] += d
                d += w  # add this command's width to previous command space requirement
            elif line_breaking == 1:
                spcreq[i] += spcreq[i + 1]
                d = 0

        res = [(t, w, d, r) for ((t, w, d, _), r) in zip(res, spcreq)]
        return res

    def render(self, cmds):
        """Process render commands in list cmds"""
        after_curve = False
        for cmd, w, data, spcreq in cmds:
            ## Put horizontal space between curves (Stiefo outlines)
            if (cmd == 'curve' or cmd == 'period') and after_curve:
                if self.px > self.x0: self.advance(self.h * 0.5)

            ## Line breaks if command doesn't fit on line, based on space required to
            ## keep commands with line_breaking != 0 connected
            if self.px + spcreq + 3*self.h > self.x1:
                if cmd != 'period': self.line_break()
            if self.py > self.y1:
                self.new_page()

            after_curve = False
            if cmd == 'text':
                self.draw_text(data)
            elif cmd == 'curve':
                self.draw_curve(data)
                after_curve = True
            elif cmd == 'space':
                if self.px > self.x0: self.advance(w)
            elif cmd == 'period':
                self.draw_dot_cross()
            elif cmd == 'line':
                self.line_break()
            elif cmd == 'page':
                self.new_page()
            else:
                raise "incorrect render cmd"
        pass


class BezierDrawer(QtWidgets.QMainWindow):
    def __init__(self, stiefoWords, filename):
        super().__init__()
        self.ui = stiefo.Ui_stiefo_curves()
        self.ui.setupUi(self)

        self.ui.button_update.clicked.connect(self.update_text)

        if stiefoWords:
            self.screenWords = stiefoWords
        else:
            self.screenWords = ["e b e c e d e f e g e h e j e k e l e",
                                "e m e n e p e r e s e t e w e z e",
                                "e sch e ch e nd e ng e cht e st e sp e pf e"]
        if not filename:
            self.drawOnScreen = True  # Zum Modellieren und Testen im Hauptfenster zeichnen
            self.ui.drawing_area.update_text(self.screenWords)
        else:  # PDF erzeugen (passiert in paintEvent)
            self.filename = filename
            self.drawOnScreen = False

    def paintEvent(self, e):
        if (self.drawOnScreen):
            pass
        else:
            printer = QtPrintSupport.QPrinter()
            printer.setOutputFileName(self.filename)
            printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
            printer.setResolution(300)

            painter = QtGui.QPainter()
            painter.begin(printer)
            ctx = print_renderer(printer, painter)
            cmds = ctx.prepare(self.screenWords)
            ctx.render(cmds)
            painter.end()

            self.close()

    def update_text(self):
        self.screenWords = stiefo.text_to_list(self.ui.text_entry.toPlainText())
        self.ui.drawing_area.update_text(self.screenWords)


class DrawingArea(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__()
        self.screenWords = []
        self.stiefoHeight = stiefoHeightScreen
        self.showBezierPoints = True
        self.points_radius = 2
        self.showLetterBorders = True
        self.border_overshoot = 10

    def update_text(self, text):
        self.screenWords = text
        self.update()

    def paintEvent(self, e):
        ww = self.frameRect().width()
        wh = self.frameRect().height()
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHints(QtGui.QPainter.Antialiasing, True)
        self.doDrawing(qp, ww, wh)
        qp.end()

    def doDrawing(self, qp, ww, wh):
        h = self.stiefoHeight
        sl = stiefo.slant
        hmargin = 8
        vmargin = 4
        sx = h*1
        sy = h

        x0 = hmargin
        y0 = vmargin + 3*h
        x1 = ww - hmargin
        y1 = wh - vmargin

        # Lineatur
        l1Pen = QtGui.QPen(QtGui.QColor(190, 190, 190))
        l2Pen = QtGui.QPen(QtGui.QColor(220, 220, 220))
        for y in range(y0, y1, 4 * h):
            qp.setPen(l1Pen)
            qp.drawLine(x0, y, x1, y)
            qp.setPen(l2Pen)
            qp.drawLine(x0, y - h, x1, y - h)
            qp.drawLine(x0, y - 2 * h, x1, y - 2 * h)
            qp.drawLine(x0, y - 3 * h, x1, y - 3 * h)

        blackPen = QtGui.QPen(QtCore.Qt.black, 2)
        grayPen = QtGui.QPen(QtCore.Qt.gray)
        redPen = QtGui.QPen(QtCore.Qt.red)
        bluePen = QtGui.QPen(QtCore.Qt.blue, 2,
                             join=QtCore.Qt.RoundJoin, cap=QtCore.Qt.RoundCap)
        greenPen = QtGui.QPen(QtCore.Qt.darkGreen)
        redBrush = QtGui.QBrush(QtCore.Qt.red)
        font = QtGui.QFont("Times", h)

        px, py = hmargin, vmargin + 3*h  # start position for drawing
        for word in self.screenWords:
            if (word[0].isalpha()):
                for w, c, p in stiefo.stiefoWortZuKurve(word):
                    w = w * sx

                    if px + w > ww:
                        px = hmargin
                        py += 4*h

                    # Bezier-Punkte
                    cc = [(10 + px + x * sx, py - y * sy) for x, y in c]

                    # Glyph-Positionen
                    pp = [(10 + px + x * sx, py - y * sy) for x, y in p]

                    # Bezier-Punkte einzeichnen
                    if self.showBezierPoints:
                        qp.setPen(redPen)
                        qp.setBrush(redBrush)
                        for x, y in cc:
                            qp.drawEllipse(QtCore.QPointF(x, y),
                                           self.points_radius, self.points_radius)

                        # Bezier-Punkte mit Linien verbinden
                        qp.setBrush(QtCore.Qt.NoBrush)
                        qp.setPen(greenPen)
                        o = None
                        for x, y in cc:
                            if o:
                                qp.drawLine(o[0], o[1], x, y)
                            o = (x, y)

                    # Glyph-Grenzen zeichnen
                    if self.showLetterBorders:
                        qp.setPen(grayPen)
                        d = self.border_overshoot
                        for x, y in pp:
                            qp.drawLine(x - d*sl, y + d, x + sl*(h + d), y - h - d)

                    # Wort als Bezier-Pfad zeichnen
                    pp = QtGui.QPainterPath()
                    pp.moveTo(*cc[0])  # "unpacking argument list"
                    for i in range(1, len(cc), 3):
                        pp.cubicTo(*(cc[i] + cc[i + 1] + cc[i + 2]))  # 2 Kontrollpunkte,
                                                         # gefolgt von 1 Endpunkt
                    qp.setPen(bluePen)
                    qp.drawPath(pp)

                    px = px + w + h
            else:
                if (word == ','):
                    px = px + 2.5*h
                elif (word == '.'):
                    px = px + 5*h
                elif word == '§':
                    px = 10
                    py += 4*h
                else:
                    qp.setPen(blackPen)
                    qp.setFont(font)
                    fontMetrics = qp.fontMetrics()
                    qp.drawText(px, py, word)
                    w = fontMetrics.width(word)
                    px += w
