#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

__all__ = ['convert_text', 'wortZuStiefo', 'list_to_text', 'text_to_list']

# ===================================================================================


def splitText(text):
    """
    Zerlegt einen Text in Worte und Interpunktion.

    >>> splitText("20'000 Meilen unter dem Meer")
    ["20'000", 'Meilen', 'unter', 'dem', 'Meer']
    >>> splitText('Er sagte:" Hallo, wie gehts?"')
    ['Er', 'sagte', ':"', 'Hallo', ',', 'wie', 'gehts', '?"']
    >>> splitText('"Warum nicht?" sagte der Esel, "ich bitte dich sogar darum!"')
    ['"', 'Warum', 'nicht', '?"', 'sagte', 'der', 'Esel', ',', '"', 'ich', 'bitte', 'dich', 'sogar', 'darum', '!"']
    >>> splitText('Jules Verne{!page!}yyy{"Original"}xxx')
    ['Jules', 'Verne', '{!page!}', 'yyy', '{"Original"}', 'xxx']
    """
    return [x for x in re.split(r"(\{[!\"$].*?[!\"$]\})|((?=\D)\w+)|\s+", text) if x and x != '\ufeff']

    # words = re.split(r"\s+|(\{[!\"$].*?[!\"$]\})", text)


## Ersetzungsmuster (Regex) für wortZuStiefo()
## FIXME: sinnvolle Codierung Präfixe; z.Zt. müssen Codes genau 1 Buchstaben lang sein
regeln = [
    ## Aufbauschrift
    # Vorsilben am Wortanfang
    (r"\bmit", "1"),
    (r"\ber", "2"),
    (r"\ban'", "3"),  # Vorsilbe „an“ wenn danach Trennzeichen (Apostroph)
    (r"\ban([^dgkt])", r"3\1"),  # oder wenn kein N-Dipthong; nicht-Apostroph-Zeichen muss bei Ersetzung wiederhergestellt werden ("\1")
    (r"\bvor", "4"),
    (r"\bzu", "5"),
    (r"\bein", "6"),
    (r"\baus'", "7"),
    (r"\baus([^cpt])", r"7\1"),  # analog Vorsilbe „an“

    ## Grundschrift:
    ('sch', 'Z'),
    ('cht', 'X'),
    ('ch', 'C'),

    ('eie', 'ei e'),

    ('aa', 'a'),
    ('ah', 'a'),
    ('äh', 'ä'),
    #('bb', 'b'),
    #('dd', 'd'),
    ('ee', 'e'),
    ('eh', 'e'),
    ('(?<!au)ff', 'f'),
    #('gg', 'g'),
    ('ie', 'i'),
    ('ih', 'i'),
    ('ck', 'k'),
    #('kk', 'k'),
    ('ll', 'l'),
    ('mm', 'm'),
    ('nn', 'n'),
    ('oo', 'o'),
    ('oh', 'o'),
    ('öh', 'ö'),
    ('pp', 'p'),
    ('rr', 'r'),
    ('sst', 'sS'),
    ('(?<=[aeiuoäöü])ss', 's'),
    ('ß', 's'),
    ('tt', 't'),
    ('uh', 'u'),
    ('üh', 'ü'),

    ('ph', 'f'),

    ('st', 'S'),
    ('nt', 'N'),

    ('(?<=[aeiuoäöü])tz', 'z'),

    ('nd', 'D'),
    ('ng', 'G'),
    ('nk', 'K'),
    ('pf', 'F'),
    ('sp', 'P'),

    ('au', 'U'),
    ('ai', 'E'),
    ('ei', 'E'),
    ('ay', 'E'),
    ('ey', 'E'),
    ('eu', 'O'),
    ('äu', 'O'),
    ('oy', 'O'),

    ('qu', 'q'),
    ('x', 'x'),
    ('v', 'f'),

    ('y', 'i'),
    ('c', 'z'),

    #('ä','e'),
    #('ü','i'),
    #('U','u'),
    #('N','D'),
    #('K','G'),

    ("'", ''),
    (' ', ''),
    ('\u00a0', ''),
    ('H', 'h')
]


