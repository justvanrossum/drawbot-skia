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


mutatorsans_variations = {
    'wdth': {
        'defaultValue': 0.0,
        'maxValue': 1000.0,
        'minValue': 0.0,
        'name': 'Width',
    },
    'wght': {
        'defaultValue': 0.0,
        'maxValue': 1000.0,
        'minValue': 0.0,
        'name': 'Weight',
    },
}


mutatorsans_instances = {
    'MutatorMathTest-LightCondensed': {'wdth': 0.0, 'wght': 0.0},
    'MutatorMathTest-BoldCondensed': {'wdth': 0.0, 'wght': 1000.0},
    'MutatorMathTest-LightWide': {'wdth': 1000.0, 'wght': 0.0},
    'MutatorMathTest-BoldWide': {'wdth': 1000.0, 'wght': 1000.0},
    'MutatorMathTest-LightCondensed_Medium_Narrow_I': {'wdth': 327.0, 'wght': 500.0},
    'MutatorMathTest-LightCondensed_Medium_Wide_I': {'wdth': 327.0, 'wght': 500.0},
}


def test_listFontVariations():
    gs = GraphicsState()
    gs.font(fontPath)
    assert mutatorsans_variations == gs.listFontVariations()


def test_listNamedInstances():
    gs = GraphicsState()
    gs.font(fontPath)
    namedInstances = gs.listNamedInstances()
    assert mutatorsans_instances == namedInstances
    assert list(mutatorsans_instances) == list(namedInstances)
