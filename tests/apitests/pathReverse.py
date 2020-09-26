size(200, 200)

path = BezierPath()
path.rect(50, 50, 100, 100)
path.reverse()
path.rect(75, 75, 50, 50)
drawPath(path)
