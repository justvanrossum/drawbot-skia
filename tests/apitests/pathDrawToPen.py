from fontTools.pens.recordingPen import RecordingPen, RecordingPointPen

size(200, 200)
translate(10, 10)
scale(0.39)

path = BezierPath()
path.moveTo((100, 100))
path.curveTo((200, 100), (300, 200), (300, 300))
path.lineTo((100, 300))
path.closePath()
path.oval(0, 0, 200, 90)
path.moveTo((250, 250))
path.arc((250, 250), 200, 0, 120, False)
# path.skew() will trigger bad results
# https://github.com/justvanrossum/drawbot-skia/issues/7
# path.skew(10, 20)

fill(None)
stroke(0)
strokeWidth(2)
drawPath(path)

pen = RecordingPen()
path.drawToPen(pen)

path = BezierPath()
pen.replay(path)

stroke(None)
fill(0, 0.3)
drawPath(path)

ppen = RecordingPointPen()
path.drawToPointPen(ppen)
