import os
import stiefo


filenamebase = "praefix-test"

wlist = stiefo.wordlist()

#wlist.load("Wortlisten/wortliste-aufbauschrift-1.txt")
if os.path.isfile(filenamebase + '.wrd'):
    wlist.load(filenamebase + '.wrd')

with open(filenamebase + '.txt', "r", encoding="utf-8") as f:
    text = f.read()

stiefo_words, unknown = stiefo.convert_text(text, [wlist])
unk = stiefo.wordlist(unknown)
unk.save(filenamebase + '.unk')

print(unknown)

stiefo_code = stiefo.list_to_text(stiefo_words)
with open(filenamebase + '.sti', "w", encoding="utf-8") as f:
    f.write(stiefo_code)

stiefo.render_pdf(stiefo_words, filenamebase + ".pdf")
