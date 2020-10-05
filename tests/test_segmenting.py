import pytest
from drawbot_skia.segmenting import textSegments, textSegmentIndices, reorderedSegments


arabicText = " أحدث "
hebrewText = " מוסיקה "
latinText = " hello "


testTexts = [
    (arabicText, None, 1, [(0, 6, "Arab", 1)]),
    (arabicText, 0, 0, [(0, 1, 'Arab', 0), (1, 5, 'Arab', 1), (5, 6, 'Arab', 0)]),
    (hebrewText, None, 1, [(0, 8, "Hebr", 1)]),
    (latinText, None, 0, [(0, 7, "Latn", 0)]),
    (latinText, 1, 1, [(0, 1, 'Latn', 1), (1, 6, 'Latn', 2), (6, 7, 'Latn', 1)]),
    (latinText + arabicText + latinText, None, 0,
        [(0, 8, "Latn", 0), (8, 12, "Arab", 1), (12, 14, "Arab", 0), (14, 20, "Latn", 0)]),
    (arabicText + latinText + arabicText, None, 1,
        [(0, 7, 'Arab', 1), (7, 12, 'Latn', 2), (12, 14, 'Latn', 1), (14, 19, 'Arab', 1)]),
    (latinText + arabicText + hebrewText + latinText, None, 0,
        [(0, 8, 'Latn', 0), (8, 14, 'Arab', 1), (14, 20, 'Hebr', 1, ), (20, 22, 'Hebr', 0), (22, 28, 'Latn', 0)]),
]


@pytest.mark.parametrize("text, baseLevelOverride, expectedBaseLevel, expectedSegments", testTexts)
def test_textSegments(text, baseLevelOverride, expectedBaseLevel, expectedSegments):
    segments, baseLevel = textSegments(text, baseLevelOverride)
    assert expectedBaseLevel == baseLevel
    newSegments = []
    for seg, script, bidiLevel, index in segments:
        newSegments.append((index, index + len(seg), script, bidiLevel))
    assert expectedSegments == newSegments


@pytest.mark.parametrize("text, baseLevelOverride, expectedBaseLevel, expectedSegments", testTexts)
def test_textSegmentIndices(text, baseLevelOverride, expectedBaseLevel, expectedSegments):
    segments, baseLevel = textSegmentIndices(text, baseLevelOverride)
    assert expectedBaseLevel == baseLevel
    assert expectedSegments == segments


def test_reorderedSegments():
    text = latinText + arabicText + hebrewText + latinText
    segments, baseLevel = textSegments(text)
    segments = [(len(seg), script, bidiLevel, index) for seg, script, bidiLevel, index in segments]
    expectedOriginal = [(8, 'Latn', 0, 0), (6, 'Arab', 1, 8), (6, 'Hebr', 1, 14), (2, 'Hebr', 0, 20), (6, 'Latn', 0, 22)]
    assert expectedOriginal == segments
    reordered = reorderedSegments(segments, baseLevel, lambda seg: seg[2])
    expectedReordered = [(8, 'Latn', 0, 0), (6, 'Hebr', 1, 14), (6, 'Arab', 1, 8), (2, 'Hebr', 0, 20), (6, 'Latn', 0, 22)]
    assert expectedReordered == reordered
