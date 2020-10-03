size(600, 500)

fill(1)
rect(0, 0, width(), height())
fill(0)
font("../fonts/IBMPlexSansArabic-Regular.otf")
fontSize(100)
openTypeFeatures(ss01=True, ss02=True, ss03=True)
openTypeFeatures(resetFeatures=True, ss03=True)
text("Aag0", (50, 50))
w, h = textSize("Aag0")
text("---", (50 + w, 50))

openTypeFeatures(resetFeatures=True)
fontSize(60)
s = "بلديهما abcde المتحدة"
text(s, (width() - 50, 150))

text("Alfabet", (width() / 2, 220))
text("البشريةً", (width() / 2, 290))

font("Helvetica")  # simply test loading an installed font
