#!/usr/bin/env python
# -*- coding: utf-8 -*-

import doctest
import math
import re


#### Einstellungen zum Schriftstil

## Schrägstellung (s.a. render.py)
slant = math.sin(20 * math.pi/180)

## Effektive Abstände (horizontale) für Vokale und Vorsilben
de = 1.1  # e, ä, a, ö
di = 0.3  # i, ü
du = 2.8  # u, au, o, ei, ai, eu, äu, oi
dkv = 0.5  # direkte Konsonantenverbindung ohne Vokal
d_extra = 0.4  # Zuschlag für etwas weitere Verbindung für bestimmte Konsonanten


## Vokale (horiz. und vert. Abstände bei der Verbindung von Konsonanten)
## Tupel (dx, dy, eff. Abst)
vokal_formen = {
    'e': (1, 0, de),
    'ä': (1, 0, de),
    'ae': (1, 0, de),
    'e0': (1, 0, 0.5 * de),  # etwas schmaler, für aber, über, Vorsilben er/mit/an
    'e@': (0, 0, 0.05),  # für Verbindungen mit -lich (außer W-lich F-lich, usw.)
    'u': (2, 0, du),
    'au': (2, 0, du),
    'i': (1, -1, di),
    'I': (1, -1, di + d_extra),  # breiter, für Wortanfang und bestimmte Verbindungen
    'i0': (1, -1, 0.25 * di),  # schmaler, für bestimmte Verbindungen
    'ü': (1, -1, di),
    'ue': (1, -1, di),
    'o': (2, -1, du),
    'a': (1, 1, de),
    'a0': (1, 1, 0.6 * de),
    'A': (1, 1, de  + 0.5 * d_extra),  # breiter, z.B. für "mittelbar"
    'ö': (1, 2, de + 0.3),
    'oe': (1, 2, de + 0.3),
    'ei': (2, 1, du),
    'eu': (2, 2, du),
    'oi': (2, 2, du),
    '/': (1, 2, de - 0.2),  # Aufstriche (be, auf, un)
    '//': (2, 2, du - 0.4),
    '|': (None, None, None)  # belieber horiz. Abstand  TODO: vielleicht auch vert.?
}


## Nachsilben
vokal_formen.update({  # Aufbauschrift 1, 5. Lernabschnitt
    'ung': vokal_formen['u'],
    'igung': vokal_formen['u'],
    'ig': vokal_formen['I'],
    'isch': vokal_formen['I'],
    'tion': vokal_formen['o'],
    'keit': vokal_formen['ei'],
    'igkeit': vokal_formen['ei'],
    'schaft': vokal_formen['a0']
})


praefix_formen = {
    # (Typ, vert. Pos. in Halbstufen, Vokal-Tupel (DX, DY, eff. Abst))
    # Typ: _ normaler Anstrich, - waager. Anstrich, / Aufstrich
    '1_': ("_", 1, vokal_formen['e0']),
    '2_': ("_", 2, (1, 0, 0.75 * de)),  # Vergleich mit Stiefo-Materialien sieht kürzer aus als E
    '3_': ("_", 3, vokal_formen['e0']),
    '1__': ("_", 1, vokal_formen['u']),
    '2__': ("_", 2, vokal_formen['u']),
    '3__': ("_", 3, vokal_formen['u']),
    '0-': ('-', 0, (1, 0, -0.75 * de)),  # TODO: nötig?
    '1-': ("-", 1, (1, 0, -0.75 * de)),
    '2-': ("-", 2, (1, 0, -0.75 * de)),
    '3-': ("-", 3, (1, 0, -(di + d_extra))),
    '4-': ("-", 4, (1, 0, -(di + d_extra))),
    '1--': ("-", 1, (2, 0, -du)),
    '2--': ("-", 2, (2, 0, -du)),
    '3--': ("-", 3, (2, 0, -du)),
    '4--': ("-", 4, (2, 0, -du)),
    '0/': ("/", 0, vokal_formen['/']),
    '0//': ("/", 0, vokal_formen['//'])
}


"""Klartext-Vorsilben in Präfix-Formen / versetzte Konsonanten übersetzen"""
vorsilben_AS1 = {
    'dis': '1d', 'da': '3d', 'dar': '3d |0.75',  # 2. Lernabschnitt
    'er': '2_', 'mit': '1_', 'an': '3_',  # 3. Lernabschnitt
    'zu': '2__', 'vor': '1__', 'ein': '3__',  # 4. Lernabschnitt
    'unter': '2nd', 'über': '1nd',  # 6. Lernabschnitt
    'ab': '3b',  # (Anleitung Selbststudium S. 10-1)
    'ge': '2-', 'aus': '2--',  # 7. Lernabschnitt
    'ver': '2@0', 'für': '1@0', 'nach': '3@0',  # 8. Lernabschnitt
    'gegen': '2@1',
    'durch': '2dd |0',  # 9. Lernabschnitt
    'auf': '0//'
}


