import stiefo

filenamebase = "Aufbauschrift2_Text17"

with open(filenamebase + '.txt', "r", encoding="utf-8") as f:
    text = f.read()

st = stiefo.text_to_list(text)

stiefo.render_pdf(st, filenamebase + ".pdf")
