size(600, 120)

proof_text = 'вгджзийклнпттттфцчшщъьюѝ'

font('../fonts/SourceSerifPro-Regular.otf')
fontSize(34)
w, _ = textSize(proof_text)
assert round(w, 1) == 498.0
text(proof_text, (12, 74))
language("bg")
w, _ = textSize(proof_text)
assert round(w, 1) == 537.7
text(proof_text, (12, 33))
