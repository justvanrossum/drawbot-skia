from typing import NamedTuple
import functools
import uharfbuzz as hb
from .font import tagToInt


class GlyphInfo(NamedTuple):
    gid: int
    cluster: int
    dx: int
    dy: int
    ax: int
    ay: int


def getShapeFuncForSkiaTypeface(skTypeface):
    return getShapeFuncForHBFace(makeHBFaceFromSkiaTypeface(skTypeface))


def makeHBFaceFromSkiaTypeface(skTypeface):
    tableData = {}

    def getTable(face, tag, userData):
        if tag in tableData:
            return tableData[tag]
        data = skTypeface.getTableData(tagToInt(tag))
        if not data:
            # Skia returns empty data when a table isn't present,
            # so we can't distinguish beteen an empty table and
            # a non-existant table. I don't think we need the former.
            return None
        # HB doesn't hold on the data, and neither does Skia, so we
        # need to do that ourselves.
        tableData[tag] = data
        return data

    return hb.Face.create_for_tables(getTable, None)


def getShapeFuncForHBFace(face):
    font = hb.Font(face)
    return functools.partial(_shape, face, font)


def _shape(face, font,
           text, *,
           features=None,
           variations=None,
           direction=None,
           language=None,
           script=None):
    if features is None:
        features = {}
    if variations is None:
        variations = {}

    font.scale = (face.upem, face.upem)
    font.set_variations(variations)

    hb.ot_font_set_funcs(font)

    buf = hb.Buffer.create()
    buf.add_str(text)  # add_str() does not accept str subclasses
    buf.guess_segment_properties()
    buf.cluster_level = hb.BufferClusterLevel.MONOTONE_CHARACTERS

    if direction is not None:
        buf.direction = direction
    if language is not None:
        buf.language = language
    if script is not None:
        buf.script = script

    hb.shape(font, buf, features)

    infos = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        infos.append(GlyphInfo(info.codepoint, info.cluster, *pos.position))

    return infos


def getFeatures(face, otTableTag):
    features = set()
    for scriptIndex, script in enumerate(hb.ot_layout_table_get_script_tags(face, otTableTag)):
        langIdices = list(range(len(hb.ot_layout_script_get_language_tags(face, otTableTag, scriptIndex))))
        langIdices.append(0xFFFF)
        for langIndex in langIdices:
            features.update(hb.ot_layout_language_get_feature_tags(face, otTableTag, scriptIndex, langIndex))
    return sorted(features)
