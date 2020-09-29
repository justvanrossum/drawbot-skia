import os
import pathlib
import skia
from drawbot_skia.font import makeTTFontFromSkiaTypeface
from drawbot_skia.gstate import GraphicsState


testDir = pathlib.Path(__file__).resolve().parent
fontPath = testDir / "fonts" / "MutatorSans.ttf"


def test_font():
    skTypeface = skia.Typeface.MakeFromFile(os.fspath(fontPath))
    ttf = makeTTFontFromSkiaTypeface(skTypeface)
    assert ttf["name"].getName(6, 3, 1).toUnicode() == "MutatorMathTest-LightCondensed"
    fvar = ttf["fvar"]
    assert fvar.axes[0].axisTag == "wdth"
    assert ["name", "fvar"] == list(ttf.tables.keys())


def test_font_gs():
    gs = GraphicsState()
    gs.font(fontPath)
    assert "fvar" in gs.textStyle.ttFont
