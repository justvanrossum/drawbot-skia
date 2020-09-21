size(275, 400)

rect(0, 0, width(), height())
font("../fonts/MutatorSans.ttf")
fontSize(100)
fill(1)
text("ABCXYZ", (10, 15))
fontVariations(wght=600)
text("ABCXYZ", (10, 115))
variations = fontVariations(wdth=200)
assert {'wdth': 200, 'wght': 600.0} == variations, variations
text("ABCXYZ", (10, 215))
variations = fontVariations(wdth=1000, resetVariations=True)
assert {'wdth': 1000} == variations, variations
text("ABCXYZ", (10, 315))
