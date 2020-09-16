import os
import pathlib
import skia


class Document:

    def beginPage(self, w, h):
        ...

    def endPage(self):
        ...

    def saveImage(self, path):
        ...


class RecordingDocument(Document):

    def __init__(self):
        self._pictures = []
        self._currentRecorder = None
        self.pageWidth = self.pageHeight = None

    @property
    def isDrawing(self):
        return self._currentRecorder is not None

    def beginPage(self, width, height):
        assert self._currentRecorder is None
        self.pageWidth = width
        self.pageHeight = height
        self._currentRecorder = skia.PictureRecorder()
        return self._currentRecorder.beginRecording(width, height)

    def endPage(self):
        self._pictures.append(self._currentRecorder.finishRecordingAsPicture())
        self._currentRecorder = None
        self.pageWidth = self.pageHeight = None

    def saveImage(self, path, **kwargs):
        path = pathlib.Path(path).resolve()
        suffix = path.suffix.lower().lstrip(".")
        methodName = f"_saveImage_{suffix}"
        method = getattr(self, methodName, None)
        if method is None:
            raise ValueError(f"unsupported file type: {suffix}")
        method(path)

    def _saveImage_pdf(self, path, **kwargs):
        stream = skia.FILEWStream(os.fspath(path))
        with skia.PDF.MakeDocument(stream) as document:
            for picture in self._pictures:
                x, y, width, height = picture.cullRect()
                assert x == 0 and y == 0
                with document.page(width, height) as canvas:
                    canvas.drawPicture(picture)

    def _saveImage_png(self, path, **kwargs):
        _savePictures(self._pictures, path, skia.kPNG)

    def _saveImage_jpeg(self, path, **kwargs):
        _savePictures(self._pictures, path, skia.kJPEG, whiteBackground=True)

    _saveImage_jpg = _saveImage_jpeg


def _savePictures(pictures, path, format, whiteBackground=False):
    pictures = [pictures[-1]]
    for index, picture in enumerate(pictures):
        _savePicture(picture, path, format, whiteBackground=whiteBackground)


def _savePicture(picture, path, format, whiteBackground=False):
    x, y, width, height = picture.cullRect()
    assert x == 0 and y == 0
    surface = skia.Surface(int(width), int(height))
    with surface as canvas:
        if whiteBackground:
            canvas.clear(skia.ColorWHITE)
        canvas.drawPicture(picture)
    image = surface.makeImageSnapshot()
    image.save(os.fspath(path), format)


class PixelDocument(Document):
    ...


class MP4Document(PixelDocument):
    ...


class PDFDocument(Document):
    ...


class SVGDocument(Document):
    ...
