import os
import pathlib
import pytest
import skia
from drawbot_skia.text import GlyphInfo, getShapeFuncForSkiaTypeface


testDir = pathlib.Path(__file__).resolve().parent
mutatorFontPath = testDir / "fonts" / "MutatorSans.ttf"
plexFontPath = testDir / "fonts" / "IBMPlexSansArabic-Regular.otf"


shapeTestCases = [
    (mutatorFontPath, "ABC", {}, {}, None, None, None, [
        GlyphInfo(gid=1, cluster=0, dx=0, dy=0, ax=400, ay=0),
        GlyphInfo(gid=2, cluster=1, dx=0, dy=0, ax=443, ay=0),
        GlyphInfo(gid=3, cluster=2, dx=0, dy=0, ax=499, ay=0),
     ]),
    (plexFontPath, "ag0", {}, {}, None, None, None, [
        GlyphInfo(gid=1, cluster=0, dx=0, dy=0, ax=534, ay=0),
        GlyphInfo(gid=8, cluster=1, dx=0, dy=0, ax=528, ay=0),
        GlyphInfo(gid=56, cluster=2, dx=0, dy=0, ax=600, ay=0),
     ]),
    (plexFontPath, "ag0", dict(ss01=True, ss02=True, ss03=True), {}, None, None, None, [
        GlyphInfo(gid=2, cluster=0, dx=0, dy=0, ax=580, ay=0),
        GlyphInfo(gid=9, cluster=1, dx=0, dy=0, ax=580, ay=0),
        GlyphInfo(gid=58, cluster=2, dx=0, dy=0, ax=600, ay=0),
     ]),
    (plexFontPath, "أي", {}, {}, None, None, None, [
        GlyphInfo(gid=990, cluster=1, dx=0, dy=0, ax=726, ay=0),
        GlyphInfo(gid=295, cluster=0, dx=0, dy=0, ax=224, ay=0),
     ]),
]


@pytest.mark.parametrize(
    "fontPath, text, features, variations, direction, language, script, expectedGlyphs",
    shapeTestCases,
)
def test_shape(fontPath, text, features, variations, direction, language, script, expectedGlyphs):
    tf = skia.Typeface.MakeFromFile(os.fspath(fontPath))
    shapeFunc = getShapeFuncForSkiaTypeface(tf)
    glyphs = shapeFunc(
        text,
        features=features,
        variations=variations,
        direction=direction,
        language=language,
        script=script,
    )
    assert expectedGlyphs == glyphs
