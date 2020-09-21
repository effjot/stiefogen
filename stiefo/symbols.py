#!/usr/bin/env python
# -*- coding: utf-8 -*-

import doctest
import math
import re


#### Einstellungen zum Schriftstil

## Schrägstellung (s.a. render.py)
slant = math.sin(15 * math.pi/180)

## Effektive Abstände (horizontale) für Vokaltypen
de = 1.2  # e, ä, a, ö
di = 0.2  # i, ü
di_extra = 0.5  # etwas weitere Verbindung für bestimmte Konsonanten
du = 2.8  # u, au, o, ei, ai, eu, äu, oi
dkv = 0.6  # direkte Konsonantenverbindung ohne Vokal


vokalAbstaende = {
    #    (dx, dy, eff. Abst)
    'a'      : (1,  1, de), 
    'schaft' : (0.6, 1, de*0.6), 
#    'sam'    : (1,  1, de*1.2), 
    'e'      : (1,  0, de), 
    'i'      : (1, -1, di),
    'I': (1, -1, di + di_extra),
    'ischmal': (1, -2, di),  # war 'ii' in effjot/master
    'o'      : (2, -1, du), 
#    'vor'    : (2, -1, du), 
    'u'      : (2,  0, du), 
#    'ein'    : (2,  0, du), 
    'ö'      : (1,  2, de + 0.3),
    'oe'     : (1,  2, de + 0.3),
    'ei'     : (2,  1, du),
    'eu'     : (2,  2, du),
    'oi'     : (2,  2, du),
    'ä'      : (1,  0, de),
    'ae'     : (1,  0, de),
    'ü'      : (1, -1, di),
    'ue'     : (1, -1, di),
    'au'     : (2,  0, du),
#    'zu'     : (2,  0, du),
    'ung'    : (2,  0, du), 
#    'er'     : (1,  0, dkv),
    'ek'     : (1*0.2,  0, dkv*0.2),
    'e2'     : (1,  0, 1),    # Alle W-lich Verbindungen
#    'be'     : (1,  2, de*1.2),   # Nur in Verbindung mit ,,,, "un-gleich"=",,,,un be g l ei ch"
#    'auf'    : (2,  2, du),   # Nur in Verbindung mit ,,,,
#    'aufa'   : (2,  3, du),   # Nur in Verbindung mit ,,,,
}


kuerzel = {
    'in': 'i n',  # Wort „in“ wird normal geschrieben, waagr. Strich nur für Vorsilbe
    'sie': '-2-', 'es': '+2-', 'als': '-4-',  # „als“ etwas tiefer, sie Aufbau2, S. 17
    'pro': '2--', 'aus': '++2--', 'so': '--2--', 'bei': '4--',
    'der': '+2.', 'die': '--2.', 'das': '++3.'
}


vorsilben = {
    'mit': '1_', 'er': '2_', 'an': '3_',
    'vor': '1__', 'zu': '2__', 'ein': '3__',
    'in': '1-', 'inter': '1-', 'ge': '2-', 'trans': '3-',
    'pro': '1--', 'aus': '2--', 'bei': '3--',
    'be': '0//', 'auf': '0//',
}


praefix_formen = {
    # (Typ, vert. Pos. in Halbstufen, Vokal-Tupel (DX, DY, eff. Abst))
    # Typ: _ normaler Anstrich, - waager. Anstrich, / Aufstrich
    '1_': ("_", 1, (1, 0, di_extra)),
    '2_': ("_", 2, (1, 0, dkv)),  # Vergleich mit Stiefo-Materialien sieht kürzer aus als E
    '3_': ("_", 3, (1, 0, di_extra)),
    '1__': ("_", 1, (2, 0, du)),
    '2__': ("_", 2, (2, 0, du)),  # identisch zu U
    '3__': ("_", 3, (2, 0, du)),
    '0-': ('-', 0, (1, 0, 0)),
    '1-': ("-", 1, (1, 0, -0.75 * de)),
    '2-': ("-", 2, (1, 0, -0.75 * de)),
    '3-': ("-", 3, (1, 0, -(di + di_extra))),
    '4-': ("-", 4, (1, 0, -(di + di_extra))),
    '1--': ("-", 1, (2, 0, -du)),
    '2--': ("-", 2, (2, 0, -du)),
    '3--': ("-", 3, (2, 0, -du)),
    '4--': ("-", 4, (2, 0, -du)),
    '0/': ("/", 0, (1, 2, de)),
    '0//': ("/", 0, (2, 2, du))
}


