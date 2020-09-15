import contextlib
import math
import skia
from fontTools.pens.basePen import BasePen


class Drawbot:

    def __init__(self):
        self._stack = []
        self._gstate = GraphicsState()
        self._canvas = None

    @property
    def canvas(self):
        if self._canvas is None:
            self.size(1000, 1000)
        return self._canvas
    
    def size(self, width, height):
        self._surface = skia.Surface(width, height)
        self._canvas = self._surface.getCanvas()
        self._canvas.translate(0, height)
        self._canvas.scale(1, -1)

    def rect(self, x, y, w, h):
        self._drawItem(self.canvas.drawRect, (x, y, w, h))

    def oval(self, x, y, w, h):
        self._drawItem(self.canvas.drawOval, (x, y, w, h))

    def drawPath(self, path):
        self._drawItem(self.canvas.drawPath, path.path)

    def _drawItem(self, canvasMethod, item):
        if self._gstate.doFill:
            canvasMethod(item, self._gstate.fillColor)
        if self._gstate.doStroke:
            canvasMethod(item, self._gstate.strokeColor)

    def fill(self, *args):
        self._gstate.setFillColor(_colorArgs(args))

    def stroke(self, *args):
        self._gstate.setStrokeColor(_colorArgs(args))

    def strokeWidth(self, value):
        self._gstate.strokeColor.setStrokeWidth(value)

    def translate(self, x, y):
        self.canvas.translate(x, y)

    def rotate(self, angle, center=(0, 0)):
        cx, cy = center
        self.canvas.rotate(angle, cx, cy)

    def scale(self, sx, sy=None, center=(0, 0)):
        if sy is None:
            sy = sx
        cx, cy = center
        if cx != 0 or cy != 0:
            self.canvas.translate(cx, cy)
            self.canvas.scale(sx, sy)
            self.canvas.translate(-cx, -cy)
        else:
            self.canvas.scale(sx, sy)

    def skew(self, sx, sy=0, center=(0, 0)):
        cx, cy = center
        if cx != 0 or cy != 0:
            self.canvas.translate(cx, cy)
            self.canvas.skew(math.radians(sx), math.radians(sy))
            self.canvas.translate(-cx, -cy)
        else:
            self.canvas.skew(math.radians(sx), math.radians(sy))

    def transform(self, matrix):
        m = skia.Matrix()
        m.setAffine(matrix)
        self.canvas.concat(m)

    @contextlib.contextmanager
    def savedState(self):
        self._stack.append(self._gstate.copy())
        self.canvas.save()
        yield
        self.canvas.restore()
        self._gstate = self._stack.pop()

    def saveImage(self, fileName):
        assert fileName.endswith(".png")
        image = self._surface.makeImageSnapshot()
        image.save(fileName)


class Path(BasePen):

    def __init__(self, path=None, glyphSet=None):
        super().__init__(glyphSet)
        if path is None:
            path = skia.Path()
        self.path = path

    def _moveTo(self, xy):
        self.path.moveTo(*xy)

    def _lineTo(self, xy):
        self.path.lineTo(*xy)

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


class GraphicsState:

    def __init__(self):
        self.doFill = True
        self.doStroke = False
        self.fillColor = skia.Paint(
            Color=0xFF000000,
            AntiAlias=True,
            Style=skia.Paint.kFill_Style,
        )
        self.strokeColor = skia.Paint(
            Color=0xFF000000,
            AntiAlias=True,
            Style=skia.Paint.kStroke_Style,
        )

    def copy(self):
        result = GraphicsState()
        result.__dict__.update(self.__dict__)
        result.fillColor = _copyPaint(self.fillColor)
        result.strokeColor = _copyPaint(self.strokeColor)
        return result

    def setFillColor(self, color):
        if color is None:
            self.doFill = False
        else:
            self.doFill = True
            self.fillColor.setARGB(*color)

    def setStrokeColor(self, color):
        if color is None:
            self.doStroke = False
        else:
            self.doStroke = True
            self.strokeColor.setARGB(*color)


_paintProperties = [
    # kwarg              getter name
    ('Alpha',           'getAlpha'),
    ('AntiAlias',       'isAntiAlias'),
    ('BlendMode',       'getBlendMode'),
    ('Color',           'getColor'),
    ('ColorFilter',     'getColorFilter'),
    ('Dither',          'isDither'),
    ('FilterQuality',   'getFilterQuality'),
    ('ImageFilter',     'getImageFilter'),
    ('MaskFilter',      'getMaskFilter'),
    ('PathEffect',      'getPathEffect'),
    ('Shader',          'getShader'),
    ('StrokeCap',       'getStrokeCap'),
    ('StrokeJoin',      'getStrokeJoin'),
    ('StrokeMiter',     'getStrokeMiter'),
    ('StrokeWidth',     'getStrokeWidth'),
    ('Style',           'getStyle'),
]


def _copyPaint(paint):
    # Make a shallow copy of a Paint object.
    # I was hoping for a paint.copy() method, though.
    kwargs = {k: getattr(paint, g)() for k, g in _paintProperties}
    return skia.Paint(**kwargs)


def _colorArgs(args):
    """Convert drawbot-style fill/stroke arguments to a tuple containing
    ARGB int values."""
    if not args:
        return None
    alpha = 1
    if len(args) == 1:
        if args[0] is None:
            return None
        r = g = b = args[0]
    elif len(args) == 2:
        r = g = b = args[0]
        alpha = args[1]
    elif len(args) == 3:
        r, g, b = args
    elif len(args) == 4:
        r, g, b, alpha = args
    else:
        assert 0
    return tuple(min(255, max(0, round(v * 255))) for v in (alpha, r, g, b))
