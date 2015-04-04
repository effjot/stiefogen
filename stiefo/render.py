#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4 import QtGui, QtCore
from stiefo import symbols

#-----------------------------------------------------


def render_pdf(words, filename):
    app = QtGui.QApplication(sys.argv)
    ex = BezierDrawer(words, filename)
    ex.show()
    app.exec_()


class renderer:
    def __init__(self, printer, painter):
        self.printer = printer
        self.pageRect = printer.pageRect(QtGui.QPrinter.DevicePixel)
        self.painter = painter
        self.h = 30
        self.x0 = int(self.pageRect.left())
        self.y0 = int(self.pageRect.top() + 3 * self.h)
        self.x1 = int(self.pageRect.right()-200)
        self.y1 = int(self.pageRect.bottom()-200)
        self.l1Pen = QtGui.QPen(QtGui.QColor(100, 100, 100))
        self.l2Pen = QtGui.QPen(QtGui.QColor(180, 180, 180))
        self.bluePen = QtGui.QPen(QtCore.Qt.black, 4, join=QtCore.Qt.RoundJoin, cap=QtCore.Qt.RoundCap)
        self.font = QtGui.QFont("AHo", self.h*72/300 *1.6)
        self.pgNr = 1
        self.sx = self.h
        self.sy = self.h
        self.px,self.py = self.x0,self.y0
        self.lineatur(self.pgNr)

    def lineatur(self, pgnr = None):
        for y in range(self.y0, self.y1+2*self.h, 4 * self.h):
            self.painter.setPen(self.l1Pen)
            self.painter.drawLine(self.x0, y, self.x1, y)
            self.painter.setPen(self.l2Pen)
            self.painter.drawLine(self.x0, y - self.h, self.x1, y - self.h)
            self.painter.drawLine(self.x0, y - 2 * self.h, self.x1, y - 2 * self.h)
            self.painter.drawLine(self.x0, y - 3 * self.h, self.x1, y - 3 * self.h)
        if pgnr:
            self.painter.setPen(self.bluePen)
            self.painter.setFont(self.font)
            self.painter.drawText((self.x1-self.x0)/2,self.y1+100,str(pgnr))

    def line_break(self):
        self.px = self.x0
        self.py += 4*self.h

    def new_page(self):
        self.px,self.py = self.x0,self.y0
        self.printer.newPage()
        self.pgNr+=1
        self.lineatur(self.pgNr)

    def measure_str(self, word):
        fontMetrics = self.painter.fontMetrics()
        return fontMetrics.width(word+" ")

    def draw_text(self, word):
        self.painter.setPen(self.bluePen)
        self.painter.drawText(self.px, self.py,""+word+" ")
        fontMetrics = self.painter.fontMetrics()
        w = fontMetrics.width(word+" ")
        self.px += w

    def draw_dot_cross(self):
        self.painter.setPen(self.bluePen)
        c = 0.2*self.h
        self.painter.drawLine(self.px - c, self.py - c, self.px + c, self.py + c)
        self.painter.drawLine(self.px - c, self.py + c, self.px + c, self.py - c)
        self.px = self.px + 0.5*self.h

    def draw_curve(self, crv):
        for w,c,_ in crv:
            cc = [(self.px + x * self.sx, self.py - y * self.sy) for x, y in c]
            pp = QtGui.QPainterPath()
            pp.moveTo(*cc[0])
            for i in range(1, len(cc), 3):
                pp.cubicTo(*(cc[i] + cc[i + 1] + cc[i + 2]))
            self.painter.setPen(self.bluePen)
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
                    crv = symbols.stiefoWortZuKurve(word)
                    w = 0
                    for dw,_,_ in crv:
                        w += dw
                    res.append(('curve', w*self.sx, crv, 0))

        spcreq = [w for _,w,_,_ in res]
        d = 0
        for i in range(len(res)-1,-1,-1):
            _,w,_,z = res[i]
            if z == 0:
                spcreq[i] += d
                d = 0
            elif z ==-1:
                spcreq[i] += d
                d += w
            elif z == 1:
                spcreq[i] += spcreq[i+1]
                d = 0

        res = [(t,w,d,r) for ((t,w,d,_),r) in zip(res, spcreq)]
        return res

    def render(self, cmds):
        flag = False
        for cmd,w,data,spc in cmds:
            if (cmd == 'curve' or cmd == 'period') and flag:
                if self.px > self.x0: self.advance(self.h*0.5)

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



