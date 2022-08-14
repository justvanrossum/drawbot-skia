import struct
import uharfbuzz as hb
from fontTools.ttLib import TTFont


def makeHBFaceFromSkiaTypeface(skTypeface):
    tableData = {}
    tableTags = {intToTag(tag) for tag in skTypeface.getTableTags()}

    def getTable(face, tag, userData):
        if tag in tableData:
            return tableData[tag]
        if tag not in tableTags:
            return None
        data = skTypeface.getTableData(tagToInt(tag))
        # HB doesn't hold on the data, and neither does Skia, so we
        # need to do that ourselves.
        tableData[tag] = data
        return data

    return hb.Face.create_for_tables(getTable, None)


def makeTTFontFromSkiaTypeface(skTypeface):
    ttf = TTFont(lazy=True)
    ttf.reader = SkiaSFNTReader(skTypeface)
    ttf._tableCache = (
        None  # fonttools fix: doesn't get set when not reading from a file
    )
    return ttf


class SkiaSFNTReader:
    def __init__(self, skTypeface):
        self.skTypeface = skTypeface
        self.tags = {intToTag(tagInt): tagInt for tagInt in skTypeface.getTableTags()}

    def __len__(self):
        return len(self.tags)

    def __contains__(self, tag):
        return tag in self.tags

    def keys(self):
        return self.tags.keys()

    def __getitem__(self, tag):
        if tag not in self.tags:
            raise KeyError(tag)
        return self.skTypeface.getTableData(self.tags[tag])


def intToTag(intTag):
    return struct.pack(">i", intTag).decode()


def tagToInt(tag):
    if isinstance(tag, str):
        tag = bytes(tag, "ascii")
    return struct.unpack(">i", tag)[0]