""" 2 Koordinatensysteme für Höhe:
  * zum Zeichnen (Bezier): 1 Einheit = 1 Stufe
  * für Vokaldefinition und Versatzzeichen im Stiefo-Code: 1 Einheit = 1/2 Stufe"""
conv_y_step = 0.5  # Umrechnung vertikale Position (Versatz Vorsilben und Kürzel)
y_baseline = 2     # y-Pos. der Grundlinie in Versatz-Zählung

y_smallstep = 0.25  # ein wenig über/unter Grundlinie setzen (aus, so, es, sie)


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
    return [(dx + x + y * s + dy * s, dy + y) for (x, y) in g]


def rotate_ccw(g, r):
    """ Punkte imt Pfad/Glyph g um r (Radians) gegen den Uhrzeigersinn rotieren"""
    return [(x*math.cos(r) - y*math.sin(r), y*math.cos(r) + x*math.sin(r)) for (x, y) in g]


### Teilelemente der Glyphen
### bei obenSpitz und untenSpitz erläutern Kommentare das Prinzip der Bezier-Punkte

def ist_vokal_waagr_strich(dl):
    """Waagerechter Strich anhand Vokaltupel erkennen"""
    dx, dy, ea = dl
    return (dy == 0 and ea <= 0)


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
    if not dl:
        b = []
    else:
        if ist_vokal_waagr_strich(dl):
            b = [(0, 1)]
        else:
            b = [(-0.3, 0.95)]
    m = [(0.2, 1), (0, 1),
         (0.0, 0.75)]
    return b + m


def kopfSchleife(dl):
    if not dl:
        b = [(0, 0.5), (0.12, 0.55), (0.31, 1)]
    else:
        dx, dy, ea = dl
        #print("kopfSchleife dx, dy, ea", dx, dy, ea)
        if dy == -1 or ist_vokal_waagr_strich(dl):  # i-Position oder waagr. Anstrich
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


