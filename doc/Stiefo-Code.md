# Stiefo-Code

Mit dem Stiefo-Code wird die Schreibweise von Wörtern in Stiefo mit
ASCII-Zeichen festgehalten.  Aus dem Stiefo-Code erzeugt der
Stiefo-Generator dann die Stiefo-Schriftzüge als Bezierkurven.

Die einzelnen Buchstaben eines Wortes werden in Stiefo-Code durch ein
Leerzeichen getrennt.  Damit können Einzelkonsonanten/Einzelvokale und
Konsonantengruppen/Dipthonge voneinander unterschieden werden.

Stiefo-Code unterscheidet Groß- und Kleinschreibung.  Die gängigsten
Codes sind alle klein geschrieben.


## Buchstaben der Grundschrift

Konsonanten:

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


Vokale:

* `a`
* `e` = `ä` (werden identisch wiedergegeben; keine Kennzeichnung durch
  `Punkt` darunter)
* `i` = `ü` (FIXME: `y` als Synonym einrichten)
* `o`
* `ö`
* `u` = au
* `ei` = ai
* `eu` = äu = oi

(TODO: Unterscheidung e/ä usw. durch Punkt darunter könnte bei Bedarf
implementiert werden.)

Das Vokaltrennzeichen, z.B. für „Bauer“, kann als `c` geschrieben
werden (`b au c e r`), ist aber nicht nötig, weil der Generator die
Vokaltrennung anhand der Leerzeichen erkennt.


Vokal-Varianten:

* `I` für etwas weitere Verbindung; wird nach `b`, `f`, `k`, `m`, `p`,
  `r`, `z`, `cht`, `ng`, `nk`, `st` sowie am Wortanfang und Wortende
  automatisch gesetzt
* `ii` für etwas engere Verbindung; wird bei `ch` automatisch gesetzt;
  kann auch bei `sp` ggf. sinnvoll sein


## Beispiele in Grundschrift

* `b e t` = Bett
* `u nd` = und
* `u n d a nk` = Undank (Trennung von `n` und `d`!)
* `st ei n` = Stein
