import skia
from fontTools.pens.basePen import BasePen


class BezierPath(BasePen):

    def __init__(self, path=None, glyphSet=None):
        super().__init__(glyphSet)
        if path is None:
            path = skia.Path()
        self.path = path

    def _moveTo(self, pt):
        self.path.moveTo(*pt)

    def _lineTo(self, pt):
        self.path.lineTo(*pt)

    def _curveToOne(self, pt1, pt2, pt3):
        x1, y1 = pt1
        x2, y2 = pt2
        x3, y3 = pt3
        self.path.cubicTo(x1, y1, x2, y2, x3, y3)

    def _qCurveToOne(self, pt1, pt2):
        x1, y1 = pt1
        x2, y2 = pt2
        self.path.quadTo(x1, y1, x2, y2)

    def _closePath(self):
        self.path.close()

    def _endPath(self):
        pass

    def rect(self, x, y, w, h):
        self.path.addRect((x, y, w, h))

    def oval(self, x, y, w, h):
        self.path.addOval((x, y, w, h))

    def polygon(self, firstPoint, *points, close=True):
        self.moveTo(firstPoint)
        for point in points:
            self.lineTo(point)
        if close:
            self.closePath()
