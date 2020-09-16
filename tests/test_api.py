from drawbot_skia.runner import makeDrawbotNamespace, runScript, runScriptSource
from drawbot_skia.drawing import Drawing
import pathlib
import pytest


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
    compareImages(outputPath, expectedOutputPath)


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


def readbytes(path):
    with open(path, "rb") as f:
        return f.read()


def compareImages(path1, path2):
    data1 = readbytes(path1)
    data2 = readbytes(path2)
    assert data1 == data2
