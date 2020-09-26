from drawbot_skia.path import BezierPath


def test_path_bounds():
    path = BezierPath()
    assert path.bounds() is None
    path.rect(10, 20, 30, 40)
    assert path.bounds() == (10, 20, 40, 60)


def test_path_controlPointBounds():
    path = BezierPath()
    assert path.controlPointBounds() is None
    path.moveTo((0, 0))
    path.curveTo((50, 100), (100, 100), (150, 0))
    assert path.bounds() == (0.0, 0.0, 150.0, 75.0)
    assert path.controlPointBounds() == (0.0, 0.0, 150.0, 100.0)
