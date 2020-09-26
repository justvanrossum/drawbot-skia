import math
import skia
from fontTools.misc.transform import Transform
from fontTools.pens.basePen import BasePen


# TODO:
# - drawToPen
# - drawToPointPen
# - text
# - textBox
# - removeOverlap
# - difference
# - intersection
# - union
# - xor
# MAYBE:
# - contours
# - expandStroke
# - intersectionPoints
# - offCurvePoints
# - onCurvePoints
# - optimizePath
# - points
# - svgClass
# - svgID
# - svgLink
# - traceImage


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

    def arc(self, center, radius, startAngle, endAngle, clockwise):
        cx, cy = center
        diameter = radius * 2
        rect = (cx - radius, cy - radius, diameter, diameter)
        sweepAngle = (endAngle - startAngle) % 360
        if clockwise:
            sweepAngle -= 360
        self.path.arcTo(rect, startAngle, sweepAngle, False)

    def arcTo(self, point1, point2, radius):
        self.path.arcTo(point1, point2, radius)

    def rect(self, x, y, w, h):
        self.path.addRect((x, y, w, h))

    def oval(self, x, y, w, h):
        self.path.addOval((x, y, w, h))

    def polygon(self, firstPoint, *points, close=True):
        self.path.addPoly((firstPoint,) + points, close)

    def pointInside(self, point):
        x, y = point
        return self.path.contains(x, y)

    def bounds(self):
        if self.path.countVerbs() == 0:
            return None
        return tuple(self.path.computeTightBounds())

    def controlPointBounds(self):
        if self.path.countVerbs() == 0:
            return None
        return tuple(self.path.getBounds())

    def reverse(self):
        path = skia.Path()
        path.reverseAddPath(self.path)
        self.path = path

    def appendPath(self, other):
        self.path.addPath(other.path)

    def copy(self):
        path = skia.Path(self.path)
        return BezierPath(path=path)

    def translate(self, x, y):
        self.path.offset(x, y)

    def scale(self, x, y=None, center=(0, 0)):
        if y is None:
            y = x
        self.transform((x, 0, 0, y, 0, 0), center=center)

    def rotate(self, angle, center=(0, 0)):
        t = Transform()
        t = t.rotate(math.radians(angle))
        self.transform(t, center=center)

    def skew(self, x, y=0, center=(0, 0)):
        t = Transform()
        t = t.skew(math.radians(x), math.radians(y))
        self.transform(t, center=center)

    def transform(self, transform, center=(0, 0)):
        cx, cy = center
        t = Transform()
        t = t.translate(cx, cy)
        t = t.transform(transform)
        t = t.translate(-cx, -cy)
        matrix = skia.Matrix()
        matrix.setAffine(t)
        self.path.transform(matrix)
