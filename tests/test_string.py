import pytest
from drawbot_skia.string import FormattedString


def test_basics():
    fs = FormattedString()
    fs.append("Hello")
    fs.append(" ")
    fs.append("there.")
    assert fs.text == "Hello there."


def test_good_args():
    fs = FormattedString(font="A", fontSize=12, fill=(1, 0, 0))
    fs.append("ABC")
    fs.fill(0, 1, 0)
    fs.append("DE")
    fs.append("F")
    fs.openTypeFeatures(liga=False)
    fs.append("fiets")
    runs = fs.runs
    assert len(runs) == 3
    assert runs[0].textStyle.font == "A"
    assert runs[0].textStyle.fontSize == 12
    assert runs[0].textStyle.features == {}
    assert runs[0].fillPaint.color == (255, 255, 0, 0)
    assert runs[0].text == "ABC"
    assert runs[1].textStyle.font == "A"
    assert runs[1].fillPaint.color == (255, 0, 255, 0)
    assert runs[1].text == "DEF"
    assert runs[2].textStyle.features == {'liga': False}
    assert runs[2].text == "fiets"


def test_bad_args():
    with pytest.raises(TypeError):
        _ = FormattedString(foo=12)


iterRunsTestData = [
    ([("Hallo", {})], ["Hallo"]),
    ([("Hallo", {}), ("Hallo", {})], ["HalloHallo"]),
    ([("Hallo", {}), ("Hallo", {"font": "Test"})], ["Hallo", "Hallo"]),
    ([("Hallo", {}), ("Hallo", {"font": "Test"}), ("Hallo", {})], ["Hallo", "HalloHallo"]),
]


@pytest.mark.parametrize("input, expectedStrings", iterRunsTestData)
def test_iter_runs(input, expectedStrings):
    fs = FormattedString()
    for txt, style in input:
        fs.append(txt, **style)
    assert expectedStrings == [r.text for r in fs.runs]
    assert "".join(expectedStrings) == fs.text


def test_iterSplit():
    fs = FormattedString(font="A", fontSize=10, fill=0)
    fs.append("abc")
    fs.fontSize(12)
    fs.append("def")
    fs.fill(1, 0, 0)
    fs.append("ghi")
    fs.fontSize(10)
    fs.append("jkl")
    fs.font("B")
    fs.append("mno")
    parts = list(fs.iterSplit(["font", "fontSize"]))
    texts = [p.text for p in parts]
    expected_texts = ['abc', 'defghi', 'jkl', 'mno']
    assert expected_texts == texts


@pytest.fixture
def testString():
    char = ord("a")
    fs = FormattedString()
    for i in range(1, 5):
        fs.fontSize(i + 10)
        for j in range(i):
            fs.append(chr(char))
            char += 1
    return fs


testFindRunIndicesTestData = [
    ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 1, 2, 2, 2, 3, 3, 3, 3]),
    ([9, 8, 7, 6, 5, 4, 3, 2, 1, 0], [3, 3, 3, 3, 2, 2, 2, 1, 1, 0]),
    ([7, 8, 3, 9, 0, 1, 4, 2, 5, 6], [3, 3, 2, 3, 0, 1, 2, 1, 2, 3]),
    ([4, 1, 7, 3, 8, 0, 9, 2, 6, 5], [2, 1, 3, 2, 3, 0, 3, 1, 3, 2]),
]


@pytest.mark.parametrize("charIndices, expectedRunIndices", testFindRunIndicesTestData)
def test_findRunIndex(testString, charIndices, expectedRunIndices):
    assert len(testString.runs) == 4
    assert [0, 1, 3, 6, 10] == testString.runCharIndices
    assert testString.runCharIndices[-1] == len(testString.text)
    runIndices = []
    runIndex = None
    for i in charIndices:
        runIndex = testString.findRunIndex(i, runIndex)
        runIndices.append(runIndex)
    assert expectedRunIndices == runIndices


def test_appendFormattedString(testString):
    numRuns = len(testString.runs)
    testString.append(testString)
    assert len(testString.runs) == numRuns * 2
    testString.append(FormattedString())
    assert len(testString.runs) == numRuns * 2
    assert "abcdefghijabcdefghij" == testString.text


def test_add(testString):
    new = testString + "XYZ"
    assert len(new.runs) == 4
    assert new != testString


def test_iadd(testString):
    before = testString
    testString += "XYZ"
    assert before is testString
    assert len(testString.runs) == 4
    assert "abcdefghijXYZ" == testString.text


