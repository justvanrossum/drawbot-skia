size(200, 200)

bez = BezierPath()
bez.moveTo((20, 20))
bez.lineTo((20, 100))
bez.lineTo((100, 100))
bez.lineTo((100, 180))
bez.curveTo((150, 180), (180, 150), (180, 100))
bez.lineTo((180, 50))
bez.qCurveTo((180, 20), (150, 20))

fill(1, 0, 0)
stroke(0)
strokeWidth(10)
drawPath(bez)

bez.closePath()

fill(None)
stroke(1)
translate(40, 15)
scale(0.7)
lineCap("round")
lineJoin("round")

drawPath(bez)
