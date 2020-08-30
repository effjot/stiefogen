import doctest
from os import listdir
from os.path import isfile, join
import re

from PyQt4 import QtGui, QtCore


import math


#===================================================================================


sl = math.sin( 15 * math.pi/180)

di = 0.4
di_extra = 0.3
de = 1.3
du = 3
dkv = 0.6  # Konsonantenverbindung

vokalAbstaende = {
    #     (DX, DY, eff. Abst)
    'a' : (1,1, de),
    'e' : (1,0, de),
    'i' : (1,-1, di),
    'I': (1, -1, di + di_extra),
    'o' : (2,-1, du),
    'u' : (2,0, du),
    'ö' : (1,2, de + 0.3),
    'ei' : (2,1, du),
    'eu' : (2,2, du),
    'oi' : (2,2, du),
    'ä' : (1,0, de),
    'ü' : (1,-1, di),
    'au' : (2,0, du),
}

def SplitStiefoWord(st):
    """Zerlege das Wort w in Vokale und Konsonanten.
    Vokale werden als (dx,dy,ea) ausgegeben, wobei
    dy die Werte -1, 0, +1, +2 haben kann für i,e,a,ö Stufen.
    dx hat die Werte 0,1,2 für Konsonantenverbindung, e, u.
    ea ist der effektive Abstand horizontal, der für diesen Vokal verwendet wird.
    '_' und '-' werden am Anfang und Ende angefügt, wenn das
    Wort mit einem Vokal anfängt oder aufhört
    >>> SplitStiefoWord("b e r n")
    ['b', (1, 0, 1.2), 'r', (0, 0, 0.6), 'n']
    >>> SplitStiefoWord("e r d e")
    ['_', (1, 0, 1.2), 'r', (0, 0, 0.6), 'd', (1, 0, 1.2), '-']
    >>> SplitStiefoWord("n a t i o n")
    ['n', (1, 1, 1.2), 't', (1, -1, 0.6), 'c', (2, -1, 2.8), 'n']
    """
    w = []
    first = True
    pz = False
    pv = False
    for z in (st.split(' ')):
        v = z in vokalAbstaende
        if first and v in ('i', 'ü'):
            z = 'I'
        if pv and v:
            w.append('c')
        if pz in ('i', 'ü') and z in ('b', 'f', 'k', 'm', 'p', 'z', 'cht', 'ng', 'nk'):
            w[-1] = 'I'
        w.append(z)
        pz = z
        pv = v
        first = False
    if w[-1] in ('i', 'ü'):
        w[-1] = 'I'
    x = []
    k = False
    for l in w:
        if l in vokalAbstaende:
            if not x:
                x.append('_')
            x.append(vokalAbstaende[l])
            k = False
        else:
            if k:
                x.append((0,0,dkv))
            x.append(l)
            k = True
    if not k:
        x.append('-')
    return x

# -----------------------------------------------



def shiftToPos(gl, dx, dy):
    return [(dx + x + y * sl, dy + y) for (x, y) in gl]


def obenSpitz(dl):
    b = [(0, 1)] if dl else []
    m = [(0, 1), (0, 1),
         (0.0, 0.5)]
    return b + m


def untenSpitz(dr):
    m = [(0.0, 0.5),
         (0, 0), (0, 0)]
    e = [(0, 0)] if dr else []
    return m + e


def obenRund(dl):
    b = [(-0.5, 1)] if dl else [(-0.35, 0.9), (-0.35, 0.9), (-0.25, 1)]
    m = [(-0.2, 1), (0, 1),
         (0.0, 0.75)]
    return b + m


def untenRund(dr, runder = True):
    if runder:
        m = [(0, 0.4),
             (0, 0), (0.3, 0)]
        e = [(0.5, 0)] if dr else [(0.35, 0), (0.45, 0.1), (0.45, 0.1)]
    else:
        m = [(0, 0.25),
             (0, 0), (0.2, 0)]
        e = [(0.5, 0)] if dr else [(0.25, 0), (0.4, 0.1), (0.4, 0.1)]
    return m + e


def untenEingelegt(dr):
    m = [(0, 0.25),
         (0.0, 0.0), (-0.2, 0)]
    e = [(-0.5, 0.0)] if dr else []
    return m + e

def obenGewoelbt(dl):
    b = [(-0.3, 0.95)] if dl else []
    m = [(0.2, 1), (0, 1),
         (0.0, 0.75)]
    return b + m


def scale(g, sx, sy, s=0):
    return [(x * sx + (1 - y) * s, y * sy) for (x, y) in g]


def shift(g, dx, dy=0):
    return [(x + dx, y + dy) for (x, y) in g]



def glyph_d(dl, dr):
    b = [(0, 0.5)] if dl else []
    m = [(0, 0.5), (0, 0.5),
         (0.2, 0), (0.5, 0)]
    e = [(0.8, 0)] if dr else [(0.5, 0), (0.6, 0.05), (0.6, 0.05)]
    return (0.5, b + m + e)


