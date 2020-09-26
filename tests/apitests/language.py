size(600, 120)

proofText = 'вгджзийклнпттттфцчшщъьюѝ'
font('../fonts/SourceSerifPro-Regular.otf')
fontSize(34)

w, _ = textSize(proofText)
assert round(w, 1) == 498.0
text(proofText, (12, 74))

language("bg")
w, _ = textSize(proofText)
assert round(w, 1) == 537.7
text(proofText, (12, 33))