def RenderPdf(words, filename):
    printer = QtGui.QPrinter()
    printer.setOutputFileName(filename)
    printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
    printer.setResolution(300)

    painter = QtGui.QPainter()
    painter.begin(printer)

    ctx = renderer(printer, painter)

    cmds = ctx.prepare(words)
    ctx.render(cmds)
    painter.end()




class BezierDrawer(QtGui.QWidget):

    def __init__(self, stiefoWords, filename):
        super(BezierDrawer, self).__init__()

        self.ww = 1200
        self.wh = 800
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowTitle('Bezier Curves')
        self.screenWords = ["e b e c e d e f e g e h e j e k e l e",
                            "e m e n e p e r e s e t e w e z e",
                            "e sch e ch e nd e ng e cht e st e sp e pf e"]
        self.stiefoHeight =30
        self.showLetterBorders = False

        RenderPdf(stiefoWords, filename)


    def paintEvent(self, e):
        self.close()
        #qp = QtGui.QPainter()
        #qp.begin(self)
        #qp.setRenderHints(QtGui.QPainter.Antialiasing, True)
        #self.doDrawing(qp)
        #qp.end()

    def doDrawing(self, qp):
        h = self.stiefoHeight
        sx = h*1
        sy = h

        x0 = 10
        y0 = 10 + 3 * h
        x1 = self.ww
        y1 = self.wh

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
        redPen = QtGui.QPen(QtCore.Qt.red)
        bluePen = QtGui.QPen(QtCore.Qt.blue, 2, join=QtCore.Qt.RoundJoin, cap=QtCore.Qt.RoundCap)
        greenPen = QtGui.QPen(QtCore.Qt.darkGreen)
        redBrush = QtGui.QBrush(QtCore.Qt.red)
        font = QtGui.QFont("Arial", h)

        px,py = 10,10+3*h
        for word in self.screenWords:

            if (word[0].isalpha()):
                for w,c,p in symbols.stiefoWortZuKurve(word):
                    w=w*sx

                    if px + w > 1200:
                        px = 10
                        py += 4*h

                    cc = [(10 + px + x * sx, py - y * sy) for x, y in c]

                    pp = [(10 + px + x * sx, py - y * sy) for x, y in p]

                    # qp.setPen(redPen)
                    # qp.setBrush(redBrush)
                    # for x,y in cc:
                    # qp.drawEllipse(x - 1, y - 1, 2, 2)
                    # qp.setBrush(QtCore.Qt.NoBrush)
                    #
                    # qp.setPen(greenPen)
                    # o = None
                    # for x,y in cc:
                    #     if o:
                    #         qp.drawLine(o[0], o[1], x,y)
                    #     o=(x,y)

                    if self.showLetterBorders:
                        qp.setPen(greenPen)
                        d = 10
                        #for x,y in pp: qp.drawLine(x-d*sl, y+d, x+sl*(h+d),y-h-d)

                    pp = QtGui.QPainterPath()
                    pp.moveTo(*cc[0])
                    for i in range(1, len(cc), 3):
                        pp.cubicTo(*(cc[i] + cc[i + 1] + cc[i + 2]))
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
                    qp.setFont(font)
                    fontMetrics = qp.fontMetrics()
                    qp.drawText(px,py,word)
                    w = fontMetrics.width(word)
                    px += w

