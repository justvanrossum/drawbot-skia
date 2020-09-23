from fontTools.misc.transform import Transform


size(200, 200)


with savedState():
    rotate(15, center=(50, 50))
    rect(25, 25, 50, 50)


with savedState():
    scale(1.2, center=(150, 50))
    rect(125, 25, 50, 50)


with savedState():
    skew(15, 10, center=(50, 150))
    rect(25, 125, 50, 50)


with savedState():
    t = Transform()
    t = t.scale(0.9, 1.1)
    t = t.rotate(0.2)
    transform(t, center=(150, 150))
    rect(125, 125, 50, 50)
