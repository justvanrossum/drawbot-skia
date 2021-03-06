[![Run tests](https://github.com/justvanrossum/drawbot-skia/workflows/Run%20tests/badge.svg)](https://github.com/justvanrossum/drawbot-skia/actions)

# drawbot-skia

A Python package implementing a subset of the [DrawBot](https://www.drawbot.com) API using [Skia](https://skia.org/) as a backend.

Work in progress!

## Roadmap

1. Get basic shapes working ✅
1. Get basic colors working ✅
1. Get minimal `BezierPath` object working ✅
1. Get transformations working ✅
1. Get single-line, single style `text()` working ✅
1. Get Variable Fonts working ✅
1. Get HarfBuzz shaping working ✅
1. Get OpenType features working ✅
1. Get PNG, JPEG image export working ✅
1. Get PDF export working ✅
1. Get MP4 export working ✅
1. Get SVG export working ✅
1. Get Animated GIF export working
1. Get multi-line, single style `text()` working
1. Get `FormattedString` working
1. Get multi-style `text()` working
1. Get remaining `BezierPath` methods working
1. Get many-things-I-forgot-to-mention working
1. ...
1. `textBox()` 🔴 _(Major Obstacle)_
1. Fill further gaps in DrawBot API

The currently supported subset of Drawbot is [tracked here](https://github.com/justvanrossum/drawbot-skia/issues/5).

## Vision

This project is purely a Python package that implements (part of) the DrawBot drawing API. Using Skia ([skia-python](https://github.com/kyamagu/skia-python)) ensures this can be done in a cross-platform way.

A DrawBot-like cross-platform application shell can be developed, but that would be a separate project. Looking forward to the `drawbot-qt`, `drawbot-wx`, `drawbot-win` or any `drawbot-*` projects of the future!

## Compatibility caveats

Some parts of the DrawBot API will be hard or impractical to duplicate.

Skia has only low level support for text, so we'll have to do Unicode processing, line wrapping, hyphenation, and shaping ourselves. In other words, `textBox()` will be a tough one to crack.

Generally, 100% text compatibility with DrawBot should not be top priority, as matching CoreText behavior will be a huge challenge.

The `ImageObject` relies heavily on builtin macOS functionality, and it is huge. At best, we should support a small subset of it, but even that is low priority.

## Strategy

So far no existing DrawBot code has been reused. Perhaps that small snippets will be copied, perhaps a part of the test suite will be adapted. Other than that I want this to be an independent project, and would like to use Skia’s powers to maximum effect, keeping efficiency and performance in mind. DrawBot's ties to macOS are so strong that it makes platform-neutral code reuse virtually impossible.

Potentially, some higher level code could be shared (for example, drawing code that uses lower level primitives), but that will have to been seen later.

## Install

The quickest way to install the latest release is with pip:

`pip install drawbot-skia`

_Note for Windows: skia-python is only supported for the 64-bit version of Python, so that goes for drawbot-skia as well, so make sure you use one of the x86-64 Python installers._

If you want to see the source code and possibly contribute: clone the repo, and do `pip install -e .` in the root directory.

## Usage

To adapt a DrawBot script to `drawbot-skia` you can do a couple of things:

- Add `from drawbot_skia.drawbot import *` at the top of your script
- Or `import drawbot_skia.drawbot as db` if that's your preferred style

Or you can use the `drawbot` runner tool from the command line:

- `drawbot mydrawbotscript.py output.png`

With the `drawbot` runner tool, you won't need any Drawbot import in the script, nor do you need a `saveImage(...)` to export results. It pretty much behaves as if you hit "Run" in the classic Drawbot application.
