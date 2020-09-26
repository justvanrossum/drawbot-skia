size(200, 200)

path = BezierPath()
path.oval(5, 5, 190, 190)

fill(1, 0.3, 0)
drawPath(path)

fill(0)

step = 10
r = 2
d = r * 2
for x in range(0, width() + step, step):
    for y in range(0, height() + step, step):
        if path.pointInside((x, y)):
            oval(x - r, y - r, d, d)
