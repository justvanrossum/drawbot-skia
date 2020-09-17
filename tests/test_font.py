import os
import pathlib
import skia
from drawbot_skia.font import makeTTFontFromSkiaTypeface


testDir = pathlib.Path(__file__).resolve().parent
fontPath = testDir / "fonts" / "MutatorSans.ttf"


def test_font():
    skTypeface = skia.Typeface.MakeFromFile(os.fspath(fontPath))
    ttf = makeTTFontFromSkiaTypeface(skTypeface)
    assert ttf["name"].getName(6, 3, 1).toUnicode() == "MutatorMathTest-LightCondensed"
    fvar = ttf["fvar"]
    assert fvar.axes[0].axisTag == "wdth"