nachsilben_AS1 = {
    'lich': 'e@ @*0', 'entlich': 'e@ @*0',  # 8. Lernabschnitt
    'lich*': '@*00', 'entlich*': '@*00',  # Varianten für unten rund (W-lich, F-lich, usw.)
    'doch': '1dd',  # 9. Lernabschnitt
    'noch': '1nn'  # als Nachsilben für jedoch, dennoch
}


vorsilben_AS2 = {
    'selb': '2@2', 'sonst': '1@2', 'stat': '3@2',  # 7. Lernabschnitt
    'deutsch': '4dd |0',  # 9. Lernabschnitt
    'euro': '4rr |0',  # 10. Lernabschnitt
    'voll': '2-- @^*00 i',  # 11. Lernabschnitt
    'in': '1-', 'inter': '1-', 'trans': '3-',
    'pro': '1--', 'bei': '3--',
    'be': '0/', 'un': '0d /', 'darauf': '0d //',
    'fort': '1t'
}


nachsilben_AS2 = {
    'chen': 'ch1',  # 2. Lernabschnitt
    'ander': '3@^00',  # 3. Lernabschnitt
    'voll': 'u @^*00',  # 11. Lernabschnitt
    'bar': '{a0 r}(-0.5,0)',  # aber für viele Wörter Anpassung a/a0 und Versatz nötig
    'barkeit': '{a0 r keit}(-0.5,0)',  # (Belegstelle erst in Text 18)
    'gleich': 'ch4',  # 27. Lernabschnitt
    'rechn': 'ch3',  # Anhang
    'alich': '|0.25 ++3@*0', 'schaftlich': '|0.25 ++3@*0'
}


vorsilben = {**vorsilben_AS1, **vorsilben_AS2}
nachsilben = {**nachsilben_AS1, **nachsilben_AS2}


kuerzel_AS1 = {
    'der': '+2.', 'die': '--2.', 'das': '++3.',  # 1. Lernabschnitt
    'des': '2s', 'sich': '1s', 'sein': '3s',
    'dem': '2m', 'mich': '1m', 'mir': '1m', 'mein': '3m',
    'den': '2en', 'nicht': '1en', 'man': '3en',
    'dies': '1d',  # 2. Lernabschnitt
    'ist': '1t', 'von': '1f',
    'wir': '1w', 'hab': '3h', 'hast': '3h', 'hat': '3h', 'gehab': '3- h',
    'und': '2nd', 'sind': '1nd',  # 6. Lernabschnitt
    'unter': '2nd e0', 'über': '1nd e0', 'aber': '3nd e0',
    'werd': '2c', 'wird': '1c', 'wirst': '1c', 'war': '3c',
    'würde': '1c e@',  # (Anleitung Selbststudium S. 10-1)
    'wurd': '2c u', 'word': '1c u', 'geword': '1c u',
    'es': '+2-', 'sie': '-2-',  # 7. Lernabschnitt
    'aus': '++2--', 'so': '--2--',
    'endlich': '2@*0',  # 8. Lernabschnitt
    'durch': '2dd', 'doch': '1dd',  # 9. Lernabschnitt
    'uns': '2nn', 'noch': '1nn',
    'in': 'i n',  # Wort „in“ wird normal geschrieben, waagr. Strich nur für Vorsilbe
}


kuerzel_AS2 = {
    'auch': '2@^0', 'ich': '1@^0', 'ander': '3@^0', 'dich': '1d* | @^00',  # 3. Lernabschnitt
    'sonder': '2@1 o', 'sonderlich': '2@1 u @^*00', # 6. Lernabschnitt
    'selbst': 'selb', 'selbständig': 'selb i',  # 7. Lernabschnitt
    'selbstverständlich': 'selb |0 @*00', 'sonstig': 'sonst i',
    'staatlich': 'stat e@ @*0', 'stattlich': 'stat |0 @*00',  # Anhang
    'status': 'stat u s',
    'kein': '3nn',  # 9. Lernabschnitt
    'nur': '2rr', 'oder': '1rr', 'europa': '4rr',  # 10. Lernabschnitt
    'deutschland': '4dd |0.1 nd',
    'voll': '2-- @^*00',  # 11. Lernabschnitt
    'prüfbar': 'p ü f {a r}(-0.25,0)', 'nachprüfbar': 'nach p ü f {a r}(-0.25,0)',
    'dankbar': 'd a nk {a r}(0,0)',
    'mittelbar': '1l {A r}(-0.1,0)', 'unmittelbar': 'un 1l {A r}(-0.1,0)',  # (Belegstelle "unmittelbar" erst in Text 12)
    'muss': 'mm', 'musst': 'mm*',  # 14. Lernabschnitt
    'müss': '1mm', 'müsst': '1mm*',
    'jedoch': 'j |0 1dd',  # 18. Lernabschnitt
    # TODO: 'dennoch': '2en „enger Abstand“ 1nn',  # 24. Lernabschnitt, Bsp. 2
    'als': '-4-',  # „als“ etwas tiefer, sie Aufbau2, S. 17
    'pro': '2--', 'bei': '4--',
    'darauf': '0d //',
    'hätte': '2t', 'hatte': '3t', 'heute': '4t',
    'für': '1@0',
    'lebhaft': 'l e b {a}(-0.4,0)',
    'gewissenhaft': 'ge w i {a0}(-0.3,0) s',
    'einfach': 'ein {a0}(0,-0.25)', 'mehrfach': 'm {a}(-0.4,0) r',
    'ebenfalls': 'e {a s} b',
    'nachbar': '+3@0 {a0 r}(0.4,-0.25)',
    'nachbarschaft': '+3@0 {a0 r schaft}(0.4,-0.25)',

    'nachvollziehbar': 'nach u @^*00 i z i bar'  # TODO: in Materialien?
}


