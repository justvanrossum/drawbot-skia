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

    def __init__(self, _doInitialize=True):
        if _doInitialize:
            # see self.copy()
            self.fillPaint = FillPaint()
            self.strokePaint = StrokePaint(somethingToDraw=False)
            self.textStyle = TextStyle()

    def copy(self):
        result = GraphicsState(_doInitialize=False)
        # Our main attributes are copy-on-write, so we can share them with
        # our copy
        result.fillPaint = self.fillPaint
        result.strokePaint = self.strokePaint
        result.textStyle = self.textStyle
        return result

    # Paint style

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

    def setBlendMode(self, blendMode):
        self.fillPaint = self.fillPaint.copy(blendMode=blendMode)
        self.strokePaint = self.strokePaint.copy(blendMode=blendMode)

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
        self.textStyle = self.textStyle.copy(font=fontNameOrPath)

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

    def setFontVariations(self, variations, resetVariations):
        if resetVariations:
            currentVariations = {}
        else:
            currentVariations = dict(self.textStyle.variations)
        currentVariations.update(variations)
        self.textStyle = self.textStyle.copy(variations=currentVariations)
        return currentVariations

    def setLanguage(self, language):
        self.textStyle = self.textStyle.copy(language=language)


class _ImmutableContainer:

    def __init__(self, **properties):
        self.__dict__.update(properties)
        self._names = set(properties)

    def copy(self, **properties):
        dct = {n: self.__dict__[n] for n in self._names}
        dct.update(properties)
        return self.__class__(**dct)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self._names != other._names:
            return False
        return all(getattr(self, n) == getattr(other, n) for n in self._names)

    def __repr__(self):
        args = ", ".join(f"{n}={self.__dict__[n]!r}" for n in self._names)
        return f"{self.__class__.__name__}({args})"


class FillPaint(_ImmutableContainer):

    somethingToDraw = True
    color = (255, 0, 0, 0)  # ARGB
    blendMode = "normal"

    @cached_property
    def skPaint(self):
        return self._makePaint(skia.Paint.kFill_Style)

    def _makePaint(self, style):
        paint = skia.Paint(
            Color=0,
            AntiAlias=True,
            Style=style,
        )
        paint.setARGB(*self.color)
        paint.setBlendMode(_blendModeMapping[self.blendMode])
        return paint


class StrokePaint(FillPaint):

    miterLimit = 5
    strokeWidth = 1
    lineCap = "butt"
    lineJoin = "miter"

    @cached_property
    def skPaint(self):
        paint = self._makePaint(skia.Paint.kStroke_Style)
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