def kreis_auf(dl, dr):
    # (Startpunkt ist nicht definiert)
    m = [(0.25, 0),    (0.5, 0.25),  (0.5, 0.5),   # [Q1], [Q2], (Q3/R0)
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
    b = [(0, 0), (0, 0)]      # Start immer spitz [P2], (P3/Q0)
    m = [(l, h), (1 - l, h)]  # [Q1], [Q2]
    e = [(1, 0), (1, 0)]      # Ende immer spitz (Q3/R0)
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
    #print("glyph_n: dl=", dl)
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
    if not dl:
        b = []
    else:
        if ist_vokal_waagr_strich(dl):
            b = [(0, 1)]
        else:
            b = [(-0.4, 0.9)]
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
    #print("glyph_l: dl=",dl)
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenRund(dr)
    return (0.25, b + m + e)


def glyph_ch(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenEingelegt(dr)
    return (0.4, shift(b + m + e, 0.2))


def glyph_c(dl, dr):
    """Vokalzeichen"""
    if not dl:
        b = []
    else:
        if ist_vokal_waagr_strich(dl):
            b = [(0, 0.5)]
        else:
            b = [(-0.4, 0.5)]
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


def glyph_selbst(dl, dr):
    assert not dl, "Glyph 'selbst' darf nur am Wortanfang stehen!"
    b = [(0, 0)]  # (P0)
    m = kreis_auf(dl, dr)
    e = [(0.75, 0), (1, 0.5), (1, 0.5)] if not dr else [(0.75, 0)]
    return [1, shift(scale(b + m + e, 0.8, 1), 0.4)]


def glyph_gegen(dl, dr):
    # Immer in Kombination mit Wortabsenkung verwenden!
    assert not dl, "Glyphen 'gegen/will/all usw.' duerfen nur am Wortanfang stehen!"
    # FIXME: "dagegen" ermöglichen
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
    w, m = glyph_uns(dl, dr)
    return [w, scale(m, 1, -1)]


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
    return (0.41, scale([(0, 0)]*2 + shift(b + m + e, 0.8), 0.5, 0.5))


def glyph_ander(dl, dr):
    assert not dl, "Glyph 'ander' darf nur am Wortanfang stehen!"
    # FIXME: "einander" ermöglichen
    b = [(0, 0)]
    m = shift(scale(kreis_auf(dl, dr), 0.15, 0.2), 0.5, 0)
    e = [(0.5, 0)]*3 if not dr else [(0.55, 0)]
    return [0.5, (b + m + e)]


def glyph_ver(dl, dr):
    #assert not dl, "Glyph 'ver' darf nur am Wortanfang stehen!"
    b = [(0, 0)] if not dl else [(0, 0), (0, 0)]
    m = scale(kreis_auf(dl, dr), 0.15, 0.2)
    e = [(0.3, -0.1), (0.4, 0.2), (0.4, 0.2)] if not dr else [(0.5, -0.1)]
    return [0.3, (b + m + e)]


def glyph_dir(dl, dr):
    w, m = glyph_ver(dr, dl)  # dl und dr vertauscht!
    m = reversed(scale(m, -1, 1))
    return w, m


def glyph_lich(dl, dr):
    _, m = glyph_ver(None, None)
    m = shift(reversed(rotate_ccw(m, math.pi)), 0, 0.2)
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
    w, m = glyph_d(dl, dr)
    return [0.5*w, scale(m, 0.7, 0.5)]


def glyph_voll(dl, dr):
    # TODO
    return [1.3, (b + m + e)]


def glyph_jetzt(dl, dr):
    w, g = glyph_b(dl, dr)
    return (0.5, scale(g, 1, 1, 0.5))


def glyph_der(dl, dr):
    assert not dl and not dr
    b = [(0, 0)]
    m = scale(kreis_auf(dl, dr), 0.1, 0.1)
    e = []
    return (0.1, shift(b + m + e, 0, 0.1))


def glyph_punkt(dl, dr):
    assert not dl and not dr, "Punkt muss alleine stehen"
    b = [(0, 0)]
    m = scale(kreis_auf(dl, dr), 0.1, 0.1)
    e = []
    return (0.1, b + m + e)


def glyph_es1(dl, dr, l):
    b = [] if dl else [(0, 0)]*2
    m = [(0,0), (l, 0), (l, 0)]
    e = [] if dr else [(l,0)]*2
    return (l, (b + m + e))


def glyph_werend(dl, dr):
    assert not dl and not dr, "Glyph darf nur allein stehen"
    m = [(0.6, 2),
         (0.6, 1.5), (0, 1.5), (0, 0.45),
         (0, -0.14), (0.6, -0.1), (0.6, 0.24),
         (0.6, 0.5),(0.1, 0.17), (0.1, 0.17)]

    return (0.5, scale(m, 1, 1))


def glyph_werts(dl, dr):
    assert not dl and not dr, "Glyph darf nur allein stehen"
    # FIXME "rückwärts", "vorwärts" ermöglichen
    m = [(0.6, 2),
         (-0.2, 1), (-0.2, 1), (0.6, 0)]
    return (0.5, scale(m, 0.6, 1))


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
    m = shift(m, -0.2, -0.25)
    return (w*sx, m)


def glyph_x(dl, dr):
    w, m = glyph_k(dl, dr)
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


def glyph_waagr_strich(l, naechster_kons):
#    print("waagr_strich l={}, nk={}.".format(l, naechster_kons))
    if not naechster_kons or naechster_kons == '=':
        y0 = 0
        e = []
    else:
        if naechster_kons[0].isdigit():  # Zahl vor Konsonant = vert. Versatz
            # dy = int(naechster_kons[0])  # TODO: Zahl nach Konsonant (Größe)
            naechster_kons = naechster_kons[1:]
        if naechster_kons in ('b', 'f', 'h', 'j', 'k', 'm', 'p', 'w', 'z',
                              'cht', 'nd', 'nt', 'ng', 'pf', 'sch'):
            y0 = 1
        else:
            y0 = 0.5
        e = [(l, y0)]
    b = [(0, y0), (0, y0)]
    m = [(l, y0), (l, y0)]
    return (l, (b + m + e))


### Lookup Konsonanten -> Glyph-Funktionen

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
    'ab':       glyph_b,       # ".ab"
    'aber':     glyph_b,       # ".aber ek"
    'all':      glyph_gegen,   # ".all"
    'ander':    glyph_ander,   # ".ander"
    'auch':     glyph_ander,   # ";auch"
    'bin':      glyph_b,       # ",,bin"
    'bund':     glyph_bund,    # "bund"
    'ca':       glyph_ca,      # ";ca"
    'chen':     glyph_chen,    # ",chen"
    'da':       glyph_d,       # ".da"
    'dir':      glyph_dir,     # ",dir"
    'den':      glyph_den,     # "den"
    'deutsch':  glyph_doch,    # ":.deutsch"
    'doch':     glyph_doch,    # "doch"
    'durch':    glyph_doch,    # ".durch"
    'ent':      glyph_ent,     # "ent"
    'euer':     glyph_ca,      # ":euer"
    'euro':     glyph_nur,     # ":euro"
    'fast':     glyph_f,       # ".fast"
    'fest':     glyph_f,       # "fest"
    'fort':     glyph_t,       # ",fort"
    'fuer':     glyph_ver,     # ",fuer"
    'galt':     glyph_l,       # ".galt"
    'ganz':     glyph_g,       # ".ganz"
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
    '.': glyph_punkt,
    '-': glyph_waagr_strich,
    '_': lambda dx, dy: (0, [(0, 0), (0, 0)]),  # Startpunkt normaler Anstrich
    '=': lambda dx, dy: (0, [(0, 0.5), (0, 0.5)])  # Vokal am Wortende
}


def isword(word):
    if not isinstance(word, str) or word == '':
        return False
    else:
        first = word[0]
        if len(word) == 1:
            return(word.isalpha() or word == '.')
        else:
            second = word[1]
        return(first.isalpha() or first.isdigit() or
               (first in ('+', '-') and (second.isdigit() or second in ('+', '-'))))


def get_y_adjust(s):
    """Hilfsfunktion: Anweisung zur Feinanpassung vert. Versatz extrahieren"""
    assert isinstance(s, str)
    y_adjust = 0

    if re.match(r'([+]*|[-]*)\d', s):
        if s.startswith('++'):
            y_adjust = 2*y_smallstep
            s = s[2:]
        elif s.startswith('+'):
            y_adjust = y_smallstep
            s = s[1:]
        elif s.startswith('--'):
            y_adjust = -2*y_smallstep
            s = s[2:]
        elif s.startswith('-'):
            y_adjust = -y_smallstep
            s = s[1:]
    return(s, y_adjust)


def SplitStiefoWord(st):
    """Zerlege das Wort st in Vokale und Konsonanten, und bestimme vertikalen Versatz.
    Vokale werden als (dx, dy, ea) ausgegeben, wobei
    dy die Werte -1, 0, +1, +2 haben kann für i, e, a, ö Stufen.
    dx hat die Werte 0, 1, 2 für Konsonantenverbindung, e, u.
    ea ist der effektive Abstand horizontal, der für diesen Vokal verwendet wird.
    '_' und '=' werden am Anfang und Ende angefügt, wenn das
    Wort mit einem Vokal anfängt oder aufhört.
    >>> SplitStiefoWord("b e r n")
    ['b', (1, 0, 1.2), 'r', (0, 0, 0.6), 'n']
    >>> SplitStiefoWord("e r d e")
    ['_', (1, 0, 1.2), 'r', (0, 0, 0.6), 'd', (1, 0, 1.2), '=']
    >>> SplitStiefoWord("n a t i o n")
    ['n', (1, 1, 1.2), 't', (1, -1, 0.2), 'c', (2, -1, 3), 'n']
    """

    # vertikaler Versatz des Worts (auf Grundlinie beginnen)
    y_offset = y_baseline

    # Diese Praefixformen brauchen das Endezeichen (=) wenn sie als einzelnes Wort stehen
    praefix_formen_allein_ohne_endezeichen = {k: v for k, v in praefix_formen.items()
                                                       if v[0] == '-'}

    w = []  # Liste der Buchstaben im Wort

    ## Wort durch Kürzel ersetzen
    if (st in kuerzel):
        st = kuerzel[st]
        st, y_adj = get_y_adjust(st)
        y_offset += y_adj

    ## Buchstabenkette auswerten
    first = True
    pz = False  # vorhergehendes Zeichen
    pv = False  # vorhergehender Vokal
    for z in (st.split(' ')):
        if z in vorsilben:
            z = vorsilben[z]
            z, y_adj = get_y_adjust(z)
            y_offset += y_adj
        v = z in vokalAbstaende or z in praefix_formen
        if first and z in ('i', 'ü'):
            z = 'I'
        if pv and v:
            w.append('c')
        if pz in ('i', 'ü') and z in ('b', 'd', 'f', 'k', 'm', 'p', 'r', 'z',
                                      'cht', 'ng', 'nk', 'st'):
            w[-1] = 'I'
        if pz in ('i', 'ü') and z in ('ch'):  # evtl. 'sp'
            w[-1] = 'ischmal'
        w.append(z)
        pz = z
        pv = v
        first = False
    if w[-1] in ('i', 'ü'):
        w[-1] = 'I'

    ## Wort in Glyphen und Vokal-Tupel zerlegen
    x = []  # zerlegtes Wort
    k = False
    for l in w:
        if l in vokalAbstaende:
            if not x:
                x.append('_')  # Anstrich für Vokal am Wortanfang
            # Vokale durch Abstands-Tupel ersetzen
            x.append(vokalAbstaende[l])
            k = False
        elif l in praefix_formen:
            assert not x, "Praefix nicht am Wortanfang! w={} l={} x={}".format(w, l, x)
            x.append(praefix_formen[l][0])  # Typ (Anstrich, waagr. Strich, Aufstrich)
            x.append(praefix_formen[l][2])  # Vokaltupel
            y_offset += praefix_formen[l][1] - y_baseline  # Vorsilbe bestimmt vert. Versatz
            k = False
        else:
            # Bei 2 Konsonanten besonderen Abstands-Tupel anfügen
            if k:
                x.append((0, 0, dkv))
            x.append(l)
            k = True
    if not k and l not in praefix_formen_allein_ohne_endezeichen:
        x.append('=')  # Wort endet mit Vokal
    return (x, y_offset)


def stiefoWortZuKurve(w):
    """Erzeuge Kurve aus Wort.  Liefert Tupel (x, c, xpos) mit den zum
    Zeichnen notwendigen Informationen: x = Breite des Worts,
    c = Liste der Bezier-Punkte, xpos = Endpositionen der einzelnen
    Buchstaben"""

    sc = 1.5  # Skalierung in x-Richtung für Glyphen und Zwischenräume
    x = 0  # aktuelle Stiftposition
    y = 0  # aktuelle Stiftposition
    c = []  # Bezier-Punkte des Worts
    xpos = [(0, 0)]  # Stift-Endpositionen hinter Vokalen und Konsonanten

    ll, y_offset = SplitStiefoWord(w)
    #print("stiefoWortZuKurve: w={}, ll={}".format(w, ll))
    ll = [None] + ll + [None]
    for i in range(0, len(ll) - 2, 2):
        dl = ll[i]      # Vokal vor dem aktuellen Konsonant
        k = ll[i + 1]   # aktueller Konsonant (Glyph)
        dr = ll[i + 2]  # Vokal nach Konsonant

        # vert. Versatz Konsonant
        k_level = y_baseline
        k, k_adj = get_y_adjust(k)
        if k[0].isdigit():
            k_level = int(k[0])
            k = k[1:]
        y_offset += k_level - y_baseline + k_adj

        assert k in glyphs, "error, unknown glyph: [" + k + "]"
        glFunc = glyphs[k]
        if k != '-':
            w, g = glFunc(dl, dr)  # w = x-Abstand hinter Glyph, g = Bezier-Punkte des Glyphen
        else:
            # waagr. Strich: Länge aus Vokaltupel; Glyph braucht nächsten Konsonant
            strich_l = abs(dr[2]) / sc  # waagr. Strich durch neg. ea markiert
            if i + 3 < len(ll):  # es gibt noch einen nächsten Konsonant
                strich_nkons = ll[i + 3]
            else:
                strich_nkons = None
  #          print("l, nkons", strich_l, strich_nkons)
            w, g = glFunc(strich_l, strich_nkons)

        w *= sc  # in x-Richtung skalieren
        g = scale(g, sc, 1)  # in x-Richtung skalieren
        if dl:
            dx, dy, ea = dl  # Vokalabstände (siehe SplitStiefoWord)
            x += ea if ea > 0 else 0  # Delta x des Stifts ist eff. Abst. des linken Vokals
                          # waagr. Strich (mit neg. ea markiert): kein weiterer Abstand
            y += dy * conv_y_step  # Delta y des Stifts ist dy des linken Vokals
            xpos.append((x, y))
        gs = shiftToPos(g, x, y + (y_offset - y_baseline) * conv_y_step, slant)  # Bezier-Punkte
                            # an die Stiftposition verschieben
        x += w  # Stift hinter Glyph setzen
        xpos.append((x, y))
        for t in gs:
            c.append(t)
    return [(x, c, xpos)]


if __name__ == '__main__':
    print(doctest.testmod())
