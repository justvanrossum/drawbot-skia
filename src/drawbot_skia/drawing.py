import contextlib
import math
import os
import skia
from .document import RecordingDocument
from .errors import DrawbotError


class Drawing:

    def __init__(self, document=None, flipCanvas=True):
        self._stack = []
        self._gstate = GraphicsState()
        if document is None:
            document = RecordingDocument()
        self._document = document
        self._skia_canvas = None
        self._flipCanvas = flipCanvas

    @property
    def _canvas(self):
        if self._skia_canvas is None:
            self.size(1000, 1000)
        return self._skia_canvas

    @_canvas.setter
    def _canvas(self, canvas):
        self._skia_canvas = canvas

    def newDrawing(self):
        ...

    def endDrawing(self):
        ...

    def size(self, width, height):
        if self._document.isDrawing:
            raise DrawbotError("size() can't be called if there's already a canvas active")
        self.newPage(width,  height)

    def newPage(self, width, height):
        if self._document.isDrawing:
            self._document.endPage()
        self._canvas = self._document.beginPage(width, height)
        if self._flipCanvas:
            self._canvas.translate(0, height)
            self._canvas.scale(1, -1)

    def width(self):
        return self._document.pageWidth

    def height(self):
        return self._document.pageHeight

    def rect(self, x, y, w, h):
        self._drawItem(self._canvas.drawRect, (x, y, w, h))

    def oval(self, x, y, w, h):
        self._drawItem(self._canvas.drawOval, (x, y, w, h))

    def drawPath(self, path):
        self._drawItem(self._canvas.drawPath, path.path)

    def fill(self, *args):
        self._gstate.setFillColor(_colorArgs(args))

    def stroke(self, *args):
        self._gstate.setStrokeColor(_colorArgs(args))

    def strokeWidth(self, value):
        self._gstate.strokeColor.setStrokeWidth(value)

    def lineCap(self, value):
        self._gstate.strokeColor.setStrokeCap(_strokeCapMapping[value])

    def lineJoin(self, value):
        self._gstate.strokeColor.setStrokeJoin(_strokeJoinMapping[value])

    def font(self, fontNameOrPath, fontSize=None):
        if fontSize is not None:
            self.fontSize(fontSize)
        if os.path.exists(fontNameOrPath):
            path = os.path.normpath(os.path.abspath(os.fspath(fontNameOrPath)))
            tf = skia.Typeface.MakeFromFile(path)
        else:
            tf = skia.Typeface(fontNameOrPath)
        self._gstate.font.setTypeface(tf)

    def fontSize(self, size):
        self._gstate.font.setSize(size)

    def text(self, txt, position, align=None):
        if not txt:
            # Hard Skia crash otherwise
            return
        # XXX replace with harfbuzz-based layout
        x, y = position
        blob = skia.TextBlob(txt, self._gstate.font)
        self._canvas.save()
        try:
            self._canvas.translate(x, y)
            if self._flipCanvas:
                self._canvas.scale(1, -1)
            self._drawItem(self._canvas.drawTextBlob, blob, 0, 0)
        finally:
            self._canvas.restore()

    def translate(self, x, y):
        self._canvas.translate(x, y)

    def rotate(self, angle, center=(0, 0)):
        cx, cy = center
        self._canvas.rotate(angle, cx, cy)

    def scale(self, sx, sy=None, center=(0, 0)):
        if sy is None:
            sy = sx
        cx, cy = center
        if cx != 0 or cy != 0:
            self._canvas.translate(cx, cy)
            self._canvas.scale(sx, sy)
            self._canvas.translate(-cx, -cy)
        else:
            self._canvas.scale(sx, sy)

    def skew(self, sx, sy=0, center=(0, 0)):
        cx, cy = center
        if cx != 0 or cy != 0:
            self._canvas.translate(cx, cy)
            self._canvas.skew(math.radians(sx), math.radians(sy))
            self._canvas.translate(-cx, -cy)
        else:
            self._canvas.skew(math.radians(sx), math.radians(sy))

    def transform(self, matrix):
        m = skia.Matrix()
        m.setAffine(matrix)
        self._canvas.concat(m)

    @contextlib.contextmanager
    def savedState(self):
        self._stack.append(self._gstate.copy())
        self._canvas.save()
        yield
        self._canvas.restore()
        self._gstate = self._stack.pop()

    def saveImage(self, fileName):
        if self._document.isDrawing:
            self._document.endPage()
        self._document.saveImage(fileName)

    # Helpers

    def _drawItem(self, canvasMethod, *items):
        if self._gstate.doFill:
            canvasMethod(*items, self._gstate.fillColor)
        if self._gstate.doStroke:
            canvasMethod(*items, self._gstate.strokeColor)


_strokeCapMapping = dict(
    butt=skia.Paint.Cap.kButt_Cap,
    round=skia.Paint.Cap.kRound_Cap,
    square=skia.Paint.Cap.kSquare_Cap,
)

_strokeJoinMapping = dict(
    miter=skia.Paint.Join.kMiter_Join,
    round=skia.Paint.Join.kRound_Join,
    bevel=skia.Paint.Join.kBevel_Join,
)


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
        self.font = skia.Font(skia.Typeface(None), 10)
        self.font.setForceAutoHinting(False)
        self.font.setHinting(skia.FontHinting.kNone)

    def copy(self):
        result = GraphicsState()
        result.__dict__.update(self.__dict__)
        result.fillColor = _copyPaint(self.fillColor)
        result.strokeColor = _copyPaint(self.strokeColor)
        result.font = _copyFont(self.font)
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


_fontProperties = [
    ('setBaselineSnap',      'isBaselineSnap'),
    ('setEdging',            'getEdging'),
    ('setEmbeddedBitmaps',   'isEmbeddedBitmaps'),
    ('setEmbolden',          'isEmbolden'),
    ('setForceAutoHinting',  'isForceAutoHinting'),
    ('setHinting',           'getHinting'),
    ('setLinearMetrics',     'isLinearMetrics'),
    ('setScaleX',            'getScaleX'),
    # ('setSize',              'getSize'),
    ('setSkewX',             'getSkewX'),
    ('setSubpixel',          'isSubpixel'),
    # ('setTypeface',          'getTypeface'),
]


def _copyFont(font):
    # Make a copy of a Font object.
    # Was hoping for a font.copy() method.
    tf = skia.Typeface.MakeDeserialize(font.getTypeface().serialize())
    newFont = skia.Font(tf, font.getSize())
    for setter, getter in _fontProperties:
        getattr(newFont, setter)(getattr(font, getter)())
    return newFont


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
