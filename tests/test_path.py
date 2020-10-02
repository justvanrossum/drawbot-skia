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


def test_path_copy():
    path1 = BezierPath()
    path1.rect(0, 0, 100, 100)
    path2 = path1.copy()
    path1.translate(50, 20)
    assert path1.bounds() == (50.0, 20.0, 150.0, 120.0)
    assert path2.bounds() == (0.0, 0.0, 100.0, 100.0)


def test_path_point_args():
    path1 = BezierPath()
    path1.moveTo([0, 0])
    path1.lineTo([0, 100])
    path1.curveTo([50, 100], [100, 100], [200, 0])


def test_path_line_args():
    path1 = BezierPath()
    path1.line([0, 0], [0, 100])
