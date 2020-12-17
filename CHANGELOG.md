# Changelog for drawbot-skia

## [0.4.6] - 2020-12-17

- Added `listFontVariations()` ([#10](https://github.com/justvanrossum/drawbot-skia/issues/10))
- Added `listNamedInstances()`
- Implemented `newDrawing()`, so multiple documents can be created in one run.

## [0.4.5] - 2020-10-17

- Added PointPen behavior to BezierPath ([#9](https://github.com/justvanrossum/drawbot-skia/pull/9), thanks Jens Kutilek!)

## [0.4.4] - 2020-10-04

- Fixed `mp4` export with Python 3.6 on Windows

## [0.4.3] - 2020-10-03

- Added `svg` export support for `saveImage()`
- Added `path.line(pt1, pt2)`
- Added `shadow()`, but it is not 100% compatible with DrawBot's in some unavoidable ways.

## [0.4.2] - 2020-10-02

- Pinned optional pyffmpeg requirement to 1.6.1 for now.
- Added `linearGradient(...)`
- Added `radialGradient(...)` (limited to a single center point and a zero start radius)
- Add `random`, `randint`, `choice` and `shuffle` from the random module to the default namespace.

## [0.4.1] - 2020-10-01

- Fixed a serious issue with the graphics state and multiple pages, that caused wrong paint properties on pages after the first.

## [0.4.0] - 2020-09-30

- Added `frameDuration(duration)`
- Added `mp4` export support for `saveImage()`

## [0.3.1] - 2020-09-27

- Added `path.removeOverlap()`
- Added `path.union(other)` and `path.__or__(other)`
- Added `path.intersection(other)` and `path.__and__(other)`
- Added `path.difference(other)` and `path.__mod__(other)`
- Added `path.xor(other)` and `path.__xor__(other)`

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
