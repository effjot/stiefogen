#!/usr/bin/env python
# -*- coding: utf-8 -*-

import doctest
import math


#### Einstellungen zum Schriftstil

slant = math.sin(15 * math.pi/180)  # Schrägstellung (s.a. render.py)

## Effektive Abstände (horizontale) für Vokaltypen
di = 0.2  # i, ü
di_extra = 0.5  # etwas weitere Verbindung für bestimmte Konsonanten
de = 1.2  # e, ä, a, ö
du = 2.8  # u, au, o, ei, ai, eu, äu, oi
dkv = 0.6  # direkte Konsonantenverbindung ohne Vokal

vokalAbstaende = {
    #    (dx, dy, eff. Abst)
    'a'      : (1,  1, de),
    'schaft' : (0.6,  1, de*0.6),
    'sam'    : (1,  1, de*1.2),
    'e'      : (1,  0, de),
    'i'      : (1, -1, di),
    'I': (1, -1, di + di_extra),
    'ischmal': (1, -2, di),
    'o'      : (2, -1, du),
    'vor'    : (2, -1, du),
    'u'      : (2,  0, du),
    'ein'    : (2,  0, du),
    'ö'      : (1,  2, de + 0.3),   # deprecated, siehe 'oe'
    'oe'     : (1,  2, de + 0.3),
    'ei'     : (2,  1, du),
    'eu'     : (2,  2, du),
    'oi'     : (2,  2, du),
    'ä'      : (1,  0, de),   # deprecated, siehe 'ae'
    'ae'     : (1,  0, de),
    'ü'      : (1, -1, di),   # deprecated, siehe 'ue'
    'ue'     : (1, -1, di),
    'au'     : (2,  0, du),
    'zu'     : (2,  0, du),
    'ung'    : (2,  0, du),
    'er'     : (1,  0, dkv),
    'ek'     : (1*0.2,  0, dkv*0.2),
    'e2'     : (1,  0, 1),    # Alle W-lich Verbindungen
    'be'     : (1,  2, de*1.2),   # Nur in Verbindung mit ,,,, "un-gleich"=",,,,un be g l ei ch"
    'auf'    : (2,  2, du),   # Nur in Verbindung mit ,,,,
    'aufa'   : (2,  3, du),   # Nur in Verbindung mit ,,,,
}


# Aufbauschriften: Wort in Y verschieben
# Muss am Wortanfang stehen! Z.B: ". u sch l a  g" => "Vorschlag"
# Leerzeichen nach , . : ist optional
# Spaeter koennte "vor" zu ".zu" geparst werden
# Fuer "-fach", "-bar" muessen wir uns noch was anderes ueberlegen...
wordOffsets = {
    ','      : -0.5,
    ';'      :  0.5,
    '.'      :  1, 
    ':'      :  2, 
    ' '      :  0,
}


#### Stift-Pfade für Glyphen (Konsonanten)

"""Worte werden als kubischen Bezier-Splines gezeichnet.
Zwischen zwei Stützpunkten (durch die die Linie geht) gibt es zwei Kontrollpunkten,
die die Richtung angeben, in der die Linien den ersten Stützpunkt verlässt bzw.
in den zweiten Stützpunkt hineingeht.
Pfade werden hier als Liste von (x, y)-Tupeln gespeichert, die die Stütz- und
Kontrollpunkte angeben. Beispiel für 3 Kurvensegmente P, Q, R:
(P0)----[P1]----[P2]----(P3/Q0)----[Q1]----[Q2]----(Q3/R0)----[R1]----[R2]----(R3)
  () = Stützpunkte (Start- und Endpunkte)
  [] = Kontrollpunkte

Glyphen (Konsonanten) und Vokale sind die Bauelemente eines Wortes.

Glyphen sind eine Liste von Punkten, beginnend mit dem 2. Kontrollpunkt
(Kontrollpunkt vor dem Stützpunkt, im Bsp. P2) bis zu einem 1. Kontrollpunkt
(Kontrollpunkt nach einem Stützpunkt, im Bsp. R1)

Vokale werden nicht als Glyphen definiert, sondern die Stützpunkte der
entsprechenden Verbindungslinie werden direkt erzeugt.

Für jede Glyphe gibt es eine Funktion, die den Pfad (Kontroll- und Stützpunkte)
liefert.  Dazu erwartet sie Angaben zum vorhergehenden und folgenden
Vokal:
 * Wenn dl vorhanden ist, dann ist Kontrollpunkt [P1] festgelegt, ansonsten nur (P0).
 * Wenn dr vorhanden ist, dann werden die Punkte [R2] und (R3) definiert."""


