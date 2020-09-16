import pathlib
import subprocess


testDir = pathlib.Path(__file__).resolve().parent
testScript = testDir / "apitests" / "oval.py"


def test_runner_app(tmpdir):
    outputPath = pathlib.Path(tmpdir / "test.png")
    assert not outputPath.exists()
    # assert 0, outputPath
    args = ["drawbot", testScript, outputPath]
    subprocess.check_output(args)
    assert outputPath.exists()
