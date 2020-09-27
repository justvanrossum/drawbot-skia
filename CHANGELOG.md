# Changelog for drawbot-skia

## [0.3.0] - 2020-09-27

- Added `clipPath(path)`
- Added `path.pointInside(point)`
- Added `path.bounds()`
- Added `path.controlPointBounds()`
- Added `path.reverse()`
- Added `path.appendPath(other)`
- Added `path.copy()`
- Added `path.translate(x, y)`
- Added `path.scale(x, y=None, center=(0, 0))`
- Added `path.rotate(angle, center=(0, 0))`
- Added `path.skew(x, y=0, center=(0, 0))`
- Added `path.transform(transform, center=(0, 0))`
- Added `path.arc(center, radius, startAngle, endAngle, clockwise)`
- Added `path.arcTo(point1, point2, radius)`
- Added `path.drawToPen(pen)`
- Added `path.drawToPointPen(pen)`
- Added `path.text(txt, ...)`
- Fixed bug when `font()` was not set

## [0.2.0] - 2020-09-26

- Added `image(imagePath, position, alpha=1.0)`
- Added `language(language)`
- Fixed signature of `transform(matrix, center=(0, 0))`
- Added `blendMode(blendMode)`
- Added `lineDash(firstValue, *values)`

## [0.1.1] - 2020-09-22

Second first release on PyPI

## [0.1.0] - 2020-09-22

First first release on PyPI
