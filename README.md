# stiefogen – ein Stiefo-Generator

Python-Programm, das mithilfe von PyQT5 Textdateien in
Stiefo-Grundschrift als PDF übersetzt.

Entwickelt von Andreas Hofer, mit Beiträgen von [Andreas Martin](https://github.com/AndreasMartin72) und [Florian Jenn](https://github.com/effjot)


## Kurze Anleitung

Benötigt: python3 und pyqt5

Das Programm bietet 2 Modi:

 * `stiefo.render_screen(words)`: Bildschirmausgabe in einem interakiven Fenster,
   in dem man Text eingeben und die Kurven und Stützpunkte sehen kann. `words`
   ist eine Liste von Strings. Jeder String ist ein Wort, in dem die einzelnen
   Buchstaben durch Leerzeichen getrennt sind: `["ei n", "t e st"]`.
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

 * Aufbauschrift
 * von PyQt4 auf PyQt5 umstellen
 * Ausgabe als SVG?


## Aufbau des Programms

`parse.py`, `wordlist.py`: Eingabetext in „Stiefo-Wörter“ zerlegen
(Stiefo-Wort = Stiefo-Buchstaben, getrennt durch
Leerzeichen). Umwandlung zwischen String- und Listenformat für
Ein/Ausgabe in Datein.

`symbols.py`: Stiefo-Wort in Bezier-Kurven umwandeln. Konsonanten (und Konsonantenverindungen wie z. B. ST, NG) werden mit „Glyphen“ (Funktionen, die die Bezierpunkte liefern) dargestellt, Vokale direkt als Linien mit entsprechender Länge und Höhenversatz. Ergebnis ist ein Tupel `(Wortbreite, Liste_von_Bezierpunkten, Grenzen_der_Konsonanten)`.

`render.py`: Kurven (aus „Stiefo-Wörtern“) mit QT5 am Bildschirm oder in PDF zeichnen.


# stiefogen – a Stiefo shorthand generator

Python program that uses PyQT5 to transcribe plain text into Stiefo Grundschrift (as PDF).

Developed by Andreas Hofer, with additions by Andreas Martin [Andreas Martin](https://github.com/AndreasMartin72) and [Florian Jenn](https://github.com/effjot)