### geometrische Transformationen

def shift(g, dx, dy=0):
    """Punkte im Pfad/Glyph g um dx und dy verschieben"""
    return [(x + dx, y + dy) for (x, y) in g]


def scale(g, sx, sy, s=0):
    """Punkte im Pfad/Glyph g um sx und sy skalieren und
    um s scheren (nach rechts kippen)"""
    return [(x * sx + (1 - y) * s, y * sy) for (x, y) in g]


def shiftToPos(g, dx, dy, s = slant):
    """Punkte im Pfad/Glyph g um dx und dy verschieben, dabei
    Scherung s berücksichtigen"""
    return [(dx + x + y * s, dy + y) for (x, y) in g]


def rotate_ccw(g, r):
    """ Punkte imt Pfad/Glyph g um r (Radians) gegen den Uhrzeigersinn rotieren"""
    return [(x*math.cos(r) - y*math.sin(r), y*math.cos(r) + x*math.sin(r)) for (x, y) in g]


### Teilelemente der Glyphen

def obenSpitz(dl):
    b = [(0, 1)] if dl else []   # [P2]
    m = [(0, 1), (0, 1),         # (P3/Q0), [Q1], [Q2]
         (0.0, 0.5)]             # ... (R0) wird in aufrufender Funktion definiert!
    return b + m


def untenSpitz(dr):
                                 # ... (R0) wurde definiert
    m = [(0.0, 0.5),             # [R1]
         (0, 0), (0, 0)]         # [R2], [R3/S0]
    e = [(0, 0)] if dr else []   # [S1]
    return m + e


def untenSpitz2(dr):
    m = [(0.0, 0.3),
         (0.4, 0), (0.4, 0)]
    e = [(0.4, 0)] if dr else []
    return m + e


def untenSpitz2(dr):
    m = [(0.0, 0.3),
         (0.4, 0), (0.4, 0)]
    e = [(0.4, 0)] if dr else []
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


def kopfSchleife(dl):
    if not dl:
        b = [(0, 0.5), (0.12, 0.55), (0.31, 1)]
    else:
        dx, dy, ea = dl
        if dy == -1:
            b = [(-0.2, 0.5), (0.0, 0.5), (0.18, 0.5),
                 (0.3, 1), ]
        elif dy < 1 or dx > 1:
            b = [(-0.1, 0.3), (0.1, 0.6), (0.2, 0.75),
                 (0.27, 1), ]
        else:
            b = [(0.16, 0.67), (0.2, 0.78), (0.24, 0.9),
                 (0.21, 1), ]
    m = [(0.13, 1), (0, 1),
         (0.0, 0.75)]
    return b + m


# Neue Hilfsfunktionen für Aufbauschriften

def kreis_auf(dl, dr):
    # (Startpunkt ist nicht definiert)
    m  = [(0.25, 0),    (0.5, 0.25),  (0.5, 0.5),   # [Q1], [Q2], (Q3/R0)
          (0.5, 0.75),  (0.25, 1),    (0, 1),       # [R1], [R2], (R3/S0)
          (-0.25, 1),   (-0.5, 0.75), (-0.5, 0.5),  # [S1], [S2], (S3/T0)
          (-0.5, 0.25), (-0.25, 0),   (0, 0)]       # [T1], [T2], (T3/U0)
    return m


def kreis_ab(dl, dr):
    return scale(kreis_auf(dl, dr), 1, -1)