kuerzel = {**kuerzel_AS1, **kuerzel_AS2}


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
    return (dy == 0 and ea < 0)


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


def untenEingelegt(dr, runder = False):
    if runder:
        m = [(0, 0.25),
             (0.0, 0.0) if dr else (-0.1, 0),
             (-0.2, 0) if dr else (-0.3, 0)]
        e = [(-0.5, 0.0)] if dr else []
    else:
        m = [(0, 0.25),
             (0.0, 0.0),
             (-0.2, 0)]
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
    """Kreis gegen UZS, auf Grundlinie liegend"""
    # (Startpunkt ist nicht definiert)
    m = [(0.25, 0),    (0.5, 0.25),  (0.5, 0.5),   # [Q1], [Q2], (Q3/R0)
         (0.5, 0.75),  (0.25, 1),    (0, 1),       # [R1], [R2], (R3/S0)
         (-0.25, 1),   (-0.5, 0.75), (-0.5, 0.5),  # [S1], [S2], (S3/T0)
         (-0.5, 0.25), (-0.25, 0),   (0, 0)]       # [T1], [T2], (T3/U0)
    return m


def kreis_ab(dl, dr):
    """Kreis im UZS, an Grundlinie hängend"""
    return scale(kreis_auf(dl, dr), 1, -1)


def welle_auf(dl, dr):
    b = []
    m = [(0.25, 0.3), (0.5, 0), (0.75, -0.3)]  # [Q2], (Q3/R0), [R1]
    e = []
    return b + m + e


def welle_ab(dl, dr):
    return scale(welle_auf(dl, dr), 1, -1)


def bogen_auf(dl, dr):
    """Bogen aufwärts, für weites N (uns usw.). Beide Enden immer spitz."""
    h = 0.65
    l = 0.3
    b = [(0, 0), (0, 0)]      # Start immer spitz [P2], (P3/Q0)
    m = [(l, h), (1 - l, h)]  # [Q1], [Q2]
    e = [(1, 0), (1, 0)]      # Ende immer spitz (Q3/R0)
    return b + m + e


def bogen_ab(dl, dr):
    """Bogen abwärts, für weites D (durch usw.).

    Ende nur spitz wenn allein steht, sonst letzten Stützpunkt etwas früher,
    letzten Kontrollpunkt für Fortsetzung in gleicher Richtung setzen, damit
    glatte Verbindung zu Folgekonsonant.
    """
    y0 = 0.5  # Höhe Anfang- und Endpunkt
    h = 0.65
    l = 0.3
    b = [(0, y0), (0, y0)]    # Start immer spitz [P2], (P3/Q0)  # TODO: ändern für jedoch
    m = [(l, y0 - h), (1 - l, y0 - h)]  # [Q1], [Q2]
    e = [(1, y0), (1, y0)] if not dr else [(1 - l/2, y0 - h/2), (1 - l/3, y0 - h/3)]  # Ende (Q3/R0)
    return b + m + e


### Glyphen (Konsonanten)

def glyph_d(dl, dr, verbindung_schmal = False):
    b = [(0, 0.5)] if dl else []
    m = [(0, 0.5), (0, 0.5),
         (0.2, 0), (0.5, 0)]
    if dr:
        e = [(0.55 if verbindung_schmal else 0.8, 0)]
    else:
        e = [(0.5, 0), (0.6, 0.05), (0.6, 0.05)]
    return (0.5, b + m + e)


def glyph_n(dl, dr):
    y1 = 0.5
    y0 = 0.0
    b = [(-0.3, y1)] if dl else [(-0.2, y1 - 0.05), (-0.2, y1 - 0.05), (-0.1, y1)]
    m = [(-0.1, y1), (0.2, y1),
         (0.4, y0), (0.4, y0)]
    e = [(0.4, y0)] if dr else []
    return (0.4, b + m + e)


def glyph_r(dl, dr):
    y1 = 0.5
    y0 = 0.0
    b = [(-0.3, y1)] if dl else [(-0.2, y1 - 0.05), (-0.2, y1 - 0.05), (-0.1, y1)]
    m = [(-0.1, y1), (0.2, y1),
         (0.2, y0), (0.5, y0)]
    e = [(0.7, y0)] if dr else [(0.5, y0), (0.6, y0 + 0.1), (0.6, y0 + 0.1)]
    return (0.4, b + m + e)


