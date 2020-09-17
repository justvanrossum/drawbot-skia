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

    def line(self, pt1, pt2):
        x1, y1 = pt1
        x2, y2 = pt2
        self._drawItem(self._canvas.drawLine, x1, y1, x2, y2)

    def polygon(self, firstPoint, *points, close=True):
        from .path import BezierPath
        bez = BezierPath()
        bez.polygon(firstPoint, *points, close=close)
        self.drawPath(bez)

    def drawPath(self, path):
        self._drawItem(self._canvas.drawPath, path.path)

    def fill(self, *args):
        self._gstate.setFillColor(_colorArgs(args))

    def stroke(self, *args):
        self._gstate.setStrokeColor(_colorArgs(args))

    def strokeWidth(self, value):
        self._gstate.strokePaint.setStrokeWidth(value)

    def lineCap(self, value):
        self._gstate.strokePaint.setStrokeCap(_strokeCapMapping[value])

    def lineJoin(self, value):
        self._gstate.strokePaint.setStrokeJoin(_strokeJoinMapping[value])

    def miterLimit(self, value):
        self._gstate.strokePaint.setStrokeMiter(value)

    def font(self, fontNameOrPath, fontSize=None):
        if fontSize is not None:
            self.fontSize(fontSize)
        self._gstate.setFont(fontNameOrPath)

    def fontSize(self, size):
        self._gstate.font.setSize(size)

    def fontVariations(self, *, resetVariations=False, **location):
        return self._gstate.setFontVariations(location, resetVariations)

    def text(self, txt, position, align=None):
        if not txt:
            # Hard Skia crash otherwise
            return
        # XXX replace with harfbuzz-based layout
        x, y = position
        blob = skia.TextBlob(txt, self._gstate.font)
        self._canvas.save()
        textWidth = self._gstate.font.measureText(txt)
        if align == "right":
            x -= textWidth
        elif align == "center":
            x -= textWidth / 2
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
            canvasMethod(*items, self._gstate.fillPaint)
        if self._gstate.doStroke:
            canvasMethod(*items, self._gstate.strokePaint)


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

    def __init__(self, cachedTypefaces=None):
        self.doFill = True
        self.doStroke = False
        self.fillPaint = skia.Paint(
            Color=0xFF000000,
            AntiAlias=True,
            Style=skia.Paint.kFill_Style,
        )
        self.strokePaint = skia.Paint(
            Color=0xFF000000,
            AntiAlias=True,
            Style=skia.Paint.kStroke_Style,
        )
        self.strokePaint.setStrokeMiter(5)  # default better matching DrawBot
        self.font = skia.Font(skia.Typeface(None), 10)
        self.font.setForceAutoHinting(False)
        self.font.setHinting(skia.FontHinting.kNone)
        self.font.setSubpixel(True)
        self.font.setEdging(skia.Font.Edging.kAntiAlias)
        self._ttFont = None
        if cachedTypefaces is None:
            cachedTypefaces = {}
        self._cachedTypefaces = cachedTypefaces

    def copy(self):
        result = GraphicsState(self._cachedTypefaces)
        result.__dict__.update(self.__dict__)
        result.fillPaint = _copyPaint(self.fillPaint)
        result.strokePaint = _copyPaint(self.strokePaint)
        result.font = _copyFont(self.font)
        return result

    def setFillColor(self, color):
        if color is None:
            self.doFill = False
        else:
            self.doFill = True
            self.fillPaint.setARGB(*color)

    def setStrokeColor(self, color):
        if color is None:
            self.doStroke = False
        else:
            self.doStroke = True
            self.strokePaint.setARGB(*color)

    def setFont(self, fontNameOrPath):
        if os.path.exists(fontNameOrPath):
            path = os.path.normpath(os.path.abspath(os.fspath(fontNameOrPath)))
            tf = self._getFontFromFile(path)
        else:
            tf = skia.Typeface(fontNameOrPath)
        self.font.setTypeface(tf)
        self._ttFont = None  # purge cached TTFont

    def _getFontFromFile(self, fontPath):
        if fontPath not in self._cachedTypefaces:
            tf = skia.Typeface.MakeFromFile(fontPath)
            self._cachedTypefaces[fontPath] = tf
        return self._cachedTypefaces[fontPath]

    def setFontVariations(self, location, resetVariations):
        from .font import intToTag
        fvar = self.ttFont.get("fvar")
        if fvar is None:
            # TODO: warn?
            return

        if resetVariations:
            currentLocation = {a.axisTag: location.get(a.axisTag, a.defaultValue) for a in fvar.axes}
        else:
            pos = self.font.getTypeface().getVariationDesignPosition()
            # XXX: With MutatorSans.ttf, this is "overcomplete" on macOS
            # (hence the p.axis != 0 condition), and incomplete on Linux:
            # the wght axis is not reported there.
            # https://github.com/kyamagu/skia-python/issues/112
            currentLocation = {intToTag(p.axis): p.value for p in pos if p.axis != 0}

        tags = [a.axisTag for a in fvar.axes]
        location = [(tag, location.get(tag, currentLocation[tag])) for tag in tags]
        self._setFontVariationDesignPosition(location)
        return dict(location)

    def _setFontVariationDesignPosition(self, location):
        from .font import tagToInt
        makeCoord = skia.FontArguments.VariationPosition.Coordinate
        rawCoords = [makeCoord(tagToInt(tag), value) for tag, value in location]
        coords = skia.FontArguments.VariationPosition.Coordinates(rawCoords)
        pos = skia.FontArguments.VariationPosition(coords)
        fontArgs = skia.FontArguments()
        fontArgs.setVariationDesignPosition(pos)
        tf = self.font.getTypeface().makeClone(fontArgs)
        self.font.setTypeface(tf)

    @property
    def ttFont(self):
        if self._ttFont is None:
            from .font import makeTTFontFromSkiaTypeface
            self._ttFont = makeTTFontFromSkiaTypeface(self.font.getTypeface())
        return self._ttFont


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
