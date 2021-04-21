# stiefogen – ein Stiefo-Generator

Python-Programm, das mithilfe von PyQt5 Textdateien in
Stiefo-Grundschrift (Aufbauschrift noch experimentell) als PDF oder auf dem Bildschirm übersetzt.

Entwickelt von Andreas Hofer, mit Beiträgen von [Andreas Martin](https://github.com/AndreasMartin72) und [Florian Jenn](https://github.com/effjot)

Hinweis: Wer nur an der Grundschrift interessiert ist, bitte den
Branch `grundschrift` verfolgen, dort wird zur Zeit auch die
Dokumentation überarbeitet.  Im Branch `aufbauschrift-2` wird die
Umsetzung der Aufbauschrift 2 verbessert, ist aber noch nicht
abgeschlossen.


## Kurze Anleitung

Benötigt: Python3 und PyQt5

Das Programm bietet 2 Modi:

 * `stiefo.render_screen(words)`: Bildschirmausgabe in einem interakiven Fenster,
   in dem man Text eingeben und die Kurven und Stützpunkte sehen kann. `words`
   ist eine Liste von Strings. Jeder String ist ein Wort, in dem die einzelnen
   Buchstaben durch Leerzeichen getrennt sind (Stiefocode): `["ei n", "t e st"]`.
   Beispieldatei: `render_on_screen.py`

 * `stiefo.render_pdf(words, filename, papersize)`: Ausgabe als PDF.
   Beispieldatei (einschließlich Aufbereitung der Klartext-Datei): `schildbuerger.py`

Die Aufbereitung von „normalen“ Textdateien („Klartext“) wird von den
Funktionen in `parse.py` erledigt (siehe Beispiel in
`schildbuerger.py`), wobei zur Unterstützung der korrekten Aufrennung
der Worte in Stiefo-Buchstaben eine Wortliste genutzt werden kann. Die
unbekannten Wörter werden als Ergebnis mit zurückgegeben und sollten
überprüft und ggf. in die Wortliste eingebaut werden.


## nächste Ziele

 * Dokumentation verbessern/erweitern
 * Aufbauschrift überarbeiten
 * Ausgabe als SVG
 * Parser/Lexer für Stiefocode


## Aufbau des Programms

`parse.py`, `wordlist.py`: Eingabetext in „Stiefo-Wörter“ zerlegen
(Stiefo-Wort = Stiefo-Buchstaben, getrennt durch
Leerzeichen). Umwandlung zwischen String- und Listenformat für
Ein/Ausgabe in Datein.

`symbols.py`: Stiefo-Wort in Bezier-Kurven umwandeln. Konsonanten (und Konsonantenverindungen wie z. B. ST, NG) werden mit „Glyphen“ (Funktionen, die die Bezierpunkte liefern) dargestellt, Vokale direkt als Linien mit entsprechender Länge und Höhenversatz. Ergebnis ist ein Tupel `(Wortbreite, Liste_von_Bezierpunkten, Grenzen_der_Konsonanten)`.

`render.py`: Kurven (aus „Stiefo-Wörtern“) mit QT5 am Bildschirm oder in PDF zeichnen.


# stiefogen – a Stiefo shorthand generator

Python program that uses PyQt5 to transcribe plain text into Stiefo
Grundschrift (as PDF or on screen).

Developed by Andreas Hofer, with additions by Andreas Martin [Andreas Martin](https://github.com/AndreasMartin72) and [Florian Jenn](https://github.com/effjot)

Please note: if you are only interested in “Grundschrift” (basic
level), please have a look at branch `grundschrift`, where
documentation is currently being improved.  Branch `aufbauschrift-2`
is a rework/update of “Aufbauschrift 2” (advanced level 2), but not
yet finished.

