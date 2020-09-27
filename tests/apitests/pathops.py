
path1 = BezierPath()
path1.rect(25, 25, 100, 100)
path2 = BezierPath()
path2.oval(75, 75, 100, 100)

operations = [
    (path1, path2, "union"),
    (path1, path2, "intersection"),
    (path1, path2, "difference"),
    (path2, path1, "difference"),
    (path1, path2, "xor"),
]

size(200, 200 * (len(operations) + 1))
fill(1)
rect(0, 0, width(), height())

stroke(0)
strokeWidth(4)
fill(0.9)

for path1, path2, op in operations:
    path = getattr(path1, op)(path2)
    drawPath(path)
    translate(0, 200)

path = path1.copy()
path.appendPath(path2)
path.removeOverlap()
drawPath(path)