# NOTE: 'plusDarker' is missing
_blendModeMapping = {
    "softLight": skia.BlendMode.kSoftLight,  # lighten or darken, depending on source
    "destinationOut": skia.BlendMode.kDstOut,  # destination trimmed outside source
    "clear": skia.BlendMode.kClear,  # replaces destination with zero: fully transparent
    "sourceIn": skia.BlendMode.kSrcIn,  # source trimmed inside destination
    "destinationOver": skia.BlendMode.kDstOver,  # destination over source
    "hardLight": skia.BlendMode.kHardLight,  # multiply or screen, depending on source
    # "???": skia.BlendMode.kDst,  # preserves destination
    "xOR": skia.BlendMode.kXor,  # each of source and destination trimmed outside the other
    "hue": skia.BlendMode.kHue,  # hue of source with saturation and luminosity of destination
    "screen": skia.BlendMode.kScreen,  # multiply inverse of pixels, inverting result; brightens destination
    # "???": skia.BlendMode.kLastMode,  # last valid value
    "difference": skia.BlendMode.kDifference,  # subtract darker from lighter with higher contrast
    "overlay": skia.BlendMode.kOverlay,  # multiply or screen, depending on destination
    # "???": skia.BlendMode.kModulate,  # product of premultiplied colors; darkens destination
    "colorBurn": skia.BlendMode.kColorBurn,  # darken destination to reflect source
    # "???": skia.BlendMode.kSrc,  # replaces destination
    "plusLighter": skia.BlendMode.kPlus,  # sum of colors
    "destinationIn": skia.BlendMode.kDstIn,  # destination trimmed by source
    "destinationAtop": skia.BlendMode.kDstATop,  # destination inside source blended with source
    "saturation": skia.BlendMode.kSaturation,  # saturation of source with hue and luminosity of destination
    # "???": skia.BlendMode.kLastSeparableMode,  # last blend mode operating separately on components
    "sourceAtop": skia.BlendMode.kSrcATop,  # source inside destination blended with destination
    "sourceOut": skia.BlendMode.kSrcOut,  # source trimmed outside destination
    # "???": skia.BlendMode.kLastCoeffMode,  # last porter duff blend mode
    "normal": skia.BlendMode.kSrcOver,  # source over destination
    "copy": skia.BlendMode.kSrcOver,  # source over destination
    "colorDodge": skia.BlendMode.kColorDodge,  # brighten destination to reflect source
    "darken": skia.BlendMode.kDarken,  # darker of source and destination
    "luminosity": skia.BlendMode.kLuminosity,  # luminosity of source with hue and saturation of destination
    "multiply": skia.BlendMode.kMultiply,  # multiply source with destination, darkening image
    "lighten": skia.BlendMode.kLighten,  # lighter of source and destination
    "color": skia.BlendMode.kColor,  # hue and saturation of source with luminosity of destination
    "exclusion": skia.BlendMode.kExclusion,  # subtract darker from lighter with lower contrast
}


class TextStyle(_ImmutableContainer):

    fontSize = 10
    features = {}  # won't get mutated
    variations = {}  # won't get mutated
    language = None

    def __init__(self, **properties):
        super().__init__(**properties)

    @cached_property
    def skFont(self):
        typeface, ttFont = self._getTypefaceAndTTFont(self.font)
        if self.variations and "fvar" in ttFont:
            typeface = self._cloneTypeface(typeface, ttFont, self.variations)
        font = self._makeFontFromTypeface(typeface, self.fontSize)
        return font

    @property
    def ttFont(self):
        _, ttFont = self._getTypefaceAndTTFont(self.font)
        return ttFont

    @staticmethod
    def _getTypefaceAndTTFont(fontNameOrPath):
        cacheKey = fontNameOrPath
        if cacheKey not in _fontCache:
            fontNameOrPath = os.fspath(fontNameOrPath)
            if not os.path.exists(fontNameOrPath):
                typeface = skia.Typeface(fontNameOrPath)
            else:
                typeface = skia.Typeface.MakeFromFile(fontNameOrPath)
                if typeface is None:
                    raise DrawbotError(f"can't load font: {fontNameOrPath}")
            ttFont = makeTTFontFromSkiaTypeface(typeface)
            _fontCache[cacheKey] = typeface, ttFont
        return _fontCache[cacheKey]

    @staticmethod
    def _makeFontFromTypeface(typeface, size):
        font = skia.Font(typeface, size)
        font.setForceAutoHinting(False)
        font.setHinting(skia.FontHinting.kNone)
        font.setSubpixel(True)
        font.setEdging(skia.Font.Edging.kAntiAlias)
        return font

    @staticmethod
    def _cloneTypeface(typeface, ttFont, variations):
        fvar = ttFont.get("fvar")
        defaultLocation = {a.axisTag: variations.get(a.axisTag, a.defaultValue) for a in fvar.axes}
        tags = [a.axisTag for a in fvar.axes]
        location = [(tag, variations.get(tag, defaultLocation[tag])) for tag in tags]
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
                language=self.language,
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


# Font cache dict
# - keys: font name or path string
# - values: (skTypeface, ttFont) tuples
_fontCache = {}


def clearFontCache():
    _fontCache.clear()