def test_copy(testString):
    copy = testString.copy()
    assert copy is not testString
    assert copy.runs is not testString.runs
    assert copy == testString
    copy.fontSize(123)
    assert copy != testString
    copy.fontSize(14)
    assert copy == testString
    copy.append("x")
    assert copy != testString
    testString.append("x")
    assert copy == testString
    assert copy.runs[-1] is not testString.runs[-1]
    assert copy.runs[-1] == testString.runs[-1]
    copy.append("y")
    testString.append("z")
    assert copy != testString
    assert copy.runs[-1] != testString.runs[-1]


@pytest.mark.parametrize("keepends", [False, True])
def test_splitlines(testString, keepends):
    testString.append("\nABC")
    testString.font("Helvetica")
    testString.append("DEF\nGHI")
    lines = testString.splitlines(keepends)
    assert testString.text.splitlines(keepends) == [line.text for line in lines]
    joiner = FormattedString("" if keepends else "\n", fontSize=14)
    joined = joiner.join(lines)
    assert joined.text == testString.text


def test_len(testString):
    assert len(testString.text) == len(testString)
    assert 0 == len(FormattedString())


sliceTestData = [
    (1, [("b", 12)]),
    ((1, 2), [("b", 12)]),
    ((None, 2), [("a", 11), ("b", 12)]),
    ((1, 4), [("bc", 12), ("d", 13)]),
    ((-2, None), [("ij", 14)]),
    ((None, None, -1), TypeError),
]


@pytest.mark.parametrize("index, expectedInput", sliceTestData)
def test_slice(testString, index, expectedInput):
    if not isinstance(expectedInput, list):
        expectedException = expectedInput
        expected = None
    else:
        expectedException = None
        expected = FormattedString()
        for txt, fontSize in expectedInput:
            expected.append(txt, fontSize=fontSize)
    if isinstance(index, tuple):
        slc = slice(*index)
    else:
        slc = index
    if expectedException is not None:
        with pytest.raises(expectedException):
            fs = testString[slc]
    else:
        fs = testString[slc]
        assert expected == fs


def test_textRun_len_slice():
    testString = FormattedString("abcdefg")
    run = testString.runs[0]
    assert 7 == len(run)
    c = run[0]
    assert "a" == c.text
    c = run[:2]
    assert "ab" == c.text
    c = run[-1:]
    assert "g" == c.text
    c = run[-2:]
    assert "fg" == c.text
    c = run[2:5]
    assert "cde" == c.text


arabicText = "  أحدث "
hebrewText = "  מוסיקה "
latinText = "  hello "

isRTLTestData = [
    (latinText, False),
    (arabicText, True),
    (hebrewText, True),
    (hebrewText + latinText, True),
    (latinText + hebrewText, False),
]


@pytest.mark.parametrize("inputString, isRTL", isRTLTestData)
@pytest.mark.parametrize("doFormat", [False, True])
def test_isRTL(inputString, isRTL, doFormat):
    fs = FormattedString()
    if doFormat:
        for i, c in enumerate(inputString):
            fs.append(c, fontSize=10 + i)
    else:
        fs.append(inputString)
    assert isRTL == fs.isRTL
    # Test setter
    fs.isRTL = not fs.isRTL
    assert not isRTL == fs.isRTL


def test_calcFeatureSegments():
    fs = FormattedString()
    fs.openTypeFeatures(liga=False, tnum=True)
    fs.append("abc")
    fs.openTypeFeatures(smcp=True)
    fs.append("def")
    fs.openTypeFeatures(liga=True)
    fs.append("ghi")
    fs.openTypeFeatures(aalt=2)
    fs.append("0")
    fs.openTypeFeatures(aalt=False, smcp=False)
    fs.append("jkl")
    features = fs.buildFeaturesDict()
    expectedFeatures = {
        'aalt': [(9, 10, 2), (10, 13, False)],
        'liga': [(0, 6, False), (6, 13, True)],
        'smcp': [(3, 10, True), (10, 13, False)],
        'tnum': True,
    }
    assert expectedFeatures == features


def test_iterSplitByScriptAndBidi():
    fs = FormattedString()
    fs.append(latinText)
    fs.append(arabicText)
    fs.append(hebrewText)
    parts = fs.iterSplitByScriptAndBidi()
    assert len(parts) == 4
    assert [p.isRTL for p in parts] == [0, 1, 1, 0]
