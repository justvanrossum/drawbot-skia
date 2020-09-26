size(200, 200)

path = BezierPath()
path.moveTo((20, 20))
path.arcTo((20, 180), (180, 180), 30)
path.arcTo((180, 180), (110, 20), 30)
path.lineTo((110, 20))

stroke(0)
strokeWidth(8)
fill(None)

drawPath(path)