def glyph_n(dl, dr):
    b = [(-0.3, 0.5)] if dl else [(-0.2, 0.45), (-0.2, 0.45), (-0.1, 0.5)]
    m = [(-0.1, 0.5), (0.2, 0.5),
         (0.4, 0), (0.4, 0)]
    e = [(0.4, 0)] if dr else []
    return (0.4, b + m + e)


def glyph_r0(dl, dr):
    b = [(-0.3, 0.5)] if dl else [(-0.2, 0.5), (-0.2, 0.5), (-0.1, 0.5)]
    m = [(-0.1, 0.5), (0.2, 0.5),
         (0.2, 0), (0.5, 0.0)]
    e = [(0.7, 0.0)] if dr else [(0.5, 0.0), (0.6, 0.0), (0.6, 0.0)]
    return (0.4, b + m + e)


def glyph_r(dl, dr):
    y1 = 0.5
    y0 = 0.0
    b = [(-0.3, y1)] if dl else [(-0.2, y1), (-0.2, y1), (-0.1, y1)]
    m = [(-0.1, y1), (0.2, y1),
         (0.2, y0), (0.5, y0)]
    e = [(0.7, y0)] if dr else [(0.5, y0), (0.6, y0 + 0.1), (0.6, y0 + 0.1)]
    return (0.4, b + m + e)


def glyph_w(dl, dr):
    b = [(-0.4, 0.9)] if dl else []
    m = [(0, 1), (-0.4, 0.9),
         (-0.4, 0), (0, 0)]
    e = [(0.3, 0)] if dr else [(0.1, 0), (0.2, 0.1), (0.2, 0.1)]
    return (0.3, shift(b + m + e,0.3))


def glyph_m(dl, dr):
    b = [(-0.3, 1)] if dl else [(-0.2, 0.9), (-0.2, 0.9), (-0.1, 1)]
    m = [(0, 1), (0.3, 1),
         (0.3, 0.0), (0, 0)]
    e = [(-0.4, 0.0)] if dr else []
    return (0.3, shift(b + m + e,0.1))


def glyph_p(dl, dr):
    b = [(0, 1)] if dl else []
    m = [(0, 1), (0, 0.1),
         (0.4, 0.9), (0.4, 0)]
    e = [(0.4, 0)] if dr else []
    return (0.4, b + m + e)


def glyph_b(dl, dr):
    b = obenSpitz(dl)
    m = [(0.0, 0.5)]
    e = untenSpitz(dr)
    return 0, b + m + e


def glyph_j(dl, dr):
    w, g = glyph_b(dl, dr)
    return (0.7, scale(g, 1, 1, 0.7))


def glyph_t(dl, dr):
    w,g = glyph_b(dl,dr)
    return (0, scale(g, 1, 0.5))


def glyph_g(dl, dr):
    w,g = glyph_b(dl,dr)
    return (0.4, scale(g, 1, 0.5, 0.4))


def glyph_f(dl, dr, runder = True):
    b = obenSpitz(dl)
    m = [(0.0, 0.5)]
    e = untenRund(dr, runder = runder)
    return (0.2, b + m + e)


def glyph_pf(dl, dr):
    w, g = glyph_f(dl, dr, runder = False)
    return (0.8, scale(g, 1, 1, 0.7))


def glyph_nd(dl, dr):
    b = obenRund(dl)
    m = [(0, 0.5)]
    e = untenSpitz(dr)
    return (0.3, shift(b + m + e,0.3))


def glyph_ng(dl, dr):
    w, g = glyph_nd(dl, dr)
    return (0.8, shift(scale(g, 1, 1, 0.6), -0.1))


def glyph_k(dl, dr, runder = True):
    b = obenRund(dl)
    m = [(0, 0.5)]
    e = untenRund(dr, runder = runder)
    return (0.3, shift(b + m + e, 0.15))


def glyph_zw(dl, dr):
    w,g = glyph_z(dl,dr)
    return (0.2, scale(g, 1, 0.5))

def glyph_schw(dl, dr):
    w,g = glyph_sch(dl,dr)
    return (0.4, scale(g, 1, 0.5))


def glyph_qu(dl, dr):
    w,g = glyph_f(dl,dr)
    return (0.2, scale(g, 1, 0.5))


def glyph_cht(dl, dr):
    w,g = glyph_k(dl, dr, runder = False)
    return (0.8, scale(g, 1, 1, 0.5))


def glyph_h(dl, dr):
    b = obenSpitz(dl)
    m = [(0, 0.5)]
    e = untenEingelegt(dr)
    return (0.2, shift(b + m + e, 0.2))


