import os
import stiefo


filenamebase = "Schildbuerger"

wlist = stiefo.wordlist()

wlist.load("Wortlisten/wortliste.txt")
if os.path.isfile(filenamebase + '.wrd'):
    wlist.load(filenamebase + '.wrd')

with open(filenamebase + '.txt', "r", encoding="utf-8") as f:
    text = f.read()


stiefoWords, unknown = stiefo.convert_text(text, [wlist])
unk = stiefo.wordlist(unknown)
unk.save(filenamebase + '.unk')

print(unknown)

st = stiefo.list_to_text(stiefoWords)
with open(filenamebase + '.sti', "w", encoding="utf-8") as f:
    f.write(st)

stiefo.render_pdf(stiefoWords, filenamebase + ".pdf")
