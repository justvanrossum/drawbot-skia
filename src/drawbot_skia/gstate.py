import os
import skia
from .errors import DrawbotError
from .text import getShapeFuncForSkiaTypeface
from .segmenting import textSegments, reorderedSegments


class GraphicsState:

    def __init__(self, cachedTypefaces=None, _doInitialize=True):
        if cachedTypefaces is None:
            cachedTypefaces = {}
        self.doFill = True
        self.doStroke = False
        self._cachedTypefaces = cachedTypefaces

        if not _doInitialize:
            # self.copy() will initialize further
            return

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
        self.textStyle = TextStyle(cachedTypefaces)

    def copy(self):
        result = GraphicsState(self._cachedTypefaces, _doInitialize=False)
        for name in ["doFill", "doStroke"]:
            setattr(result, name, getattr(self, name))
        result.fillPaint = _copyPaint(self.fillPaint)
        result.strokePaint = _copyPaint(self.strokePaint)
        result.textStyle = self.textStyle.copy()
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


class TextStyle:

    def __init__(self, cachedTypefaces, _doInitialize=True):
        self._cachedTypefaces = cachedTypefaces
        self._ttFont = None
        self._shape = None

        if not _doInitialize:
            # self.copy() will initialize further
            return

        self.font = skia.Font(skia.Typeface(None), 10)
        self.font.setForceAutoHinting(False)
        self.font.setHinting(skia.FontHinting.kNone)
        self.font.setSubpixel(True)
        self.font.setEdging(skia.Font.Edging.kAntiAlias)
        self.currentFeatures = {}
        self.currentVariations = {}

    def copy(self):
        result = TextStyle(self._cachedTypefaces, _doInitialize=False)
        result.font = _copyFont(self.font)
        result.currentFeatures = dict(self.currentFeatures)
        result.currentVariations = dict(self.currentVariations)

    def setFont(self, fontNameOrPath):
        if os.path.exists(fontNameOrPath):
            path = os.path.normpath(os.path.abspath(os.fspath(fontNameOrPath)))
            tf = self._getFontFromFile(path)
        else:
            tf = skia.Typeface(fontNameOrPath)
        self.font.setTypeface(tf)
        # purge cached items:
        self._ttFont = None
        self._shape = None

    def _getFontFromFile(self, fontPath):
        if fontPath not in self._cachedTypefaces:
            tf = skia.Typeface.MakeFromFile(fontPath)
            if tf is None:
                raise DrawbotError(f"can't load font: {fontPath}")
            self._cachedTypefaces[fontPath] = tf
        return self._cachedTypefaces[fontPath]

    def setOpenTypeFeatures(self, features, resetFeatures):
        if resetFeatures:
            self.currentFeatures = {}
        self.currentFeatures.update(features)
        return dict(self.currentFeatures)

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
            # https://github.com/kyamagu/skia-python/issues/113
            currentLocation = {intToTag(p.axis): p.value for p in pos if p.axis != 0}

        tags = [a.axisTag for a in fvar.axes]
        location = [(tag, location.get(tag, currentLocation[tag])) for tag in tags]
        self._setFontVariationDesignPosition(location)
        self.currentVariations = dict(location)
        return dict(self.currentVariations)

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

    def shape(self, txt):
        if self._shape is None:
            self._shape = getShapeFuncForSkiaTypeface(self.font.getTypeface())

        segments, baseLevel = textSegments(txt)
        segments = reorderedSegments(segments, baseLevel)
        startPos = (0, 0)
        glyphsInfo = None
        for runChars, script, bidiLevel, index in segments:
            runInfo = self._shape(
                runChars,
                fontSize=self.font.getSize(),
                startPos=startPos,
                startCluster=index,
                flippedCanvas=True,
                features=self.currentFeatures,
                variations=self.currentVariations,
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
