import contextlib
import math
import skia
from .document import RecordingDocument
from .errors import DrawbotError
from .gstate import GraphicsState


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
            self.size(1000, 1000)  # This will create the canvas
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
        self._gstate.setStrokeWidth(value)

    def lineCap(self, lineCap):
        self._gstate.setLineCap(lineCap)

    def lineJoin(self, lineJoin):
        self._gstate.setLineJoin(lineJoin)

    def miterLimit(self, miterLimit):
        self._gstate.setMiterLimit(miterLimit)

    def font(self, fontNameOrPath, fontSize=None):
        if fontSize is not None:
            self.fontSize(fontSize)
        self._gstate.setFont(fontNameOrPath)

    def fontSize(self, size):
        self._gstate.setFontSize(size)

    def openTypeFeatures(self, *, resetFeatures=False, **features):
        return self._gstate.setOpenTypeFeatures(features, resetFeatures)

    def fontVariations(self, *, resetVariations=False, **variations):
        return self._gstate.setFontVariations(variations, resetVariations)

    def textSize(self, txt):
        # TODO: with some smartness we can shape only once, for a
        # textSize()/text() call combination with the same text and
        # the same text parameters.
        glyphsInfo = self._gstate.textStyle.shape(txt)
        textWidth = glyphsInfo.endPos[0]
        return (textWidth, self._gstate.textStyle.skFont.getSpacing())

    def text(self, txt, position, align=None):
        if not txt:
            # Hard Skia crash otherwise
            return

        glyphsInfo = self._gstate.textStyle.shape(txt)
        builder = skia.TextBlobBuilder()
        builder.allocRunPos(self._gstate.textStyle.skFont, glyphsInfo.gids, glyphsInfo.positions)
        blob = builder.make()

        x, y = position
        textWidth = glyphsInfo.endPos[0]
        if align is None:
            align = "left" if not glyphsInfo.baseLevel else "right"
        if align == "right":
            x -= textWidth
        elif align == "center":
            x -= textWidth / 2

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
        if self._gstate.fillPaint.somethingToDraw:
            canvasMethod(*items, self._gstate.fillPaint.skPaint)
        if self._gstate.strokePaint.somethingToDraw:
            canvasMethod(*items, self._gstate.strokePaint.skPaint)


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