def glyph_th(dl, dr):
    w,g = glyph_h(dl,dr)
    return (0.2, scale(g, 1, 0.5))


def glyph_tsch(dl, dr):
    w,g = glyph_nd(dl,dr)
    return (0.3, scale(g, 1, 0.5))


def glyph_z(dl, dr):
    b = obenGewoelbt(dl)
    m = [(0, 0.5)]
    e = untenSpitz(dr)
    return (0.2, b + m + e)


def glyph_sch(dl, dr):
    b = obenGewoelbt(dl)
    m = [(0, 0.5)]
    e = untenEingelegt(dr)
    return (0.4, shift(b + m + e,0.2))

def kopfSchleife(dl):
    if not dl:
        b = [(0, 0.5), (0.12, 0.55), (0.31, 1)]
    else:
        dx,dy,ea = dl
        if dy == -1:
            b = [ (-0.2, 0.5),(0.0, 0.5),(0.18, 0.5),
                 (0.3, 1),]
        elif dy < 1 or dx > 1:
            b = [ (-0.1, 0.3),(0.1, 0.6),(0.2, 0.75),
                 (0.27, 1),]
        else:
            b = [ (0.16, 0.67),(0.2, 0.78),(0.24, 0.9),
                 (0.21, 1),]
    m = [(0.13,1), (0, 1),
         (0.0, 0.75)]
    return b + m

def glyph_st(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenSpitz(dr)
    return (0.25, b + m + e)

def glyph_l(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenRund(dr)
    return (0.25, b + m + e)

def glyph_ch(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenEingelegt(dr)
    return (0.4, shift(b + m + e,0.2))

def glyph_c(dl, dr):
    b = [(-0.4, 0.5)] if dl else []
    m = [(0, 0.5), (-0.3, 0.45),
         (-0.3, 0), (0, 0)]
    e = [(0.3, 0)] if dr else [(0.1, 0), (0.2, 0.05), (0.2, 0.05)]
    return (0.2, shift(b + m + e,0.2))

def glyph_s(dl, dr):
    b = [(-0.3, 0.5)] if dl else [(-0.2, 0.45), (-0.2, 0.45), (-0.1, 0.5)]
    m = [(0, 0.5), (0.3, 0.5),
         (0.3, 0.0), (0, 0)]
    e = [(-0.4, 0.0)] if dr else []
    return (0.3, shift(b + m + e,0.1))

def glyph_sp0(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenSpitz(dr)
    return (0.5, shift(scale(b + m + e,1,1,0.8),-0.4))

def glyph_sp(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenSpitz2(dr)
    return (0.4, shift(b + m + e,0))

def untenSpitz2(dr):
    m = [(0.0, 0.3),
         (0.4, 0), (0.4, 0)]
    e = [(0.4, 0)] if dr else []
    return m + e

glyphs = {
    'b': glyph_b,
    'd': glyph_d,
    'f': glyph_f,
    'g': glyph_g,
    'h': glyph_h,
    'j': glyph_j,
    'k': glyph_k,
    'l': glyph_l,
    'm': glyph_m,
    'n': glyph_n,
    'p': glyph_p,
    'r': glyph_r,
    's': glyph_s,
    't': glyph_t,
    'w': glyph_w,
    'z': glyph_z,
    'sch': glyph_sch,
    'ch': glyph_ch,
    'nd': glyph_nd,
    'ng': glyph_ng,
    'cht': glyph_cht,
    'st': glyph_st,
    'sp': glyph_sp,
    'pf': glyph_pf,
    'nt': glyph_nd,
    'nk': glyph_ng,
    'th': glyph_th,
    'tsch': glyph_tsch,
    'zw': glyph_zw,
    'schw': glyph_schw,
    'q': glyph_qu,
    'c': glyph_c,
    '_': lambda dx, dy: (0, [(0, 0), (0, 0)]),
    '-': lambda dx, dy: (0, [(0, 0.5), (0, 0.5)]),
}



def stiefoWortZuKurve(w):
    sc = 1.5
    ll = [None] + SplitStiefoWord(w) + [None]
    x = 0
    y = 0
    c = []
    xpos = [(0,0)]
    for i in range(0, len(ll) - 2, 2):
        dl = ll[i]
        k = ll[i + 1]
        dr = ll[i + 2]
        if not k in glyphs:
            print("error, unknown glyph: ["+k+"]", w)
        glFunc = glyphs[k]
        w, g = glFunc(dl, dr)
        w *= sc
        g = scale(g,sc,1)
        if dl:
            dx, dy, ea = dl
            x += ea
            y += dy * 0.5
            xpos.append((x,y))
        gs = shiftToPos(g, x, y)
        x += w
        xpos.append((x,y))
        for t in gs: c.append(t)
    return [(x,c,xpos)]



# -----------------------------------------------

if __name__ == '__main__':

    print(doctest.testmod())


