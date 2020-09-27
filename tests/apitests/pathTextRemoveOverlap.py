size(200, 100)

t = "المتحدة"
p = BezierPath()
p.text(t, (187, 20), font="../fonts/IBMPlexSansArabic-Regular.otf", fontSize=70, align="right")

stroke(0)
fill(None)
p.removeOverlap()
drawPath(p)
