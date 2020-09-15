from drawbot_skia.runner import makeDrawbotNamespace, runScript
from drawbot_skia.drawbot import Drawbot
import pathlib
import pytest


testDir = pathlib.Path(__file__).resolve().parent
apiTestsDir = testDir / "apitests"
apiTestsOutputDir = testDir / "apitests_output"
apiTestsExpectedOutputDir = testDir / "apitests_expected_output"


apiScripts = apiTestsDir.glob("*.py")


@pytest.mark.parametrize("apiTestPath", apiScripts)
def test_foo(apiTestPath):
    db = Drawbot()
    namespace = makeDrawbotNamespace(db)
    runScript(apiTestPath, namespace)
    if not apiTestsOutputDir.exists():
        apiTestsOutputDir.mkdir()
    outputPath = apiTestsOutputDir / (apiTestPath.stem + ".png")
    expectedOutputPath = apiTestsExpectedOutputDir / (apiTestPath.stem + ".png")
    db.saveImage(outputPath)
    compareImages(outputPath, expectedOutputPath)


def readbytes(path):
    with open(path, "rb") as f:
        return f.read()


def compareImages(path1, path2):
    data1 = readbytes(path1)
    data2 = readbytes(path2)
    assert data1 == data2
