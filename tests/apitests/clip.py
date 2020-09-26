size(200, 400)

path = BezierPath()
path.polygon((80, 28), (50, 146), (146, 152), (172, 78))

with savedState():
    clipPath(path)
    scale(200/512)
    image("../images/drawbot.png", (0, 0))

translate(0, 200)

with savedState():
    scale(200/512)
    image("../images/drawbot.png", (0, 0))