def welle_auf(dl, dr):
    b = []
    m = [(0.25, 0.3), (0.5, 0), (0.75, -0.3)]  # [Q2], (Q3/R0), [R1]
    e = []

    return b + m + e


def welle_ab(dl, dr):
    return scale(welle_auf(dl, dr), 1, -1)


def bogen_auf(dl, dr):
    h = 0.6
    l = 0.3
    b = [(0, 0), (0, 0)]     # Start immer spitz [P2], (P3/Q0)
    m = [(l, h), (1 - l, h)]   # [Q1], [Q2]
    e = [(1, 0), (1, 0)]     # Ende immer spitz (Q3/R0)

    return b + m + e


def bogen_ab(dl, dr):
    return scale(bogen_auf(dl, dr), 1, -1)


### Glyphen (Konsonanten)

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
    return (0.3, shift(b + m + e, 0.3))


def glyph_m(dl, dr):
    b = [(-0.3, 1)] if dl else [(-0.2, 0.9), (-0.2, 0.9), (-0.1, 1)]
    m = [(0, 1), (0.3, 1),
         (0.3, 0.0), (0, 0)]
    e = [(-0.4, 0.0)] if dr else []
    return (0.3, shift(b + m + e, 0.1))


def glyph_p(dl, dr):
    b = [(0, 1)] if dl else []     # [P2]
    m = [(0, 1), (0, 0.1),         # (P3/Q0), [Q1]
         (0.4, 0.9), (0.4, 0)]     # [Q2], (Q3/R0)
    e = [(0.4, 0)] if dr else []   # [R1]
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
    w, g = glyph_b(dl, dr)
    return (0, scale(g, 1, 0.5))


def glyph_g(dl, dr):
    w, g = glyph_b(dl, dr)
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
    return (0.3, shift(b + m + e, 0.3))


def glyph_ng(dl, dr):
    w, g = glyph_nd(dl, dr)
    return (0.8, shift(scale(g, 1, 1, 0.6), -0.1))


def glyph_k(dl, dr, runder = True):
    b = obenRund(dl)
    m = [(0, 0.5)]
    e = untenRund(dr, runder = runder)
    return (0.3, shift(b + m + e, 0.15))


def glyph_cht(dl, dr):
    w, g = glyph_k(dl, dr, runder = False)
    return (0.8, scale(g, 1, 1, 0.5))


def glyph_h(dl, dr):
    b = obenSpitz(dl)
    m = [(0, 0.5)]
    e = untenEingelegt(dr)
    return (0.2, shift(b + m + e, 0.2))


def glyph_z(dl, dr):
    b = obenGewoelbt(dl)
    m = [(0, 0.5)]
    e = untenSpitz(dr)
    return (0.2, b + m + e)


def glyph_sch(dl, dr):
    b = obenGewoelbt(dl)
    m = [(0, 0.5)]
    e = untenEingelegt(dr)
    return (0.4, shift(b + m + e, 0.2))


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
    return (0.4, shift(b + m + e, 0.2))


def glyph_c(dl, dr):  # Vokalzeichen
    b = [(-0.4, 0.5)] if dl else []
    m = [(0, 0.5), (-0.3, 0.45),
         (-0.3, 0), (0, 0)]
    e = [(0.3, 0)] if dr else [(0.1, 0), (0.2, 0.05), (0.2, 0.05)]
    return (0.2, shift(b + m + e, 0.2))


def glyph_s(dl, dr):
    b = [(-0.3, 0.5)] if dl else [(-0.2, 0.45), (-0.2, 0.45), (-0.1, 0.5)]
    m = [(0, 0.5), (0.3, 0.5),
         (0.3, 0.0), (0, 0)]
    e = [(-0.4, 0.0)] if dr else []
    return (0.3, shift(b + m + e, 0.1))


