size(200, 200)

bez = BezierPath()
bez.rect(10, 10, 30, 40)
bez.oval(100, 10, 30, 40)
bez.polygon((10, 100), (10, 180), (40, 180), (40, 110))
bez.polygon((110, 100), (110, 180), (140, 180), (140, 110), close=False)
bez.line((80, 100), (75, 180))

fill(1, 0.5, 0)
stroke(0)
strokeWidth(2)

drawPath(bez)