def glyph_r_var(dl, dr):
    """flaches R / „Welle“"""
    b = [(0, -0.1)] * 2 if not dl else []
    m = welle_auf(dl, dr)
    e = [(1, 0.1)] * 2 if not dr else []
    return [0.7, shift(scale(b + m + e, 0.7, 1), 0, 0.1)]


def glyph_r_weit(dl, dr):
    sx = 3
    sy = 2
    w, m = glyph_r_var(dl, dr)
    return (w * sx, scale(m, sx, sy))


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


def glyph_w_2stuf(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_w(dl, dr)
    return (w * sx, scale(m, sx, sy))


def glyph_w_var(dl, dr, y1 = 0.4, dx1 = 0.2):
    w, b_m = glyph_w(dl, True)
    b_m[-1] = (w + dx1, 0)  # letzter Kontrollpunkt von glyph_w liegt sonst zu weit rechts
    e = [(w + dx1, y1), (w, y1), (w - dx1, y1),
         (w - dx1, 0), (w, 0)]
    if dr:
        e.append((w + dx1, 0))
    return(w + 0.5*dx1, b_m + e)


def glyph_w_var_2stuf(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_w_var(dl, dr, y1 = 0.4/sy, dx1 = 0.2/sx)
    return (w * sx, scale(m, sx, sy))


def glyph_w_var2_2stuf(dl, dr):
    assert not dl and not dr, 'Glyph “w var2 2stuf” must not be connected.'
    # FIXME "rückwärts", "vorwärts" ermöglichen -> disjointed?!
    m = [(0.6, 2),
         (-0.2, 1.1), (-0.2, 0.9), (0.6, 0)]
    return (0.5, scale(m, 0.6, 1))


def glyph_m(dl, dr):
    b = [(-0.3, 1)] if dl else [(-0.2, 0.9), (-0.2, 0.9), (-0.1, 1)]
    m = [(0, 1), (0.3, 1),
         (0.3, 0.0), (0, 0)]
    e = [(-0.4, 0.0)] if dr else []
    return (0.3, shift(b + m + e, 0.1))


def glyph_m_2stuf(dl, dr):
    sx = 1.8
    sy = 2
    w, g = glyph_m(dl, dr)
    return (w * sx, scale(g, sx, sy))


def glyph_m_var(dl, dr):
    assert not dl, 'Glyph “m var” only allowed at beginning of word.'
    y1 = 0.3
    w, b_m = glyph_m(False, False)
    if not dr:
        e = [(0, 0), (0, y1), (w, y1)]
    else:
        e = [(-0.05, 0), (-0.05, y1 - 0.10), (w - 0.1, y1 - 0.05), (w + 0.1, y1)]
    return (w, b_m + e)


def glyph_m_weit_ALT(dl, dr):
    b = [(-0.2, 0.7), (0.3, 0.9)] if not dl else []
    m = [(0.8, 1), (1.1, 1), (1.7, 1),
         (1.4, 0.0), (1.1, 0)]
    e = [(0.8, 0.0)] if dr else []
    return (1.5, (b + m + e))


def glyph_m_weit(dl, dr):
    b = [(-0.1, 0.6), (0.3, 0.9)] if not dl else []
    m = [(0.2 if dl else 0.6, 1), (0.9, 1), (1.5, 1),
         (1.2, 0.0), (0.9, 0)]
    e = [(0.6, 0.0)] if dr else []
    return (1.3, (b + m + e))


def glyph_m_weit_var(dl, dr):
    assert not dr, 'Glyph “m weit var” only allowed at end of word.'
    x0 = 0.9  # last x from m part of glyph_m_weit
    w, b_m = glyph_m_weit(dl, False)
    e = [(x0 - 0.15, 0), (x0 - 0.15, 0.3), (x0 + 0.25, 0.25)]
    return (w, b_m + e)


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


def glyph_b_2stuf(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_b(dl, dr)
    return(w * sx, scale(m, sx, sy))


def glyph_j(dl, dr):
    w, g = glyph_b(dl, dr)
    return (0.7, scale(g, 1, 1, 0.7))


def glyph_j_2stuf(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_j(dl, dr)
    return(w * sx, scale(m, sx, sy))


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


def glyph_f_2stuf(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_f(dl, dr)
    return (w*sx, scale(m, sx, sy))


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


def glyph_k_2stuf(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_k(dl, dr, runder=False)
    return (w*sx, scale(m, sx, sy))


def glyph_cht(dl, dr):
    w, g = glyph_k(dl, dr, runder = False)
    return (0.8, scale(g, 1, 1, 0.5))


def glyph_h(dl, dr, runder = True):
    b = obenSpitz(dl)
    m = [(0, 0.5)]
    e = untenEingelegt(dr, runder = runder)
    return (0.2, shift(b + m + e, 0.2))


def glyph_z(dl, dr):
    b = obenGewoelbt(dl)
    m = [(0, 0.5)]
    e = untenSpitz(dr)
    return (0.2, b + m + e)


def glyph_z_halbstuf(dl, dr):
    w, g = glyph_z(dl, dr)
    return (0.2, scale(g, 1, 0.5))


def glyph_z_2stuf(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_z(dl, dr)
    return(w * sx, scale(m, sx, sy))


def glyph_sch(dl, dr):
    b = obenGewoelbt(dl)
    m = [(0, 0.5)]
    e = untenEingelegt(dr)
    return (0.4, shift(b + m + e, 0.2))


def glyph_sch_halbstuf(dl, dr):
    w, g = glyph_sch(dl, dr)
    return (0.4, scale(g, 1, 0.5))


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


def glyph_l_2stuf(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_l(dl, dr)
    return (w * sx, scale(m, sx, sy))


def glyph_ch(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenEingelegt(dr)
    return (0.4, shift(b + m + e, 0.2))


def glyph_ch_halbstuf(dl, dr):
    sx = 1
    sy = 0.5
    w, m = glyph_ch(dl,dr)
    m = scale(m, sx, sy, s=+slant/2)
    m = shift(m, -0.2, 0)
    return (w * sx, m)


def glyph_ch_einhalbstuf(dl, dr):
    """1,5-stufiges CH"""
    sx = 1.25
    sy = 1.5
    w, m = glyph_ch(dl, dr)
    return (w * sx, scale(m, sx, sy, s=+slant/2))


def glyph_ch_2stuf(dl, dr):
    sx = 1.5
    sy = 2
    w, m = glyph_ch(dl, dr)
    return (w * sx, scale(m, sx, sy, s=+slant/2))


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


def glyph_s_var(dl, dr):
    y1 = 0.25
    w, b_m = glyph_s(dl, False)
    if not dr:
        e = [(-0.1, 0.1), (0, y1 + 0.1), (w, y1 - 0.1)]
    else:
        e = [(-0.05, 0), (-0.05, y1 - 0.10), (w - 0.1, y1 - 0.05), (w + 0.1, y1)]
    return (w, b_m + e)


def glyph_sp(dl, dr):
    b = kopfSchleife(dl)
    m = [(0, 0.5)]
    e = untenSpitz2(dr)
    return (0.4, shift(b + m + e, 0))


def glyph_qu(dl, dr):
    w, g = glyph_f(dl, dr)
    return (0.2, scale(g, 1, 0.5))


def glyph_th(dl, dr):
    w, g = glyph_h(dl, dr)
    return (0.2, scale(g, 1, 0.5))


def glyph_tsch(dl, dr):
    w, g = glyph_nd(dl, dr)
    return (0.3, scale(g, 1, 0.5))


def glyph_x(dl, dr):
    w, m = glyph_k(dl, dr)
    return (w * 0.5, scale(m, 0.5, 0.5))


def glyph_punktschleife_geg_uzs(dl, dr, schmal = False):
    x0 = 0.1 if schmal else 0.3
    b = [(0, 0)] if not dl else [(0, 0), (0, 0)]
    m = scale(kreis_auf(dl, dr), 0.1, 0.15)
    e = [(x0, -0.1), (x0 + 0.1, 0.2), (x0 + 0.1, 0.2)] if not dr else [(x0 + 0.1 if schmal else 0.2, -0.1)]
    return [0.15 if schmal else 0.3, (b + m + e)]


def glyph_punktschleife_geg_uzs_anstrich(dl, dr, schmal = False):
    x0 = 0.25 if not dl else 0.125
    if not schmal:
        x0 += 0.25
    if not dl:
        if not dr:
            b = [(0, 0), (0.2, -0.05), (x0 - 0.2, -0.05), (x0, 0.025)]
        else:
            b = [(0, 0), (0, 0), (x0, 0), (x0, 0)]
    else:
        if not dr:
            b = [(0, 0), (0, 0), (1/3*x0, 0), (2/3*x0, 0.0125), (x0, 0.025)]
        else:
            b = [(0, 0), (0, 0), (0, 0), (x0, 0), (x0, 0)]
    m = shift(scale(kreis_auf(dl, dr), 0.1, 0.15), x0, 0.05 if not dr else 0)
    e = [(x0, 0.05)]*3 if not dr else [(x0 + 0.05, 0)]
    return [x0, (b + m + e)]


def glyph_punktschleife_im_uzs(dl, dr, schmal = False):
    _, m = glyph_punktschleife_geg_uzs(None, None, schmal=schmal)
    m = shift(reversed(rotate_ccw(m, math.pi)), 0.25 if schmal else 0.4, 0.2)
    if dl:
        m = m[2:]
    if dr:
        m = m[:-2]
    return [0.25 if schmal else 0.4, m]

def glyph_punktschleife_im_uzs_anstrich(dl, dr, schmal = False):
    w, g = glyph_punktschleife_geg_uzs_anstrich(dl, dr, schmal)
    return [w, scale(g, 1, -1, 0)]


def glyph_schleife_halbstuf_geg_uzs(dl, dr):
    assert not dl, "Glyphen 'gegen/will/all usw.' duerfen nur am Wortanfang stehen!"
    # FIXME: "dagegen" ermöglichen
    b = [(0, 0)]  # (P0)
    m = kreis_auf(dl, dr)
    e = [(0.75, 0), (1, 0.5), (1, 0.5)] if not dr else [(0.75, 0)]
    return [0.5, shift(scale(b + m + e, 0.4, 0.5), 0.2, 0)]


def glyph_schleife_1stuf_geg_uzs(dl, dr):
    assert not dl, "Glyph 'selbst' darf nur am Wortanfang stehen!"
    b = [(0, 0)]  # (P0)
    m = kreis_auf(dl, dr)
    e = [(0.5, 0), (0.75, 0.25), (0.75, 0.25)] if not dr else [(0.35, 0)]
    return [0.75, shift(scale(b + m + e, 0.8, 1), 0.4)]


def glyph_en(dl, dr):
    assert not dl, 'Glyph “en” only allowed at beginning of word.'
    b = [(0, 0), (0, 0)]
    w, m = glyph_n(b, dr)
    e = []
    return [w + 0.05 + w, b + shift(m + e, w + 0.05, 0)]


def glyph_n_weit(dl, dr):
    b = ([(0, 0)]*2 if not dl else [])  # [P0], [P1]
    m = bogen_auf(dl, dr)
    e = [(1, 0)]*2 if not dr else []
    return [2, scale(b + m + e, 2, 1)]


def glyph_d_weit(dl, dr):
    y0 = 0.5
    b = ([(0, y0)]*2 if not dl else [])  # [P0], [P1]
    m = bogen_ab(dl, dr)
    e = [(1, y0)]*2 if not dr else []
    return [2, scale(b + m + e, 2, 1)]


def glyph_ent(dl, dr):
    assert not dl, 'Glyph “ent” only allowed at beginning of word.'
    b = obenRund(True)
    m = [(0, 0.5)]
    e = untenSpitz(dr)
    return (0.41, scale([(0, 0)]*2 + shift(b + m + e, 0.8), 0.5, 0.5))


def glyph_los(dl, dr):  # FIXME: ist Symbol für voll
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


def glyph_jetzt(dl, dr):
    w, g = glyph_b(dl, dr)
    return (0.5, scale(g, 1, 1, 0.5))


def glyph_punkt(dl, dr):
    assert not dl and not dr, 'Glyph “.” (dot) must not be connected.'
    b = [(0, 0)]
    m = scale(kreis_auf(dl, dr), 0.1, 0.1)
    e = []
    return (0.1, b + m + e)


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
        elif naechster_kons.startswith('@'):
            y0 = 0
        else:
            y0 = 0.5
        e = [(l, y0)]
    b = [(0, y0), (0, y0)]
    m = [(l, y0), (l, y0)]
    return (l, (b + m + e))


### Lookup Konsonanten -> Glyph-Funktionen

glyphs = {
    'b': glyph_b,
    'b4': glyph_b_2stuf,
    'd': glyph_d,
    'd*': lambda dl, dr: glyph_d(dl, dr, verbindung_schmal=True),  # für "dich"
    'f': glyph_f,
    'f4': glyph_f_2stuf,
    'g': glyph_g,
    'h': glyph_h,
    'h0': lambda dl, dr: glyph_h(dl, dr, runder=False),
    'j': glyph_j,
    'j4': glyph_j_2stuf,
    'k': glyph_k,
    'k4': glyph_k_2stuf,
    'l': glyph_l,
    'l4': glyph_l_2stuf,
    'm': glyph_m,
    'm*': glyph_m_var,
    'm4': glyph_m_2stuf,
    'mm': glyph_m_weit,
    'mm*': glyph_m_weit_var,
    'n': glyph_n,
    'p': glyph_p,
    'r': glyph_r,
    's': glyph_s,
    's*': glyph_s_var,
    't': glyph_t,
    'w': glyph_w,
    'w*': glyph_w_var,
    'w4': glyph_w_2stuf,
    'w*4': glyph_w_var_2stuf,
    'w**4': glyph_w_var2_2stuf,
    'x': glyph_x,
    'z': glyph_z,
    'z1': glyph_z_halbstuf,
    'zw': glyph_z_halbstuf,
    'z4': glyph_z_2stuf,
    'sch': glyph_sch,
    'sch1': glyph_sch_halbstuf,
    'schw': glyph_sch_halbstuf,
    'ch': glyph_ch,
    'ch1': glyph_ch_halbstuf,
    'ch3': glyph_ch_einhalbstuf,
    'ch4': glyph_ch_2stuf,
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
    'q':        glyph_qu,
    'c': glyph_c,  # Vokalzeichen
    'en': glyph_en,
    'nn': glyph_n_weit,
    'dd': glyph_d_weit,
    '@0': glyph_punktschleife_geg_uzs,
    '@': glyph_punktschleife_geg_uzs,  # Abkürzung
    '@00': lambda dl, dr: glyph_punktschleife_geg_uzs(dl, dr, schmal = True),
    '@^0': glyph_punktschleife_geg_uzs_anstrich,
    '@^': glyph_punktschleife_geg_uzs_anstrich,  # Abkürzung
    '@^00': lambda dl, dr: glyph_punktschleife_geg_uzs_anstrich(dl, dr, schmal = True),
    '@*0': glyph_punktschleife_im_uzs,
    '@*': glyph_punktschleife_im_uzs,  # Abkürzung
    '@*00': lambda dl, dr: glyph_punktschleife_im_uzs(dl, dr, schmal = True),
    '@^*0': glyph_punktschleife_im_uzs_anstrich,
    '@^*00': lambda dl, dr: glyph_punktschleife_im_uzs_anstrich(dl, dr, schmal = True),
    '@1': glyph_schleife_halbstuf_geg_uzs,
    '@2':   glyph_schleife_1stuf_geg_uzs,
    'r*': glyph_r_var,
    'rr': glyph_r_weit,
    'ent':      glyph_ent,     # "ent"
    'los':      glyph_los,     # "los"
    '.': glyph_punkt,
    '-': glyph_waagr_strich,
    '_': lambda dx, dy: (0, [(0, 0), (0, 0)]),  # Startpunkt normaler Anstrich
    '/': lambda dx, dy: (0, [(0, 0), (0, 0)]),  # Startpunkt Aufstrich
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
    assert isinstance(s, str), 'Not a string: {}'.format(s)
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
    y_word_offset = y_baseline

    # Diese Praefixformen brauchen das Endezeichen (=) wenn sie als einzelnes Wort stehen
    praefix_formen_allein_ohne_endezeichen = {k: v for k, v in praefix_formen.items()
                                                       if v[0] == '-'}

    w = []  # Liste der Buchstaben im Wort

    ## Kürzel auflösen
    if (st in kuerzel):
        st = kuerzel[st]
        st, y_adj = get_y_adjust(st)
        y_word_offset += y_adj

    ## Vor- und Nachsilben auflösen (ergibt Token)
    st_tokenised = []
    first_form = True
    for z in st.split(' '):
        if first_form and z in vorsilben:
            pfx = vorsilben[z]
            st_tokenised.extend(pfx.split(' '))
        elif not first_form and z in nachsilben:
            pfx = nachsilben[z]
            st_tokenised.extend(pfx.split(' '))
        else:
            st_tokenised.append(z)
        first_form = False
    st_tokenised = ' '.join(st_tokenised)

    ## zweiteilige Formen (Durchstreichungen) auflösen
    disjointed = re.search(r'\{(.+)\}(\(\+?-?\d+\.?\d*,\+?-?\d+\.?\d*\))?', st_tokenised)
    if disjointed:
        disjointed_code = disjointed.group(1)
        adjust_str = disjointed.group(2)
        st_tokenised = re.sub(r'\{(.+)\}(\(.*\))?', '!', st_tokenised)
        if adjust_str:
            disjointed_adjust = tuple(map(float, adjust_str[1:-1].split(',')))
            #print("adjust_str={}, tuple={}".format(adjust_str, disjointed_adjust))
        else:
            disjointed_adjust = None
    else:
        disjointed_code = None
        disjointed_adjust = None


    ## Token auswerten (Präfixe einfügen, bestimmte Vokalanpassungen)
    first_token = True
    pz = False  # vorhergehendes Zeichen
    pv = False  # vorhergehender Vokal
    pfx2 = None  # zweites Token von zusammengesetzter Vorsilbe
    for z in st_tokenised.split(' '): #(st.split(' ')):
        #print("z = {}, pz={}, pv={}".format(z, pz, pv))
        if z == '!':
            w.append(z)
            continue

        v = z in vokal_formen or z[0] == '|' or z in praefix_formen
        if first_token and z in ('i', 'ü', 'ue'):
            z = 'I'
        if pv and v:
            w.append('c')
        if pz in ('i', 'ü', 'ue') and z in ('b', 'd', 'f', 'g', 'k', 'm', 'p', 'r', 'z',
                                            'cht', 'ng', 'nk', 'st'):
            w[-1] = 'I'
        if pz in ('i', 'ü', 'ue') and z in ('ch'):  # evtl. auch 'sp'
            w[-1] = 'i0'
        w.append(z)
        pz = z
        pv = v
        first_token = False
    if w[-1] in ('i', 'ü', 'ue'):
        w[-1] = 'I'

    ## Token in Glyphen und Vokal-Tupel auflösen
    x = []  # zerlegtes Wort
    k = False
    for l in w:
        if l in vokal_formen or l[0] == '|':
            if not x:
                x.append('_')  # Anstrich für Vokal am Wortanfang
            # Vokale durch Abstands-Tupel ersetzen
            if l[0] != '|':
                x.append(vokal_formen[l])
            else:
                stretch = float(l[1:]) if len(l) > 1 else 0
                x.append((stretch, 0, stretch))
            k = False
        elif l in praefix_formen:
            assert not x, "Praefix nicht am Wortanfang! w={} l={} x={}".format(w, l, x)
            x.append(praefix_formen[l][0])  # Typ (Anstrich, waagr. Strich, Aufstrich)
            x.append(praefix_formen[l][2])  # Vokaltupel
            y_word_offset += praefix_formen[l][1] - y_baseline  # Vorsilbe bestimmt vert. Versatz
            k = False
        elif l == '!':
            x.append(l)
        else:
            # Bei 2 Konsonanten besonderen Abstands-Tupel anfügen
            if k:
                x.append((0, 0, dkv))
            x.append(l)
            k = True
    if not k and l not in praefix_formen_allein_ohne_endezeichen:
        x.append('=')  # Wort endet mit Vokal
    return (x, y_word_offset, disjointed_code, disjointed_adjust)


def slanted(x, y, s=slant):
    return (x + s * y, y)


def stiefoWortZuKurve(w):
    """Erzeuge Kurve aus Wort.  Liefert Tupel (x, c, xpos) mit den zum
    Zeichnen notwendigen Informationen: x = Breite des Worts,
    c = Liste der Bezier-Punkte, xpos = Endpositionen der einzelnen
    Buchstaben"""

    sc = 1.5  # Skalierung in x-Richtung für Glyphen und Zwischenräume
    c = []  # Bezier-Punkte des Worts
    disjointed_outline_offset = None

    ll, y_word_offset, disjointed, disjointed_adj = SplitStiefoWord(w)
    #print("stiefoWortZuKurve: w={}, ll={}, y_w_off={}, disj={}".format(w, ll, y_word_offset,disjointed))

    ll = [None] + ll + [None]
    if disjointed:
        i_disjointed = ll.index('!') - 1
        ll.remove('!')

    x = 0  # aktuelle Stiftposition
    y = (y_word_offset - y_baseline) * conv_y_step
    xpos = [slanted(x, y)]  # Stift-Positionen (Startpunkt und nach jedem Buchstaben)

    #print("start xpos={}, x={}, y={}".format(xpos, x, y))
    for i in range(0, len(ll) - 2, 2):
        #print("  i={}".format(i))
        dl = ll[i]      # Vokal vor dem aktuellen Konsonant
        k = ll[i + 1]   # aktueller Konsonant (Glyph)
        dr = ll[i + 2]  # Vokal nach Konsonant

        # vert. Versatz Konsonant
        k_level = y_baseline
        k, k_adj = get_y_adjust(k)
        if k[0].isdigit():
            k_level = int(k[0])
            k = k[1:]
        y_offset = (k_level + k_adj - y_baseline) * conv_y_step
        #print("  k={} k_level={}, k_adj={}, y_offset={}".format(k, k_level, k_adj, y_offset))
        assert k in glyphs, 'Unknown glyph: [{}]'.format(k)
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
            w, g = glFunc(strich_l, strich_nkons)

        w *= sc  # Breite in x-Richtung skalieren
        g = scale(g, sc, 1)  # Glyph in x-Richtung skalieren
        y += y_offset  # vert. Versatz Konsonant

        if dl:
            dx, dy, ea = dl  # Vokalabstände (siehe SplitStiefoWord)
            x += ea if ea > 0 else 0  # Delta x des Stifts ist eff. Abst. des linken Vokals
                          # waagr. Strich (mit neg. ea markiert): kein weiterer Abstand
            y += dy * conv_y_step  # Delta y des Stifts ist dy des linken Vokals
            xpos.append(slanted(x, y))

        if disjointed:
            if i == i_disjointed:    # Mitte Vokal
                disjointed_outline_offset = (x - ea/2 if ea > 0 else x + ea/2, y)
            if i + 1 == i_disjointed:   # am Konsonant
                disjointed_outline_offset = (x, y)

        gs = shiftToPos(g, x, y, slant)  # Bezier-Punkte an die Stiftposition verschieben
        x += w  # Stift hinter Glyph setzen

        curve_width = x
        for t in gs:
            c.append(t)
        xpos.append(slanted(x, y))

    if disjointed:
        dj_x, dj_y = disjointed_outline_offset
        if disjointed_adj:
            dj_x += disjointed_adj[0]
            dj_y += disjointed_adj[1] * conv_y_step
        dj_off = (-(curve_width - dj_x), dj_y)
        dj_width, dj_curve, dj_pos, _ = stiefoWortZuKurve(disjointed)[0]
        if disjointed_outline_offset[0] + dj_width < curve_width:  # bei nicht über Wortende hinaushängendem Zeichen Wortlänge anpassen
            dj_width = curve_width - disjointed_outline_offset[0]
        disjointed_outline = [(dj_width, dj_curve, dj_pos, dj_off)]
    else:
        disjointed_outline = []
    return [(curve_width, c, xpos, None)] + disjointed_outline


if __name__ == '__main__':
    print(doctest.testmod())
