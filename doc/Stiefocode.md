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

(TODO: Codes für die 3-stufigen frei wählbaren Kürzel? z.B. mit
Großbuchstaben für 3-stufige Version der ganzstufigen Konsonanten und
C+Symbol für 3-stufige Version der halbstufigen Konsonanten)


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


## Codierung der Aufbauschrift

### Konsonantensymbole

Folgende Symbole für Konsonanten und Kürzel kommen hinzu:

* `chen` (halbstufiges CH)
* `qu` (halbstufiges F)
* `schw` (halbstufiges SCH)
* `th` (halbstufiges H)
* `tsch` (halbstufiges ND)
* `x` (halbstufiges K)
* `zw` (halbstufiges Z)
* `.` Punkt
* `@` Schleife gegen Uhrzeigersinn (UZS)
* `@*` Schleife im Uhrzeigersinn (FIXME: besseres Codezeichen finden)

### vertikaler Versatz und Größe von Konsonantensymbolen

Konsonantensymbole können vertikal verschoben und in unterschiedlichen
Größen gezeichnet werden.  Dazu wird vor dem Konsonant eine Zahl für
den vertikale Versatz und nach dem Konsonant eine Zahl für die Größe
gesetzt.  Versatz und Größe werden in Halbstufen gezählt.  Um negative
Zahlen beim Versatz zur vermeiden, beginnt die Skala mit 0 für einen Versatz um 2
Halbstufen nach unten.  Folgende Versätze sind damit möglich:

* 0: ganze Stufe tiefer (z.B. Startpunkt der Vorsilben auf-, be-, un-)
* 1: halbe Stufe tiefer (i)
* 2: kein Versatz (e)
* 3: halbe Stufe höher (a)
* 4: ganze Stufe höher (ö)

Lässt man den Versatz weg, wird der Konsonant nicht vertikal
verschoben (Versatz = 2).

Der vertikale Versatz kann mit vorangestelltem `+` und `-`
feinjustiert werden (in Schritten von Achtelstufen: `y_smallstep` in
symbols.py):

* `--`: Viertelstufe tiefer
* `-`: Achtelstufe tiefer
* `+`: Achtelstufe höher
* `++`: Viertelstufe höher

(FIXME: nachgestellte Symbole oder Versatz mit Komma wären wohl
eleganter)


Gültige Größenangaben sind:

* 0 (bei Schleifen): Punktschleife
* 1: halbstufig
* 2: ganzstufig
* 3: 1,5-stufig (selten, Aufbauschrift-2-Kürzel für Büro, -rechn-)
* 4: zweistufig (Aufbauschrift-2-Kürzel)
* 6: dreistufig (vom Nutzer frei definierbare Kürzel; in den
  Studienmaterialien bereits am Ende der Grundschrift eingeführt)
  (TODO: noch nicht implementiert)

Lässt man die Größenangabe weg, wird die Normalgröße des Konsonanten
verwendet (2 für ganzstufige, 1 für halbstufige Zeichen).

Bei Punkten gibt es keine Größe.


Beispiele:

* `1t` = T in i-Position = ist
* `3t` = T in a-Position = hatte
* `k4` = 2-stufiges K in Grundstellung = klein
* `1k4` = 2-stufiges K in i-Position = rück
* `k1` = halbstufiges K = x
* `ei g m4` = Eigentum (2-stufiges M = -tum)
* `ei g 1m4 e r` = Eigentümer (2-stufiges M, halbe Stufe tiefer =
  -tüm)
* `.` = Punkt auf Grundlinie = der
* `+2.` = Punkt Viertelstufe über der Grundlinie = der, aber besser zu erkennen
* `@*0` = Punktschleife im UZS = endlich
* `1@0` = Punktschleife gegen UZS in i-Position = für
* `@1` = halbstufige Schleife gegen UZS auf Grundlinie = gegen
* `3@2` = ganzstufige Schleife gegen UZS in a-Position = statt


### Konsonant-Varianten

„Breite“ Varianten einiger Konsonanten werden durch Verdopplung
gekennzeichnet:

* `dd` = „breites D“ (oder oben offener weiter Bogen) = durch
* `nn` = „breites N“ (oder unten offener weiter Bogen) = uns
* `rr` = „breites R“ (weite Welle) = nur
* `mm` = „breites M“ (nach links vorgezogener Anstrich) = muss


Mit nachgestelltem `*` erhält man Schreibvarianten von einigen
Konsonantzeichen:

* `h*`, `m*`, `s*`: betonte Fußschleife, z.B. für Herr, mehr, sicher
  (FIXME: „h0“ vs „h*“ noch nicht zufriedenstellend gelöst)
* `mm*` = breites M mit betonter Fußschleife = musst
* `w*`, `w*4`: W mit eingerolltem Fuß (in „offizieller“ Aufbauschrift
  nur `w*4` = während)
* `w**4` = wärts (unten spitze Variante des 2-stufigen W)
* `r*` = „flaches R“ (Tilde) = ungefähr
* `d*` = d mit schmaler Verbindung, wird nur intern verwendet für
  Kürzel „dich“


Verbesserte Darstellung von Zeichen mit E-Anstrich:

* `en` = N mit Anstrich = schmaler Bogen für den, nicht, man (Anstrich
  ist etwas kürzer als normales E, damit der Bogen halbkreisförmig
  wird)
* `ent` = halbstufiges ND mit Anstrich für ent- (Anstrich ist etwas
  kürzer als normales E)


### Symbole für Vokale, Vor- und Nachsilben


### Durchstreichungen


### Beispiele für Wörter in Aufbauschrift


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

* `..` markiert Satzende durch ein Kreuzchen und `spc2`-Abstand
* `,` keine grafische Darstellung, `spc2`-Abstand einfügen

Hinweis: Die Stiefo-Materialien stellen den Punkt nur durch den
längeren `spc1`-Abstand dar.

FIXME: Symboldarstellung und Abstände sollten konfigurierbar sein (in
symbols.py und render.py)


Weitere Satzzeichen sind nicht Teil des Stiefocodes, sondern werden
vom Parser folgendermaßen in Stiefocode umgesetzt:

* ? → `~?  spc2`
* ! → `~!  spc2`
* : → `~:  spc2`
* ; → `~;  spc2`
* öffnendes Anführungszeichen („ » « › ‹ " ') → `~~„`
* schließendes Anführungszeichen (“ » « › ‹ " ') → `~“`
