#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math

from PyQt4 import QtGui, QtCore
import stiefo


stiefoHeightPrint = 30
stiefoHeightScreen = 75

zeichneHilfslinien = True
text_y_offset = 0.1 * stiefoHeightPrint


def render_pdf(words, filename):
    app = QtGui.QApplication(sys.argv)
    window = BezierDrawer(words, filename)
    window.show()
    sys.exit(app.exec_())


def render_screen(words):
    app = QtGui.QApplication(sys.argv)
    window = BezierDrawer(words, [])
    window.show()
    sys.exit(app.exec_())


class print_renderer:
    def __init__(self, printer, painter):
        self.h = stiefoHeightPrint
        self.word_space = 0.5 * self.h
        self.printer = printer
        self.painter = painter
        self.pageRect = printer.pageRect(QtGui.QPrinter.DevicePixel)
        self.x0 = int(self.pageRect.left())
        self.y0 = int(self.pageRect.top() + 3 * self.h)
        self.x1 = int(self.pageRect.right() - 200)
        self.y1 = int(self.pageRect.bottom() - 200)

        self.l1Pen = QtGui.QPen(QtGui.QColor(100, 100, 100))
        self.l2Pen = QtGui.QPen(QtGui.QColor(180, 180, 180))
        self.blackPen = QtGui.QPen(QtCore.Qt.black, 4,
                                  join=QtCore.Qt.RoundJoin, cap=QtCore.Qt.RoundCap)
        self.font = QtGui.QFont("Arial", self.h * 72/300 * 1.6)
        self.pgNr = 1
        self.sx = self.h
        self.sy = self.h
        self.px, self.py = self.x0 + self.word_space, self.y0
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
        self.px = self.x0 + self.word_space
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
        self.painter.drawText(self.px, self.py - text_y_offset, "" + word + " ")
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
        for w, c, _, outline_offset in crv:
            # Kurve verschieben (Startpunkt anpassen)
            dx = 0
            dy = 0
            if outline_offset:
                dx = outline_offset[0] * self.sx
                dy = outline_offset[1] * self.sy
                self.px += dx - self.word_space
                self.py -= dy

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

    # render items are tuples:  (cmd, width, data)
    # cmd:
    #      ('text', width, literal text)
    #      ('curve', width, stiefo curve points)
    #      ('space', width, None)
    #      ('period', width, None)
    #      ('line', 0, None)   line break
    #      ('page', 0, None)   page break
    def prepare(self, words):
        res = []
        for word in words:
            short = 100
            if word.startswith('~~'):
                word = word[2:]
                w = self.measure_str(word)
                if (w < short):
                    res.append(('text', w, word, +1))
                else:
                    res.append(('text', w, word, 0))
            elif word.startswith('~'):
                word = word[1:]
                w = self.measure_str(word)
                if (w < short):
                    res.append(('text', w, word, -1))
                else:
                    res.append(('text', w, word, 0))
            else:
                if word == '':
                    pass
                elif word == '&':
                    res.append(('space', -0.4*self.h, None, 0))
                elif word == 'spc1':
                    res.append(('space', 10.7*self.h, None, 0))
                elif word == ',' or word == 'spc2':
                    res.append(('space', 5*self.h, None, 0))
                elif word == '..':
                    res.append(('period', 0.5*self.h, None, -1))
                    res.append(('space', 5*self.h, None, 0))
                elif word == '§§':
                    res.append(('page', 0, None, 0))
                elif word == '§':
                    res.append(('line', 0, None, 0))
                else:
                    crv = stiefo.stiefoWortZuKurve(word)
                    w = 0
                    for dw, _, _, _ in crv:
                        w += dw  # FIXME: was mit disjointed?!
                    res.append(('curve', w*self.sx, crv, 0))

        spcreq = [w for _, w, _, _ in res]
        d = 0
        for i in range(len(res) - 1, -1, -1):
            _, w, _, z = res[i]
            if z == 0:
                spcreq[i] += d
                d = 0
            elif z == -1:
                spcreq[i] += d
                d += w
            elif z == 1:
                spcreq[i] += spcreq[i + 1]
                d = 0

        res = [(t, w, d, r) for ((t, w, d, _), r) in zip(res, spcreq)]
        return res

    def render(self, cmds):
        flag = False
        for cmd, w, data, spc in cmds:
            if (cmd == 'curve' or cmd == 'period') and flag:
                if self.px > self.x0: self.advance(self.word_space)

            if self.px + spc + 3*self.h > self.x1:
                if cmd != 'period': self.line_break()
            if self.py > self.y1:
                self.new_page()

            flag = False
            if cmd == 'text':
                self.draw_text(data)
            elif cmd == 'curve':
                self.draw_curve(data)
                flag = True
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


class BezierDrawer(QtGui.QMainWindow):
    def __init__(self, stiefoWords, filename, parent=None):
        super(BezierDrawer, self).__init__()
        QtGui.QWidget.__init__(self, parent)
        self.ui = stiefo.Ui_stiefo_curves()
        self.ui.setupUi(self)

        QtCore.QObject.connect(self.ui.button_update, QtCore.SIGNAL("clicked()"),
                               self.update_text)

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
            printer = QtGui.QPrinter()
            printer.setOutputFileName(self.filename)
            printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
            printer.setResolution(300)
            printer.setPaperSize(QtGui.QPrinter.A4)

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


class DrawingArea(QtGui.QFrame):
    def __init__(self, parent):
        super(DrawingArea, self).__init__()
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
        word_space = h
        sl = stiefo.slant
        hmargin = 8
        vmargin = 4
        sx = h*1
        sy = h
        sl = stiefo.slant

        x0 = hmargin + word_space
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
        font     = QtGui.QFont("Arial", h)

        px, py = hmargin, vmargin + 3*h  # start position for drawing
        for word in self.screenWords:
            if stiefo.isword(word) and word not in (',', '..'):
                for w, c, p, outline_offset in stiefo.stiefoWortZuKurve(word):
                    w = w * sx  # Wortlänge

                    # Kurve verschieben (Startpunkt anpassen)
                    dx = 0
                    dy = 0
                    if outline_offset:
                        dx = outline_offset[0] * sx
                        dy = outline_offset[1] * sy
                        px += dx - word_space
                        py -= dy

                    # Zeilenumbruch  TODO: Offset vs Zeilenumbruch?!
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

                    # Neue Zeichenposition berechnen
                    px = px + w + word_space
                    py += dy  # Offset rückgängig machen
            else:
                if (word == ','):
                    px = px + 2.5*h
                elif (word == '..'):
                    px = px + 5*h
                elif word == '§':
                    px = 10
                    py += 4*h
                else:
                    qp.setPen(blackPen)
                    qp.setFont(font)
                    fontMetrics = qp.fontMetrics()
                    qp.drawText(px, py - text_y_offset, word)
                    w = fontMetrics.width(word)
                    px += w
