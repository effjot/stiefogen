import os
import stiefo



filenamebase = "Das_getupfte_Band"

wlist = stiefo.wordlist()

wlist.load("WortListen/wortliste.txt")
if os.path.isfile(filenamebase+'.wrd'):
    wlist.load(filenamebase+'.wrd')

with open(filenamebase+'.txt', "r", encoding="utf-8") as f:
    text = f.read()



abk = stiefo.wordlist(
    {'Dr.': 'd r',
     'St.': 'st',
     'Mr.': 'm r',
     'Mrs.': 'm r s',
    }
)

stiefoWords, unknown = stiefo.convert_text(text, [abk, wlist])
unk = stiefo.wordlist(unknown)
unk.save(filenamebase + '.unk')

print(unknown)

st = stiefo.list_to_text(stiefoWords)
with open(filenamebase+'.sti', "w", encoding="utf-8") as f:
    f.write(st)

stiefo.render_pdf(stiefoWords, filenamebase + ".pdf")
