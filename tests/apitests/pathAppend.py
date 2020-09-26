size(200, 200)

path1 = BezierPath()
path1.rect(25, 25, 100, 100)
path2 = BezierPath()
path2.rect(75, 75, 100, 100)

path1.appendPath(path2)
drawPath(path1)

# help(path.appendPath)