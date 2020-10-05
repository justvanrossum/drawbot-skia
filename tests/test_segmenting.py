import pytest
from drawbot_skia.segmenting import textSegments, reorderedSegments


arabicText = " أحدث "
hebrewText = " מוסיקה "
latinText = " hello "


testTexts = [
    (arabicText, 1, [(6, "Arab", 1, 0)]),
    (hebrewText, 1, [(8, "Hebr", 1, 0)]),
    (latinText, 0, [(7, "Latn", 0, 0)]),
    (latinText + arabicText + latinText, 0,
        [(8, "Latn", 0, 0), (4, "Arab", 1, 8), (2, "Arab", 0, 12), (6, "Latn", 0, 14)]),
    (arabicText + latinText + arabicText, 1,
        [(7, 'Arab', 1, 0), (5, 'Latn', 2, 7), (2, 'Latn', 1, 12), (5, 'Arab', 1, 14)]),
    (latinText + arabicText + hebrewText + latinText, 0,
        [(8, 'Latn', 0, 0), (6, 'Arab', 1, 8), (6, 'Hebr', 1, 14), (2, 'Hebr', 0, 20), (6, 'Latn', 0, 22)]),
]


@pytest.mark.parametrize("text, expectedBaseLevel, expectedSegments", testTexts)
def test_textSegments(text, expectedBaseLevel, expectedSegments):
    segments, baseLevel = textSegments(text)
    assert expectedBaseLevel == baseLevel
    segments = [(len(seg), script, bidiLevel, index) for seg, script, bidiLevel, index in segments]
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
