size(250, 680)

fill(1)
rect(0, 0, width(), height())

font("../fonts/Nabla.subset.ttf")

fs = 120
steps = 5
fontSize(fs)
for i in range(steps):
    t = i / (steps - 1)
    wght = 100 + 600 * t
    HLGT = t * 10
    fontVariations(wght=wght, HLGT=HLGT)
    text("ABC", (20, 20))
    translate(0, 1.1 * fs)
