import os
import skia
from .errors import DrawbotError
from .font import makeTTFontFromSkiaTypeface, tagToInt
from .text import getShapeFuncForSkiaTypeface
from .segmenting import textSegments, reorderedSegments


class cached_property(object):

    # This exitsts in the stdlib in Python 3.8, but not earlier

    """A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property."""

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class GraphicsState:

    def __init__(self, cachedTypefaces=None, _doInitialize=True):
        if cachedTypefaces is None:
            cachedTypefaces = {}
        self._cachedTypefaces = cachedTypefaces

        if _doInitialize:
            self.fillPaint = FillPaint()
            self.strokePaint = StrokePaint(somethingToDraw=False)
            self.textStyle = TextStyle(cachedTypefaces)

    def copy(self):
        result = GraphicsState(self._cachedTypefaces, _doInitialize=False)
        result.fillPaint = self.fillPaint
        result.strokePaint = self.strokePaint
        result.textStyle = self.textStyle
        return result

    def setFillColor(self, color):
        if color is None:
            self.fillPaint = self.fillPaint.copy(somethingToDraw=False)
        else:
            self.fillPaint = self.fillPaint.copy(color=color, somethingToDraw=True)

    def setStrokeColor(self, color):
        if color is None:
            self.strokePaint = self.strokePaint.copy(somethingToDraw=False)
        else:
            self.strokePaint = self.strokePaint.copy(color=color, somethingToDraw=True)

    def setStrokeWidth(self, strokeWidth):
        self.strokePaint = self.strokePaint.copy(strokeWidth=strokeWidth)

    def setLineCap(self, lineCap):
        self.strokePaint = self.strokePaint.copy(lineCap=lineCap)

    def setLineJoin(self, lineJoin):
        self.strokePaint = self.strokePaint.copy(lineJoin=lineJoin)

    def setMiterLimit(self, miterLimit):
        self.strokePaint = self.strokePaint.copy(miterLimit=miterLimit)

    # Text style

    def setFont(self, fontNameOrPath):
        if os.path.exists(fontNameOrPath):
            font = os.path.normpath(os.path.abspath(os.fspath(fontNameOrPath)))
        else:
            font = font
        self.textStyle = self.textStyle.copy(font=font)

    def setFontSize(self, size):
        self.textStyle = self.textStyle.copy(fontSize=size)

    def setOpenTypeFeatures(self, features, resetFeatures):
        if resetFeatures:
            currentFeatures = {}
        else:
            currentFeatures = dict(self.textStyle.features)
        currentFeatures.update(features)
        self.textStyle = self.textStyle.copy(features=currentFeatures)
        return currentFeatures

    def setFontVariations(self, location, resetVariations):
        if resetVariations:
            currentVariations = {}
        else:
            currentVariations = dict(self.textStyle.variations)
        currentVariations.update(location)
        self.textStyle = self.textStyle.copy(variations=currentVariations)
        return currentVariations


class FillPaint:

    somethingToDraw = True
    color = (255, 0, 0, 0)  # ARGB

    def __init__(self, **properties):
        self.__dict__.update(properties)
        self._names = set(properties)

    def copy(self, **properties):
        d = {n: self.__dict__[n] for n in self._names}
        d.update(properties)
        return self.__class__(**d)

    @cached_property
    def paint(self):
        paint = skia.Paint(
            Color=0,
            AntiAlias=True,
            Style=skia.Paint.kFill_Style,
        )
        paint.setARGB(*self.color)
        return paint


class StrokePaint(FillPaint):

    miterLimit = 5
    strokeWidth = 1
    lineCap = "butt"
    lineJoin = "miter"

    @cached_property
    def paint(self):
        paint = skia.Paint(
            Color=0,
            AntiAlias=True,
            Style=skia.Paint.kStroke_Style,
        )
        paint.setARGB(*self.color)
        paint.setStrokeMiter(self.miterLimit)
        paint.setStrokeWidth(self.strokeWidth)
        paint.setStrokeCap(_strokeCapMapping[self.lineCap])
        paint.setStrokeJoin(_strokeJoinMapping[self.lineJoin])
        return paint


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


class TextStyle:

    fontSize = 10
    features = {}  # won't get mutated
    variations = {}  # won't get mutated

    def __init__(self, cachedTypefaces, **styleProperties):
        self._cachedTypefaces = cachedTypefaces
        self.__dict__.update(styleProperties)
        self._names = set(styleProperties)

    def copy(self, **styleProperties):
        d = {n: self.__dict__[n] for n in self._names}
        d.update(styleProperties)
        return self.__class__(self._cachedTypefaces, **d)

    @cached_property
    def skFont(self):
        typeface, ttFont = self._getTypefaceAndTTFont(self.font)
        if self.variations and "fvar" in ttFont:
            typeface = self._cloneTypeface(typeface, ttFont, self.variations)
        font = self._makeFont(typeface, self.fontSize)
        return font

    def _getTypefaceAndTTFont(self, font):
        if font not in self._cachedTypefaces:
            if not os.path.exists(font):
                typeface = skia.Typeface(font)
            else:
                typeface = skia.Typeface.MakeFromFile(font)
                if typeface is None:
                    raise DrawbotError(f"can't load font: {font}")
            ttFont = makeTTFontFromSkiaTypeface(typeface)
            self._cachedTypefaces[font] = typeface, ttFont
        return self._cachedTypefaces[font]

    @staticmethod
    def _makeFont(typeface, size):
        font = skia.Font(typeface, size)
        font.setForceAutoHinting(False)
        font.setHinting(skia.FontHinting.kNone)
        font.setSubpixel(True)
        font.setEdging(skia.Font.Edging.kAntiAlias)
        return font

    @staticmethod
    def _cloneTypeface(typeface, ttFont, location):
        fvar = ttFont.get("fvar")
        defaultLocation = {a.axisTag: location.get(a.axisTag, a.defaultValue) for a in fvar.axes}
        tags = [a.axisTag for a in fvar.axes]
        location = [(tag, location.get(tag, defaultLocation[tag])) for tag in tags]
        makeCoord = skia.FontArguments.VariationPosition.Coordinate
        rawCoords = [makeCoord(tagToInt(tag), value) for tag, value in location]
        coords = skia.FontArguments.VariationPosition.Coordinates(rawCoords)
        pos = skia.FontArguments.VariationPosition(coords)
        fontArgs = skia.FontArguments()
        fontArgs.setVariationDesignPosition(pos)
        return typeface.makeClone(fontArgs)

    @cached_property
    def _shapeFunc(self):
        return getShapeFuncForSkiaTypeface(self.skFont.getTypeface())

    def shape(self, txt):
        segments, baseLevel = textSegments(txt)
        segments = reorderedSegments(segments, baseLevel)
        startPos = (0, 0)
        glyphsInfo = None
        for runChars, script, bidiLevel, index in segments:
            runInfo = self._shapeFunc(
                runChars,
                fontSize=self.skFont.getSize(),
                startPos=startPos,
                startCluster=index,
                flippedCanvas=True,
                features=self.features,
                variations=self.variations,
            )
            if glyphsInfo is None:
                glyphsInfo = runInfo
            else:
                glyphsInfo.gids += runInfo.gids
                glyphsInfo.clusters += runInfo.clusters
                glyphsInfo.positions += runInfo.positions
                glyphsInfo.endPos = runInfo.endPos
            startPos = runInfo.endPos
        glyphsInfo.baseLevel = baseLevel
        return glyphsInfo


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
