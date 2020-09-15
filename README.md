# drawbot-skia

A Python package implementing a subset of the [DrawBot](https://www.drawbot.com) API using [Skia](https://skia.org/) as the backend.

Work in progress!

## Roadmap

1. Get basic shapes working
1. Get basic colors working
1. Get Path object working
1. Get transformations working
1. Get `text()` working
1. Get `FormattedString` working
1. Get pixel image export working (png, jpeg, tiff, ...)
1. Get PDF export working
1. Get SVG export working
1. Get mp4 export working
1. ...
1. Fill gaps in DrawBot API

## Compatibility caveats

Some parts of the DrawBot API will be hard or impractical to duplicate.

Skia has only low level support for text, so we'll have to do Unicode processing, line wrapping and shaping ourselves. In other words, `textBox()` will be a tough one to crack.

Generally, 100% text compatibility with DrawBot should not be top priority, as matching CoreText behavior will be an addition challenge.

The `ImageObject` relies heavily on builtin macOS functionality, and i huge. At best, we should support a small subset of it, but even that is low priority.