def wortZuStiefo(w):
    """
    Konvertiert ein Wort in Normaltext mit Hilfe von ein paar Regeln in das interne Format „Stiefocode“.

    >>> [wortZuStiefo(w) for w in "Waschbär Bauer an'gekommen angst Schlüssel'loch nichtig Geschichte".split()]
    ['w a sch b ä r', 'b au e r', 'an g e k o m e n', 'a ng st', 'sch l ü s e l l o ch', 'n i cht i g', 'g e sch i cht e']
    >>> [wortZuStiefo(w) for w in "Der Esel und die Ziege".split()]
    ['d e r', 'e s e l', 'u nd', 'd i', 'z i g e']
    >>> [wortZuStiefo(w) for w in "Freund möchte stelle verletzt andern'tags führen".split()]
    ['f r eu nd', 'm ö cht e', 'st e l e', 'f e r l e z t', 'a nd e r n t a g s', 'f ü r e n']
    >>> [wortZuStiefo(w) for w in "Ruhe Wehe wiehern stehen Höhe gehören daher hohen".split()]
    ['r u h e', 'w e h e', 'w i h e r n', 'st e h e n', 'h ö h e', 'g e h ö r e n', 'd a h e r', 'h o h e n']
    >>> [wortZuStiefo(w) for w in "Hexe quälen".split()]
    ['h e x e', 'q ä l e n']
    >>> wortZuStiefo("nach'teil")
    'n a ch t ei l'
    >>> [wortZuStiefo(w) for w in "Angebot An'gebot Anlage an'treffen aus'treten Ausgang".split()]
    ['a ng e b o t', 'an g e b o t', 'an l a g e', 'an t r e f e n', 'aus t r e t e n', 'aus g a ng']

    # Test für Grundschrift: >>> [wortZuStiefo(w) for w in "Hexe quälen".split()]
    # ['h e ks e', 'kw ä l e n']
    """
    # alles Kleinbuchstaben, gleich von Anfang an.
    s = w.lower()
    # ein 'h' zwischen zwei Vokalen soll behalten werden. Temporär in ein 'H' umwandeln.
    s = re.sub(r"([aeiouöüä])h([aeiouöüä])", r"\1H\2", s)
    # Die Regeln der Reihe nach anwenden.
    for a, b in regeln:
        #s = s.replace(a,b)
        s = re.sub(a, b, s)
    # Zwei aufeinanderfolgende Vokale mit dem Vokalzeichen 'c' trennen.
    while True:
        s2 = re.sub(r"([aeiouöüäOEU])([aeiouöüäOEU])", r"\1c\2", s)
        if s2 == s:
            break
        s = s2

    v = {'1': 'mit',
         '2': 'er',
         '3': 'an',
         '4': 'vor',
         '5': 'zu',
         '6': 'ein',
         '7': 'aus',
         'Z': 'sch',
         'C': 'ch',
         'D': 'nd',
         'G': 'ng',
         'X': 'cht',
         'S': 'st',
         'P': 'sp',
         'F': 'pf',
         'E': 'ei',
         'O': 'eu',
         'N': 'nt',
         'K': 'nk',
         'U': 'au',
         #'x': 'k s',  #Grundschrift
         #'q': 'k w',
    }
    s = s.replace('c', '')  # Vokalzeichen, entfernen falls explizit vorhanden
    return ' '.join(((v[x] if x in v else x) for x in s))


def convert_text(text, wordlists):
    """
    Converts a text into Stiefocode.
    :param text: the text to convert
    :param wordlists: a list of dictionaries with known words
    :return: a tuple (stiefo_text, unknown_words)
    """
    pct = {
        '.': ['.', 'spc2'],  # FIXME: Punkt jetzt .., Abstand in render.py
        ',': [',', 'spc2'],  # FIXME: Abstand jetzt in render.py
        '<br>': '§',

        '!': ['~!', 'spc2'],
        '?': ['~?', 'spc2'],
        ':': ['~:', 'spc2'],
        ';': ['~;', 'spc2'],

        '!,': ['~!', ',', 'spc2'],
        '?,': ['~?', ',', 'spc2'],
    }

    quotes = ['"', "'", '«', '‹', '<', '>', '›', '»']
    for ch in quotes:
        pct['.'+ch] = ['.', '~'+ch, 'spc2']
        pct[','+ch] = ['~'+ch, ',', 'spc2']
        pct[ch+','] = ['~'+ch, ',', 'spc2']
        pct['?'+ch+','] = ['~?'+ch, ',', 'spc2']
        pct['!'+ch+','] = ['~!'+ch, ',', 'spc2']
        pct['!'+ch] = ['~!'+ch, 'spc2']
        pct['?'+ch] = ['~?'+ch, 'spc2']

    unknown = {}
    wordlists = [pct] + wordlists + [unknown]

    def check_dicts(w):
        wl = w.lower()
        for l in wordlists:
            if w in l:
                return l[w]
            if wl in l:
                return l[wl]
        return None

    def append_or_extend(lst, x):
        if isinstance(x, str):
            lst.append(x)
        else:
            lst.extend(x)


    def convert_blk(blk):
        text = blk.replace('\n', ' <br> ')  # Zeilenenden erhalten
        res = []
        # first split into words by spaces.
        words = [x for x in re.split(r"\s+", text) if x]
        for w in words:
            # if the words are found in the dict, use that
            x = check_dicts(w)
            if x:
                append_or_extend(res, x)
            else:
                # otherwise check if there is punctuation and separate that out
                p = [x for x in re.split(r'(\w[\w\']*\w|\w)', w) if x]
                # then check again with the dict
                fst = True
                for w1 in p:
                    x = check_dicts(w1)
                    if x:
                        append_or_extend(res, x)
                    elif w1[0].isalpha():
                        w1 = w1.replace("'", "")
                        x = check_dicts(w1)
                        if x:
                            append_or_extend(res, x)
                        else:
                            # use the default rules and put into unknown if not found
                            w1 = w1.lower()
                            st = wortZuStiefo(w1)
                            unknown[w1] = st
                            res.append(st)
                    else:
                        if fst:
                            res.append('~~' + w1)
                        else:
                            res.append('~' + w1)
                    fst = False

        return res

    # UTF-8 Kennung entfernen, falls vorhanden
    if text.startswith('\ufeff'):
        text = text[1:]

    # text aufteilen in Blöcke
    blocks = re.split(r'(\{!.*?!\}|\{".*?"\})', text, 0, re.DOTALL)
    words = []
    for blk in blocks:
        if blk.startswith('{"'):
            # langtext literal
            words.append('~' + blk[2:-2])
        elif blk.startswith('{!'):
            # stiefo literal
            st = blk[2:-2].strip()
            flg = False
            for ln in st.split('\n'):
                if flg:
                    words.append('§')
                words.extend(re.split('\s\s+', ln))
                flg = True
        else:
            words.extend(convert_blk(blk))
            # zu konvertierender Text

    return words, unknown


def list_to_text(l):
    lines = []
    line = ""
    for w in l:
        if len(line) + 2 + len(w) > 80:
            lines.append(line)
            line = ""
        if line:
            line += " \u00A0 "
        line += w
        if w == "§":
            lines.append(line)
            line = ""
    if line:
        lines.append(line)
    return "\n".join(lines)


def text_to_list(txt):
    return re.split(' \u00A0 |\n|  +', txt)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