def glyph_sp0(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenSpitz(dr)
    return (0.5, shift(scale(b + m + e, 1, 1, 0.8), -0.4))


def glyph_sp(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenSpitz2(dr)
    return (0.4, shift(b + m + e, 0))


def glyph_zw(dl, dr):
    w, g = glyph_z(dl, dr)
    return (0.2, scale(g, 1, 0.5))


def glyph_schw(dl, dr):
    w, g = glyph_sch(dl, dr)
    return (0.4, scale(g, 1, 0.5))


def glyph_qu(dl, dr):
    w, g = glyph_f(dl, dr)
    return (0.2, scale(g, 1, 0.5))


def glyph_th(dl, dr):
    w, g = glyph_h(dl, dr)
    return (0.2, scale(g, 1, 0.5))


def glyph_tsch(dl, dr):
    w, g = glyph_nd(dl, dr)
    return (0.3, scale(g, 1, 0.5))


# Neue Glyphen
def glyph_selbst(dl, dr):
    assert not dl, "Glyph 'selbst' darf nur am Wortanfang stehen!"
    b = [(0, 0)]  # (P0)
    m = kreis_auf(dl, dr)
    e = [(0.75, 0), (1, 0.5), (1, 0.5)] if not dr else [(0.75, 0)]
    return [1, shift( scale(b + m + e, 0.8, 1), 0.4)]


def glyph_gegen(dl, dr):
    # Immer in Kombination mit Wortabsenkung verwenden!
    assert not dl, "Glyphen 'gegen/will/all usw.' duerfen nur am Wortanfang stehen!"
    b = [(0, 0)] # (P0)
    m = kreis_auf(dl, dr)
    e = [(0.75, 0), (1, 0.5), (1, 0.5)] if not dr else [(0.75, 0)]
    return [0.5, shift(scale(b + m + e, 0.4, 0.5), 0.2, 0)]


def glyph_ca(dl, dr):
    b = [(0, -0.1)]*2 if not dl else []
    m = welle_auf(dl, dr)
    e = [(1, 0)]*2 if not dr else []
    return [0.7, shift(scale(b + m + e, 0.7, 1), 0, 0.1)]


def glyph_uns(dl, dr):
    b = [(0, 0)]*2 if not dl else []
    m = bogen_auf(dl, dr)
    e = [(1, 0)]*2 if not dr else []
    return [2, scale(b + m + e, 2, 1)]


def glyph_doch(dl, dr):
    w,m = glyph_uns(dl, dr)
    return [w, scale(m,1,-1)]


def glyph_den(dl, dr):
    b = [(0, 0)]*2 if not dl else []
    m = bogen_auf(dl, dr)
    e = [(1, 0)]*2 if not dr else []
    return [0.4, scale(b + m + e, 0.4, 0.5)]


def glyph_ent(dl, dr):
    assert not dl, "Glyph 'ent' darf nur am Wortanfang stehen"
    b = obenRund(True)
    m = [(0, 0.5)]
    e = untenSpitz(dr)

    return (0.41, scale([(0, 0)]*2 + shift( b + m + e, 0.8), 0.5, 0.5))


def glyph_ander(dl, dr):
    assert not dl, "Glyph 'ander' darf nur am Wortanfang stehen!"
    b = [(0, 0)]
    m = shift( scale( kreis_auf(dl, dr), 0.15, 0.2 ), 0.5, 0 ) 
    e = [(0.5, 0)]*3 if not dr else [(0.55, 0)]

    return [0.5, (b + m + e)]


def glyph_ver(dl, dr):
    #assert not dl, "Glyph 'ver' darf nur am Wortanfang stehen!"
    b = [(0, 0)] if not dl else [(0, 0), (0, 0)]
    m = scale(kreis_auf(dl, dr), 0.15, 0.2)
    e = [(0.3, -0.1), (0.4, 0.2), (0.4, 0.2)] if not dr else [(0.5, -0.1)]

    return [0.3, (b + m + e)]


def glyph_dir(dl, dr):
    w,m = glyph_ver(dr, dl)  # dl und dr vertauscht!
    m = reversed(scale( m, -1, 1 ) )

    return w, m

def glyph_lich(dl, dr):
    _, m = glyph_ver(None, None)
    m = shift(reversed(rotate_ccw(m, math.pi) ), 0, 0.2)
    if dl:
        m = m[2:]
    if dr:
        m = m[:-2]

    return [0.4, m]


def glyph_los(dl, dr):
    l = 1.5
    b = [(0, 0)]*2 if not dl else []
    m = [(l, 0)]*2 + shift(scale(kreis_ab(dl, dr), 0.2, 0.2), l)
    e = [(l, 0)] if dr else []
    return [l, (b + m + e)]


def glyph_sonder(dl, dr):
    l = 1.8
    m = scale(kreis_auf(dl, dr), 0.4, 0.4)
    b = [(0, 0)] if not dl else [m[0]]*2 
    e = [(0, 0), (l, 0), (l, 0)] if not dr else [(l, 0)]
    return [l, (b + m + e)]



def glyph_un(dl, dr):
    w,m = glyph_d(dl, dr)

    return [0.5*w, scale(m, 0.7, 0.5)]


def glyph_voll(dl, dr):

    return [1.3, (b + m + e)]


def glyph_jetzt(dl, dr):
    w, g = glyph_b(dl, dr)
    return (0.5, scale(g, 1, 1, 0.5))


def glyph_der(dl, dr):
    assert not dl and not dr
    b = [(0, 0)]
    m = scale( kreis_auf(dl, dr), 0.1, 0.1 )
    e = []

    return (0.1, shift(b + m + e, 0, 0.1) )


def glyph_es1(dl, dr, l):
    b = [] if dl else [(0, 0)]*2
    m = [(0,0), (l, 0), (l, 0)]
    e = [] if dr else [(l,0)]*2

    return (l, (b + m + e) )


def glyph_werend(dl, dr):
    assert not dl and not dr, "Glyph darf nur allein stehen"
    m = [(0.6, 2), 
         (0.6, 1.5), (0, 1.5), (0, 0.45), 
         (0, -0.14), (0.6, -0.1), (0.6, 0.24), 
         (0.6, 0.5),(0.1, 0.17), (0.1, 0.17)]

    return (0.5, scale( m, 1, 1) )


def glyph_werts(dl, dr):
    assert not dl and not dr, "Glyph darf nur allein stehen"
    m = [(0.6, 2), 
         (-0.2, 1), (-0.2, 1), (0.6, 0)]

    return (0.5, scale( m, 0.6, 1) )


def glyph_es(dl, dr):
    l = 0.6
    w, m = glyph_es1(dl, dr, l)

    return (w*l, scale(m, l, 1))


def glyph_so(dl, dr):
    l = 1.3
    w, m = glyph_es1(dl, dr, l)

    return (w*l, scale(m, l, 1))


def glyph_viel(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_f(dl, dr)

    return (w*sx, scale(m, sx, sy))


def glyph_klein(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_k(dl, dr)

    return (w*sx, scale(m, sx, sy))


def glyph_gleich(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_ch(dl, dr)

    return (w*sx, scale(m, sx, sy))


def glyph_letzt(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_l(dl, dr)

    return (w*sx, scale(m, sx, sy))


def glyph_bund(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_b(dl, dr)

    return (w*sx, scale(m, sx, sy))


def glyph_wesen(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_w(dl, dr)

    return (w*sx, scale(m, sx, sy))


def glyph_zer(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_z(dl, dr)

    return (w*sx, scale(m, sx, sy))


def glyph_jed(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_j(dl, dr)

    return (w*sx, scale(m, sx, sy))


def glyph_nur(dl, dr):
    sx = 3
    sy = 1
    w, m = glyph_ca(dl, dr)

    return (w*sx, scale(m, sx, sy))


def glyph_chen(dl, dr):
    sx = 1
    sy = 0.5
    w,m = glyph_ch(dl,dr)
    m = scale(m, sx, sy)
    m = shift( m, -0.2, -0.25)

    return (w*sx, m)


def glyph_x(dl, dr):
    w,m = glyph_k(dl, dr)

    return (w * 0.5, scale(m, 0.5, 0.5))


def glyph_muss(dl, dr):
    b = [(-0.2, 0.7), (0.3, 0.9)] if not dl else []
    m = [(0.8, 1), (1.1, 1), (1.7, 1), 
         (1.4, 0.0), (1.1, 0)]
    e = [(0.8, 0.0)] if dr else []

    return (1.5, (b + m + e))


def glyph_um(dl, dr):
    b = [(-0.5, 1)] if dl else []
    m = [(0, 1.6), (0.35, 2.1), (1.85, 2.4), 
         (0.65, 0.25), (0.65, 0.25), (0.5, 0), (0.3, 0)]
    e = [(0, 0)] if dr else []

    return (1.2, (b + m + e))



glyphs = {
    'b':        glyph_b, 
    'd':        glyph_d, 
    'f':        glyph_f, 
    'g':        glyph_g, 
    'h':        glyph_h, 
    'j':        glyph_j, 
    'k':        glyph_k, 
    'l':        glyph_l, 
    'm':        glyph_m, 
    'n':        glyph_n, 
    'p':        glyph_p, 
    'r':        glyph_r, 
    's':        glyph_s, 
    't':        glyph_t, 
    'w':        glyph_w, 
    'x':        glyph_x,
    'z':        glyph_z, 
    'sch':      glyph_sch, 
    'ch':       glyph_ch, 
    'nd':       glyph_nd, 
    'ng':       glyph_ng, 
    'cht':      glyph_cht, 
    'st':       glyph_st, 
    'sp':       glyph_sp, 
    'pf':       glyph_pf, 
    'nt':       glyph_nd, 
    'nk':       glyph_ng, 
    'th':       glyph_th, 
    'tsch':     glyph_tsch, 
    'zw':       glyph_zw, 
    'schw':     glyph_schw, 
    'q':        glyph_qu, 
    'c':        glyph_c, 
    # mit: ",,ek"
    # er:  "ek"
    # an:  ".ek"
    # vor: ",u"
    # zu:  "u"
    # ein: ".u"
    # auf: ",,,,ei"
    # be-: ",,,,be"
    'ab':       glyph_b,       # ".ab"
    'aber':     glyph_b,       # ".aber ek"
    'all':      glyph_gegen,   # ".all"
    'als':      glyph_es,      # ":,als"
    'ander':    glyph_ander,   # ".ander"
    'auch':     glyph_ander,   # ";auch"
    'aus':      glyph_so,      # ";aus"
    'bei':      glyph_so,      # ":,bei"
    'bin':      glyph_b,       # ",,bin"
    'bund':     glyph_bund,    # "bund"
    'ca':       glyph_ca,      # ";ca"
    'chen':     glyph_chen,    # ",chen"
    'da':       glyph_d,       # ".da"
    'der':      glyph_der,     # "der"
    'die':      glyph_der,     # ",die"
    'das':      glyph_der,     # ":,das"
    'dir':      glyph_dir,     # ",dir"
    'den':      glyph_den,     # "den"
    'deutsch':  glyph_doch,    # ":.deutsch"
    'doch':     glyph_doch,    # "doch"
    'durch':    glyph_doch,    # ".durch"
    'es':       glyph_es,      # ";es"
    'ent':      glyph_ent,     # "ent"
    'euer':     glyph_ca,      # ":euer"
    'euro':     glyph_nur,     # ":euro"
    'fast':     glyph_f,       # ".fast"
    'fest':     glyph_f,       # "fest"
    'fort':     glyph_t,       # ",fort"
    'fuer':     glyph_ver,     # ",fuer"
    'galt':     glyph_l,       # ".galt"
    'ganz':     glyph_g,       # ".ganz"
    'ge':       glyph_es,      # "ge"
    'gegen':    glyph_gegen,   # "gegen"
    'gelt':     glyph_l,       # "gelt"
    'gilt':     glyph_l,       # ",,gilt"
    'gleich':   glyph_gleich,  # "gleich"
    'gut':      glyph_g,       # "gut"
    'ich':      glyph_ander,   # ",ich"
    'ig':       glyph_es,      # "ig"
    'ist':      glyph_t,       # ",ist"
    'immer':    glyph_ca,      # ",immer"
    'ion':      glyph_so,      # "ion"
    'jed':      glyph_jed,     # "jed"
    'jetzt':    glyph_jetzt,   # "jetzt"
    'kein':     glyph_uns,     # ".uns"
    'klein':    glyph_klein,   # "klein"
    'kon':      glyph_k,       # ",,kon"
    'letzt':    glyph_letzt,   # "letzt"
    'lich':     glyph_lich,    # "lich"  ( auch fuer 'endlich', oder :lich fuer 'moeglich', ",,w e lich" fuer 'wirklich')
    'los':      glyph_los,     # "los"
    'man':      glyph_den,     # ":,man"
    'mein':     glyph_m,       # ".mein"
    'muss':     glyph_muss,    # "muss"
    'nach':     glyph_ver,     # ":,nach"
    'nicht':    glyph_den,     # ",nicht"
    'noch':     glyph_uns,     # ",,uns"
    'nur':      glyph_nur,     # "nur"
    'ober':     glyph_bund,    # ",,bund"
    'rueck':    glyph_klein,   # ",,rueck"
    'so':       glyph_so,      # ",so"
    'sie':      glyph_es,      # ",es"
    'sind':     glyph_nd,      # ",,sind"
    'selbst':   glyph_selbst,  # "selbst"
    'sonder':   glyph_sonder,  # "sonder"
    'sonst':    glyph_selbst,  # ",,sonst"
    'soll':     glyph_gegen,   # ",,soll u"
    'stat':     glyph_selbst,  # ".statt"
    'trotz':    glyph_zer,     # ",,trotz"
    'ueber':    glyph_b,       # ",,ueber ek"
    'uns':      glyph_uns,     # "uns"
    'um':       glyph_um,      # "um"
    'un':       glyph_un,      # ",,,,un"
    'und':      glyph_nd,      # "und"
    'unter':    glyph_nd,      # ",,unter ek"
    'ver':      glyph_ver,     # "ver"
    'viel':     glyph_viel,    # ",,viel"
    'voll':     glyph_voll,    # "voll"
    'welch':    glyph_ch,      # "welch"
    'euch':     glyph_ch,      # "euch"
    'werend':   glyph_werend,  # "werend"
    'wesen':    glyph_wesen,   # "wesen"
    'werts':    glyph_werts,   # "werts"
    'wieder':   glyph_wesen,   # ",,wieder"
    'will':     glyph_gegen,   # ",,will"
    'woll':     glyph_gegen,   # ",,woll"
    'zer':      glyph_zer,     # "zer"
    'zwar':     glyph_ca,      # ":,zwar"
    '_':        lambda dx, dy: (0, [(0, 0), (0, 0)]),
    '-':        lambda dx, dy: (0, [(0, 0.5), (0, 0.5)])
}


def isword(word):
    return word[0].isalpha() or word[0] in wordOffsets


def SplitStiefoWord(st):
    """Zerlege das Wort st in Vokale und Konsonanten.
    Vokale werden als (dx, dy, ea) ausgegeben, wobei
    dy die Werte -1, 0, +1, +2 haben kann für i, e, a, ö Stufen.
    dx hat die Werte 0, 1, 2 für Konsonantenverbindung, e, u.
    ea ist der effektive Abstand horizontal, der für diesen Vokal verwendet wird.
    '_' und '-' werden am Anfang und Ende angefügt, wenn das
    Wort mit einem Vokal anfängt oder aufhört.
    >>> SplitStiefoWord("b e r n")
    ['b', (1, 0, 1.2), 'r', (0, 0, 0.6), 'n']
    >>> SplitStiefoWord("e r d e")
    ['_', (1, 0, 1.2), 'r', (0, 0, 0.6), 'd', (1, 0, 1.2), '-']
    >>> SplitStiefoWord("n a t i o n")
    ['n', (1, 1, 1.2), 't', (1, -1, 0.2), 'c', (2, -1, 3), 'n']
    """
    wrdOffsY = 0  # Wortoffset in Y
    # Wort-Offset nur in Kombination mit weiteren Zeichen erlaubt
    while len(st) > 1 and st[0] in wordOffsets:
        wrdOffsY += wordOffsets[st[0]]
        st = st[1:]

    w = []  # Liste der Buchstaben im Wort
    first = True
    pz = False  # vorhergehendes Zeichen
    pv = False  # vorhergehender Vokal
    for z in (st.split(' ')):
        v = z in vokalAbstaende
        if first and z in ('i', 'ü'):
            z = 'I'
        if pv and v:
            w.append('c')
        if pz in ('i', 'ü') and z in ('b', 'f', 'k', 'm', 'p', 'r', 'z',
                                      'cht', 'ng', 'nk', 'st'):
            w[-1] = 'I'
        if pz in ('i', 'ü') and z in ('ch'):  # evtl. 'sp'
            w[-1] = 'ischmal'  # (war ii in effjot/master)
        w.append(z)
        pz = z
        pv = v
        first = False
    if w[-1] in ('i', 'ü'):
        w[-1] = 'I'
    x = []  # Liste für zerlegtes Wort mit Konsonanten und Vokal-Tupeln
    k = False
    for l in w:
        if l in vokalAbstaende:
            if not x:
                x.append('_')
            # Vokale durch Abstands-Tupel ersetzen
            x.append(vokalAbstaende[l])
            k = False
        else:
            # Bei 2 Konsonanten besonderen Abstands-Tupel anfuegen
            if k:
                x.append((0, 0, dkv))
            x.append(l)
            k = True
    if not k:
        x.append('-')
    return (x, wrdOffsY)


def stiefoWortZuKurve(w):
    """Erzeuge Kurve aus Wort.  Liefert Tupel (x, c, xpos) mit den zum
    Zeichnen notwendigen Informationen: x = Breite des Worts,
    c = Liste der Bezier-Punkte, xpos = Endpositionen der einzelnen
    Buchstaben"""

    sc = 1.5  # Skalierung in x-Richtung für Glyphen und Zwischenräume
    conv_y_step  = 0.5  # Umrechnung vertikaler Versatz (dy der Vokale zählt halbe, ganze Stufe als 1, 2)
    x = 0  # aktuelle Stiftposition
    y = 0  # aktuelle Stiftposition
    c = []  # Bezier-Punkte des Worts
    xpos = [(0, 0)]  # Stift-Endpositionen hinter Vokalen und Konsonanten

    ll, wrdOffsY   = SplitStiefoWord(w)
    ll = [None] + ll + [None]

    for i in range(0, len(ll) - 2, 2):
        dl = ll[i]      # Vokal vor dem aktuellen Konsonant
        k = ll[i + 1]   # aktueller Konsonant (Glyph)
        dr = ll[i + 2]  # Vokal nach Konsonant
        if not k in glyphs:
            print("error, unknown glyph: [" + k + "]", w)
        glFunc = glyphs[k]
        w, g = glFunc(dl, dr)  # w = x-Abstand hinter Glyph, g = Bezier-Punkte des Glyphen
        w *= sc  # in x-Richtung skalieren
        g = scale(g, sc, 1)  # in x-Richtung skalieren
        if dl:
            dx, dy, ea = dl  # Vokalabstände (siehe SplitStiefoWord)
            x += ea  # Delta x des Stifts wird von eff. Abst. des linken Vokals bestimmt
            y += dy * conv_y_step  # Delta y des Stifts vom Delta y des linken Vokals * 0.5
                           # (weil dy Vokal halbe, ganze Stufe als 1, 2 zählt)
            xpos.append((x, y))
        gs = shiftToPos(g, x, y + wrdOffsY * conv_y_step, slant)  # Bezier-Punkte an die Stiftposition verschieben
        x += w  # Stift hinter Glyph setzen
        xpos.append((x, y))
        for t in gs:
            c.append(t)
    return [(x, c, xpos)]


if __name__ == '__main__':
    print(doctest.testmod())
