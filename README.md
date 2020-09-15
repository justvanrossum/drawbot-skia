# drawbot-skia

A Python package implementing a subset of the [DrawBot](https://www.drawbot.com) API using [Skia](https://skia.org/) as a backend.

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

## Vision

This project is purely a Python package that implements (part of) the DrawBot drawing API. Using Skia ([skia-python](https://github.com/kyamagu/skia-python)) ensures this can be done in a cross-platform way.

A DrawBot-like cross-platform application shell can be developed, but that should be a separate project. Looking forward to the `drawbot-qt`, `drawbot-wx`, `drawbot-win` or any `drawbot-*` projects of the future!

## Compatibility caveats

Some parts of the DrawBot API will be hard or impractical to duplicate.

Skia has only low level support for text, so we'll have to do Unicode processing, line wrapping and shaping ourselves. In other words, `textBox()` will be a tough one to crack.

Generally, 100% text compatibility with DrawBot should not be top priority, as matching CoreText behavior will be a huge challenge.

The `ImageObject` relies heavily on builtin macOS functionality, and it is huge. At best, we should support a small subset of it, but even that is low priority.

## Strategy

So far no existing DrawBot code has been reused. Perhaps that small snippets will be copied, perhaps a part of the test suite will be adapted. Other than that I want this to be an independent project, and would like to use Skia’s powers to maximum effect, keeping efficiency and performance in mind. DrawBot's ties to macOS are so strong that it makes platform-neutral code reuse virtually impossible.

Potentially, some higher level code could be shared (for example, drawing code that uses lower level primitives), but that will have to been seen later.
