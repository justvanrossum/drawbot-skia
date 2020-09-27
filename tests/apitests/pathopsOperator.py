import operator

path1 = BezierPath()
path1.rect(25, 25, 100, 100)
path2 = BezierPath()
path2.oval(75, 75, 100, 100)

operations = [
    (path1, path2, operator.or_),
    (path1, path2, operator.and_),
    (path1, path2, operator.mod),
    (path2, path1, operator.mod),
    (path1, path2, operator.xor),
]

size(200, 200 * len(operations))
fill(1)
rect(0, 0, width(), height())

stroke(0)
strokeWidth(4)
fill(0.9)

for path1, path2, op in operations:
    path = op(path1, path2)
    drawPath(path)
    translate(0, 200)
