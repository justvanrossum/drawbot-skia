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
    fs = FormattedString()
    for i in range(1, 5):
        fs.fontSize(i + 10)
        fs.append("a" * i)
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


def test_add(testString):
    new = testString + "XYZ"
    assert len(new.runs) == 4
    assert new != testString


def test_iadd(testString):
    before = testString
    testString += "XYZ"
    assert before is testString
    assert len(testString.runs) == 4
    assert "aaaaaaaaaaXYZ" == testString.text


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


def test_slice():
    testString = FormattedString("abc", fontSize=12)
    testString.append("def", fontSize=13)
    testString.append("h", fontSize=14)
    testString.append("ijk", fontSize=15)

    expected = FormattedString("b", fontSize=12)
    assert expected == testString[1]

    expected = FormattedString("k", fontSize=15)
    assert expected == testString[-1]

    expected = FormattedString("b", fontSize=12)
    assert expected == testString[1:2]

    expected = FormattedString("ab", fontSize=12)
    assert expected == testString[:2]

    expected = FormattedString("bc", fontSize=12)
    assert expected == testString[1:3]

    expected = FormattedString("bc", fontSize=12)
    expected.append("d", fontSize=13)
    assert expected == testString[1:4]

    expected = FormattedString("jk", fontSize=15)
    assert expected == testString[-2:]

    with pytest.raises(TypeError):
        testString[::-1]


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
