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
Bedarf implementiert werden, z.B. durch nachgestelltes `=`)

(TODO: Markierung vor Großschreibung durch Strich darunter könnte bei
Bedarf implementiert werden, z.B. durch nachgestelltes `_`)

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
* `i0` für etwas engere Verbindung; wird bei `ch` automatisch gesetzt;
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
* `@h`, `@h^` Schleifen gegen UZS für Nachsilbe „-heit“; Kombination mit Vokal `ei`.
   FIXME: ist intern eine häßliche und unpraktische Lösung, ähnlich wie waagr. Anstrich `-`.
   → Bearbeitung Glyphen und Vokale muss überarbeitet werden.


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

(FIXME: nachgestellte Symbole oder Versatz mit Dezimalzahl wären wohl
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

* `dd` = „breites D“ (oder oben offener weiter Bogen) = _durch_
* `nn` = „breites N“ (oder unten offener weiter Bogen) = _uns_
* `rr` = „breites R“ (weite Welle) = _nur_
* `mm` = „breites M“ (nach links vorgezogener Anstrich) = _muss_


Mit nachgestelltem `*` erhält man Schreibvarianten von einigen
Konsonantzeichen:

* `h*`, `m*`, `s*`: betonte Fußschleife, z.B. für _Herr_, _mehr_, _sicher_
* `mm*` = breites M mit betonter Fußschleife = _musst_
* `w*`, `w*4`: W mit eingerolltem Fuß (in „offizieller“ Aufbauschrift
  nur `w*4` = _während_)
* `w**4` = _-wärts_ (unten spitze Variante des 2-stufigen W)
* `r*` = „flaches R“ (Tilde) = _ungefähr_
* `d*` = d mit schmaler Verbindung, wird nur intern verwendet für
  Kürzel _dich_
* `h^` = etwas steileres, weniger weit nach links auslaufendes H, damit
  in Kombinationen wie `3d h` (_daher_) der Fuß des H nicht in den
  Aufstrich läuft


Verbesserte Darstellung von Zeichen mit E-Anstrich:

* `en` = N mit Anstrich = schmaler Bogen für _den_, _nicht_, _man_
  (Anstrich ist etwas kürzer als normales E, damit der Bogen
  halbkreisförmig wird)
* `ent` = halbstufiges ND mit Anstrich für _ent-_ (Anstrich ist etwas
  kürzer als normales E)


### Symbole für Vokale und Vorsilben

Die normalen Vokale werden um Varianten mit angepasstem Abstand für
bestimmte Situationen ergänzt:

* `a0` schmaler/steiler, für Nachsilben _-schaft_, _-bar_, _-fach_,
  _-haft_
* `A` breiter/flacher, z.B. für _mittelbar_
* `e0` schmaler, für _aber_, _über_, Vorsilben _er_/_mit_/_an_
* `e@` sehr schmale Verbindung, um Punktschleife (_-lich_) anzuhängen
* `/`, `//` sind technisch zwar Vokale, dienen aber zur Darstellung von
  Vorsilben mit Aufstrich, s.u.

Zur sauberen Darstellung bestimmter Verbindungen kann mit `|` eine
beliebig weite Verbindung eingefügt werden. Die Weite wird durch eine
direkt an `|` anschließende Zahl (mit Dezimal_punkt_) angegeben.  Ohne
Zahl wird ein E-Abstand verwendet.  Beispiele: `j |0 1dd` = _jedoch_,
`4dd |0.1 nd` = _Deutschland_.


Es gibt drei Arten von durch Anstriche dergestellen Vorsilben:

* `_` = normaler Anstrich: beginnt auf Linie (Höhe Fußpunkt folgender
  Konsonant), steigt zum Kopf des Konsonanten an
* `-` = waagerechter Anstrich: beginnt auf Höhe Kopf des folgenden
  Konsonanten, verläuft waagerecht zum Kopf des Konsonanten
* `/` = Aufstrich, beginnt 1 Stufe unterhalb der Linie, für _auf_,
  _be-_, _un-_; darf auch im Wort verwendet werden

Durch Verdoppelung erhält man die weiten Varianten.

Die Höhe _muss_ durch eine vorangestellte Zahl angegeben werden.  Die
Skala ist die gleiche wie beim vertikalen Versatz von Konsonanten.

Beispiele:

* `2__ g e b` = _zugeben_
* `1- p o t` = _Import_
* `0//` = _auf_
* `0d /` = _un-_


### Durchstreichungen

Einige Nachsilben werden mit Durchstreichung dargestellt.  Dazu können
beliebige Stiefocodes (außer weitere Durchstreichung) in geschweifte
Klammern gesetzt werden, um die Durchstreichung zu schreiben:

* `m {a}` = mehrfach
* `e {a s} b` = ebenfalls
* `g au {a0} b` = glaubhaft

Der Stiefogenerator erkennt, ob ein Vokal oder Konsonant vorausgeht
und setzt Durchstreichungen von Vokalen in die Mitte der Verbindung
und Durchstreichungen von Konsonanten auf den Konsonanten.  Oft ist
es aber notwendig, die Position auf die jeweiligen Buchstaben
abzustimmen.  Dazu in runden Klammern den x- und y-Versatz (mit
Dezimal_punkt_) getrennt durch Komma (keine Leerzeichen) angeben:

* `l e b {a}(-0.4,0)` = lebhaft
* `p ü f {a r keit}(-0.25,0)` = prüfbar

Durchstreichungen lassen sich auch für Punktierungen (Unterscheidung
e/ä, u/au in der Grundschrift) und Unter-/Überstreichungen verwenden:

* `h au {--2.} s` = Haus (AU mit Punkt gekennzeichnet)
* `r a nk {+4-} e n` = ranken (NK durch Überstreichung gekennzeichnet)


### Vordefinierte Kürzel-Codes

Damit man nicht immer die zum Teil recht unübersichtlichen Stiefocodes
schreiben muss, sind die gängigen, in den Stiefomaterialen vorgestellten
Kürzel in symbol.py als Codes definiert.

Beispiele für Vorsilben:

* `zu` = `2__`
* `mit` = `1_`
* `aus` = `2--`
* `ver` = `2@0`
* `über` = `1b`
* `voll` = `2-- @^*00 i`

Beispiele für Nachsilben:

* `ung` = `u`
* `ig` = `I`
* `igkeit` = `ei`
* `schaft` = `a0`
* `lich` = `e0 @*0`
* `los` = `|0.25 @^*00`
* `schaftlich` = `|0.25 ++3@*0`

Beispiele für Kürzel, die für ganze Wörter bzw. Wortstämme stehen:

* `hab` = `3h`
* `gehab` = `3- h`
* `muss` = `mm`
* `müsst` = `1mm*`
* `oder` = `1rr`
* `sonst` = `1@2`
* `als` = `-4-` (waagr. Strich in A-Position, etwas tiefer gesetzt)

Durchstreichungen brauchen oft einen fein abgestimmten Versatz, der
nicht automatisch errechnet werden kann.  Darum sind hier viele Wörter
vorformuliert, z.B.: 

* `einfach` = `ein {a0}(0,-0.25)`
* `bar` = `{a0 r}(-0.5,0)`
* `dankbar` = `3ng {a r}(0.5,0)`
* `unmittelbar` = `un 1l {|1.3 +3r}(-0.15,-0.25)` (das A beginnt etwas
  tiefer, damit man die Durchstreichung besser erkennen kann)



## Texte in Stiefocode

Stiefocode für einzelne Wörter kann zu Texten kombiniert werden,
indem man sie mit mind. 2 Leerzeichen oder geschützte Leerzeichen
(non-break-space, Unicode 0x00a0) voneinander trennt.


### wörtliche Texte in Langschrift

Mit `~` können beliebige Texte in Langschrift eingefügt werden.
Das Ende des Texts wird durch doppeltes Leerzeichen markiert.
Beispiel:

    ~Ein Text der in Langschrift („normale“ Schriftart) erscheint
    ei n   st ei n   ~ein Stein   d i   n a cht   ~die Nacht


### horizontale Abstände, Zeilen- und Seitenumbruch

Bei der Ausgabe wird zwischen die einzelnen Wörter ein halbweiter
Abstand (entspricht Breite des Vokals e) gesetzt.

Für zusätzliche Abstände gibt es die Befehle

* `spc1`: ungefähr 10 halbweite Abstände
* `spc2`: ungefähr 5 halbweite Abstände (FIXME: andersrum wäre logischer)
* `&`: Wortabstand verringern, wenn Wörter zerlegt geschrieben werden.
       Kann auch wiederholt werden für engeren Abstand.
       Bsp.: `l i nk  &  &  h e nd e r` (Linkshänder)


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
