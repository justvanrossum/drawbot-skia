size(200, 200)

path = BezierPath()
path.moveTo((100, 100))
path.arc((100, 100), 80, 230, 170, False)
path.arc((100, 100), 60, 30, 120, True)
path.closePath()

stroke(0)
fill(None)
strokeWidth(4)
drawPath(path)

# arc(center, radius, startAngle, endAngle, clockwise)
# Arc with center and a given radius, from startAngle to endAngle, going clockwise if clockwise is True and counter clockwise if clockwise is False.

# arcTo(point1, point2, radius)
# Arc defined by a circle inscribed inside the angle specified by three points: the current point, point1, and point2. The arc is drawn between the two points of the circle that are tangent to the two legs of the angle.
