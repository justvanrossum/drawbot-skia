from drawbot_skia.runner import makeDrawbotNamespace, runScript, runScriptSource
from drawbot_skia.drawing import Drawing
import pathlib
import pytest
from PIL import Image
import numpy as np


testDir = pathlib.Path(__file__).resolve().parent
apiTestsDir = testDir / "apitests"
apiTestsOutputDir = testDir / "apitests_output"
apiTestsExpectedOutputDir = testDir / "apitests_expected_output"


apiScripts = apiTestsDir.glob("*.py")


@pytest.mark.parametrize("apiTestPath", apiScripts)
def test_apitest(apiTestPath):
    db = Drawing()
    namespace = makeDrawbotNamespace(db)
    runScript(apiTestPath, namespace)
    if not apiTestsOutputDir.exists():
        apiTestsOutputDir.mkdir()
    outputPath = apiTestsOutputDir / (apiTestPath.stem + ".png")
    expectedOutputPath = apiTestsExpectedOutputDir / (apiTestPath.stem + ".png")
    db.saveImage(outputPath)
    same, reason = compareImages(outputPath, expectedOutputPath)
    assert same, reason


multipageSource = """
for i in range(3):
    newPage(200, 200)
    rect(50, 50, 100, 100)
"""


def test_saveImage_multipage(tmpdir):
    tmpdir = pathlib.Path(tmpdir)
    db = Drawing()
    namespace = makeDrawbotNamespace(db)
    runScriptSource(multipageSource, "<string>", namespace)
    assert [] == sorted(tmpdir.glob("*.png"))
    outputPath = tmpdir / "test.png"
    db.saveImage(outputPath)
    expected_filenames = ['test_0.png', 'test_1.png', 'test_2.png']
    assert expected_filenames == [p.name for p in sorted(tmpdir.glob("*.png"))]


def test_saveImage_mp4(tmpdir):
    from drawbot_skia import ffmpeg
    from pyffmpeg import FFMPEG_FILE
    ffmpeg.FFMPEG_PATH = FFMPEG_FILE  # Force ffmpeg from pyffmpeg
    tmpdir = pathlib.Path(tmpdir)
    db = Drawing()
    namespace = makeDrawbotNamespace(db)
    runScriptSource(multipageSource, "<string>", namespace)
    assert [] == sorted(tmpdir.glob("*.png"))
    outputPath = tmpdir / "test.mp4"
    db.saveImage(outputPath)
    expected_filenames = ['test.mp4']
    assert expected_filenames == [p.name for p in sorted(tmpdir.glob("*.mp4"))]


def test_noFont(tmpdir):
    db = Drawing()
    # Ensure we don't get an error when font is not set
    db.text("Hallo", (0, 0))


def readbytes(path):
    with open(path, "rb") as f:
        return f.read()


def compareImages(path1, path2):
    data1 = readbytes(path1)
    data2 = readbytes(path2)
    if data1 == data2:
        return True, "data identical"
    im1 = Image.open(path1)
    im2 = Image.open(path2)
    if im1 == im2:
        return True, "images identical"
    if im1.size != im2.size:
        return False, "sizes differ"
    a1 = np.array(im1).astype(int)
    a2 = np.array(im2).astype(int)
    diff = a1 - a2
    maxDiff = max(abs(np.max(diff)), abs(np.min(diff)))
    if maxDiff < 128:
        return True, "images similar enough"
    return False, f"images differ too much, maxDiff: {maxDiff}"
