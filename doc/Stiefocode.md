# Stiefocode

Mit dem Stiefocode wird die Schreibweise von Wörtern in Stiefo mit
ASCII-Zeichen festgehalten.  Aus dem Stiefocode erzeugt der
Stiefo-Generator dann die Stiefo-Schriftzüge als Bezierkurven.

Die einzelnen Buchstaben eines Wortes werden in Stiefocode durch ein
Leerzeichen getrennt.  Damit können Einzelkonsonanten/Einzelvokale und
Konsonantengruppen/Dipthonge voneinander unterschieden werden.

Stiefocode unterscheidet Groß- und Kleinschreibung.  Die gängigsten
Codes sind alle klein geschrieben.


## Buchstaben der Grundschrift

### Konsonanten

* `ch`
* `cht`
* `b`
* `d`
* `f`
* `g`
* `h`
* `j`
* `k`
* `l`
* `m`
* `n`
* `nd` = `nt` (werden identisch wiedergegeben; keine Kennzeichnung durch
  Strich darüber)
* `ng` = `nk`
* `p`
* `pf`
* `r`
* `s`
* `sch`
* `sp`
* `st`
* `t`
* `w`
* `z`

(TODO: Unterscheidung nd/nt, f/v usw. durch Strich darüber könnte bei
Bedarf implementiert werden)


### Vokale

* `a`
* `e` = `ä` (werden identisch wiedergegeben; keine Kennzeichnung durch
  `Punkt` darunter)
* `i` = `ü` (FIXME: `y` als Synonym einrichten)
* `o`
* `ö`
* `u` = `au`
* `ei` = `ai`
* `eu` = `oi` (FIXME: `äu` als Synonym einrichten)

(TODO: Unterscheidung e/ä usw. durch Punkt darunter könnte bei Bedarf
implementiert werden.)

Das Vokaltrennzeichen, z.B. für „Bauer“, kann als `c` geschrieben
werden (z.B. `b au c e r`), ist aber im Normalfall nicht nötig, weil
der Generator die Vokaltrennung anhand der Leerzeichen erkennt.  Der
Code `c` kann verwendet werden, wenn man das Vokaltrennzeichen für
sich alleine zeigen will.


Vokal-Varianten:

* `I` für etwas weitere Verbindung; wird vor `b`, `f`, `k`, `m`, `p`,
  `r`, `z`, `cht`, `ng`, `nk`, `st` sowie am Wortanfang und Wortende
  automatisch gesetzt; kann bei bestimmten Verbindungen mit `nd`
  (z.B. Wind, Kind) sinnvoll sein
* `ii` für etwas engere Verbindung; wird bei `ch` automatisch gesetzt;
  kann auch bei `sp` ggf. sinnvoll sein


### Beispiele für Wörter in Grundschrift

* `b e t` = Bett
* `st ei n` = Stein
* `k I nd` = Kind (etwas weitere Verbindung als normales `i`,
  sieht „runder“ aus)
* `s i nd` = sind (normale Verbindung)
* `u nd` = und
* `u n d a nk` = Undank (Trennung von `n` und `d`!)
* `n a cht` = Nacht
* `n a ch t ei l` = Nachteil (Trennung von `ch` und `t`!)


## Texte in Stiefocode

Stiefocode für einzelne Wörter kann zu Texten kombiniert werden,
indem man sie mit mind. 2 Leerzeichen oder geschützte Leerzeichen
(non-break-space, Unicode 0x00a0) voneinander trennt.


### wörtliche Texte in Langschrift

Mit `~` können beliebige Texte in Langschrift eingefügt werden.
Beispiel:

    ~Ein Text der in Langschrift („normale“ Schriftart) erscheint
    ei n   st ei n   ~ein Stein   d i   n a cht   ~die Nacht


### horizontale Abstände, Zeilen- und Seitenumbruch

Bei der Ausgabe wird zwischen die einzelnen Wörter ein halbweiter
Abstand (entspricht Breite des Vokals e) gesetzt.

Für zusätzliche Abstände gibt es die Befehle

* `spc1`: ungefähr 10 halbweite Abstände
* `spc2`: ungefähr 5 halbweite Abstände

FIXME: andersrum wäre logischer

Ein neue Zeile kann mit `§` erzwungen werden, eine neue Seite mit `§§`.


Kurze wörtliche Texte mit `~` werden beim automatischen Zeilenumbruch
nicht vom vorhergehenden Wort getrennt.  Dies wird hauptsächlich für
Satzzeichen genutzt, die nicht allein in die nächste Zeile gesetzt
werden sollen (s.u.).  Mit der Variante `~~` werden kürzere Texte beim
Zeilenumbruch nicht vom nächsten Wort getrennt.  Dies wird für
öffnende Anführungszeichen genutzt.  Bei längeren Texten gelten diese
Einschränkungen nicht.  „Länger“ sind Texte über 100 Pixel (Variable
`short` in `print_renderer.prepare`).  FIXME: Stiefo-Einheiten wären
wahrscheinlich besser als Pixel.


### Interpunktion

Folgende Satzzeichen stehen als Codes zur Verfügung:

* `.` markiert Satzende durch ein Kreuzchen
* `,` keine grafische Darstellung

Ein Komma wird in Stiefo üblicherweise durch den `spc2`-Abstand
dargestellt. Der Parser für Klartext-Dateien übersetzt Kommas
entsprechend in den Stiefocode `,  spc2` und Punkte in `.  spc2`.

Hinweis: Die Stiefo-Materialien stellen den Punkt durch den
längeren `spc1`-Abstand dar.

FIXME: Symboldarstellung und Abstände sollten konfigurierbar sein (in
symbols.py und render.py, nicht in parse.py).


Weitere Satzzeichen sind nicht Teil des Stiefocodes, sondern werden
vom Parser folgendermaßen in Stiefocode umgesetzt:

* ? → `~?  spc2`
* ! → `~!  spc2`
* : → `~:  spc2`
* ; → `~;  spc2`
* öffnendes Anführungszeichen („ » « › ‹ " ') → `~~„`
* schließendes Anführungszeichen (“ » « › ‹ " ') → `~“`
