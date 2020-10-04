import os
import pathlib
import pytest
import skia
from drawbot_skia.shaping import getShapeFuncForSkiaTypeface


testDir = pathlib.Path(__file__).resolve().parent
mutatorFontPath = testDir / "fonts" / "MutatorSans.ttf"
plexFontPath = testDir / "fonts" / "IBMPlexSansArabic-Regular.otf"


shapeTestCases = [
    (mutatorFontPath, "ABC", {}, {}, None, None, None, (
        [1, 2, 3], [0, 1, 2], [(0, 0), (400, 0), (843, 0)], (1342, 0),
     )),
    (plexFontPath, "ag0", {}, {}, None, None, None, (
        [1, 8, 56], [0, 1, 2], [(0, 0), (534, 0), (1062, 0)], (1662, 0),
     )),
    (plexFontPath, "ag0", dict(ss01=True, ss02=True, ss03=True), {}, None, None, None, (
        [2, 9, 58], [0, 1, 2], [(0, 0), (580, 0), (1160, 0)], (1760, 0),
     )),
    (plexFontPath, "أي", {}, {}, None, None, None, (
        [990, 295], [1, 0], [(0, 0), (726, 0)], (950, 0),
     )),
]


@pytest.mark.parametrize(
    "fontPath, text, features, variations, direction, language, script, expected",
    shapeTestCases,
)
def test_shape(fontPath, text, features, variations, direction, language, script, expected):
    tf = skia.Typeface.MakeFromFile(os.fspath(fontPath))
    shapeFunc = getShapeFuncForSkiaTypeface(tf)
    glyphInfo = shapeFunc(
        text,
        features=features,
        variations=variations,
        direction=direction,
        language=language,
        script=script,
    )
    expectedGids, expectedClusters, expectedPositions, expectedEndPos = expected
    assert expectedGids == glyphInfo.gids
    assert expectedClusters == glyphInfo.clusters
    assert expectedPositions == glyphInfo.positions
    assert expectedEndPos == glyphInfo.endPos
