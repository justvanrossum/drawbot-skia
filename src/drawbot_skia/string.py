from bisect import bisect
from typing import NamedTuple
from .gstate import FillPaint, StrokePaint, TextStyle, GraphicsStateMixin


class FormattedString(GraphicsStateMixin):

    def __init__(self, text=None, runs=None, **properties):
        self.runs = []
        self._runCharIndices = None
        if runs:
            if text is not None or properties:
                raise TypeError("can't pass text or properties when initializing from runs")
            self._appendRuns(runs)
        else:
            self.textStyle = TextStyle()
            self.fillPaint = FillPaint()
            self.strokePaint = StrokePaint(somethingToDraw=False)
            self.append(text, **properties)

    def copy(self):
        copy = FormattedString(runs=self.runs)
        # Ok to share these, they are copy-on-write, see GraphicsStateMixin
        copy.textStyle = self.textStyle
        copy.fillPaint = self.fillPaint
        copy.strokePaint = self.strokePaint
        return copy

    def append(self, text, **properties):
        self._runCharIndices = None
        if isinstance(text, FormattedString):
            if properties:
                raise TypeError("can't pass properties when appending FormattedString")
            self._appendRuns(list(text.runs))  # Copy, just in case text is self
            return
        self._applyProperties(properties)
        if not text:
            return
        self._appendRun(TextRun(text, self.textStyle, self.fillPaint, self.strokePaint))

    def _appendRuns(self, runs):
        if not runs:
            return
        self._appendRun(runs[0])
        self.runs.extend(runs[1:])
        lastRun = runs[-1]
        self.textStyle = lastRun.textStyle
        self.fillPaint = lastRun.fillPaint
        self.strokePaint = lastRun.strokePaint

    def _appendRun(self, run):
        if self.runs:
            lastRun = self.runs[-1]
            if (lastRun.textStyle == run.textStyle
                    and lastRun.fillPaint == run.fillPaint
                    and lastRun.strokePaint == run.strokePaint):
                self.runs[-1] = lastRun.addText(run.text)
                return
        self.runs.append(run)

    def _applyProperties(self, properties):
        for prop, value in properties.items():
            method = getattr(self, prop, None)
            if method is None:
                raise TypeError(f"FormattedString does not have a '{prop}' property")
            if isinstance(value, dict):
                method(**value)
            elif isinstance(value, (tuple, list)):
                method(*value)
            else:
                method(value)

    def __eq__(self, other):
        if not isinstance(other, FormattedString):
            return NotImplemented
        return (self.runs == other.runs
                and self.textStyle == other.textStyle
                and self.fillPaint == other.fillPaint
                and self.strokePaint == other.strokePaint)

    def __add__(self, other):
        result = self.copy()
        result.append(other)
        return result

    def __iadd__(self, other):
        self.append(other)
        return self

    def __len__(self):
        return self.runCharIndices[-1]

    def __getitem__(self, indexOrSlice):
        if isinstance(indexOrSlice, int):
            index = indexOrSlice
            if index < 0:
                index += len(self)
            if not (0 <= index < len(self)):
                raise IndexError(f"index {indexOrSlice} out of range")
            startRunIndex = self.findRunIndex(index)
            runStart = self.runCharIndices[startRunIndex]
            runs = [self.runs[startRunIndex][index - runStart]]
        else:
            slc = indexOrSlice
            start, stop, step = slc.indices(len(self))
            if step != 1:
                raise TypeError(f"FormattedString slicing does not support step != 1 ({step})")
            startRunIndex = self.findRunIndex(start)
            if stop == len(self):
                stopRunIndex = len(self.runs) - 1
            else:
                stopRunIndex = self.findRunIndex(stop)
            runStart = self.runCharIndices[startRunIndex]
            runStop = self.runCharIndices[stopRunIndex]
            if startRunIndex == stopRunIndex:
                runs = [self.runs[startRunIndex][start - runStart:stop - runStop]]
            else:
                runs = []
                runs.append(self.runs[startRunIndex][start - runStart:])
                runs.extend(self.runs[startRunIndex + 1: stopRunIndex])
                stopSlice = self.runs[stopRunIndex][:stop - runStop]
                if stopSlice:
                    runs.append(stopSlice)
        return FormattedString(runs=runs)

    def splitlines(self, keepends=False):
        currentLine = []
        lines = []
        for item in self.runs:
            runParts = item.splitlines(keepends)
            assert runParts
            if len(runParts) == 1:
                currentLine.extend(runParts)
            else:
                lines.append(currentLine + runParts[:1])
                for p in runParts[1:-1]:
                    lines.append([p])
                currentLine = runParts[-1:]
        if currentLine:
            lines.append(currentLine)
        return [FormattedString(runs=runs) for runs in lines]

    def join(self, items):
        result = FormattedString()
        if items:
            result.append(items[0])
            for item in items[1:]:
                result.append(self)
                result.append(item)
        return result

    @property
    def text(self):
        return "".join(item.text for item in self.runs)

    @property
    def runCharIndices(self):
        if self._runCharIndices is None:
            pos = 0
            indices = [pos]
            for run in self.runs:
                pos += len(run.text)
                indices.append(pos)
            self._runCharIndices = indices
        return self._runCharIndices

    def findRunIndex(self, characterIndex, previousRunIndex=None):
        """Given the index of a character into the total string that
        'self' represents, return the index of the run that contains
        the character.

        This is needed to retrieve the formatting information needed to
        render a glyph from a shaped glyph sequence, which may cover
        multiple runs. The cluster number that HarfBuzz gives us is the
        character index.

        When iterating over the shaped glyphs, the requested run index
        for a glyph is likely to be close to the run index returned for
        the previous glyph: either the it is part of the same run, or of
        the run before it or after it.

        findRunIndex() can often find the run index faster if it knows
        the previously returned run index. This is what the
        `previousRunIndex` argument is for.
        """
        numRuns = len(self.runs)
        if numRuns == 1:
            # Better: the caller optimizes for this
            return 0
        runCharIndices = self.runCharIndices
        assert 0 <= characterIndex < runCharIndices[-1]
        assert len(runCharIndices) == numRuns + 1
        runIndex = previousRunIndex
        if runIndex is None:
            # Common case: it's the first or last run
            if characterIndex < runCharIndices[1]:
                return 0
            elif characterIndex >= runCharIndices[-2]:
                return numRuns - 1
            # else: fall through, do binary search
        else:
            assert 0 <= runIndex < numRuns
            if runIndex > 0 and characterIndex < runCharIndices[runIndex]:
                # Maybe it's the previous run
                runIndex -= 1
            elif characterIndex >= runCharIndices[runIndex + 1]:
                # Maybe it's the next run
                runIndex += 1  # can't overflow because of the first assert
            if not (runCharIndices[runIndex] <= characterIndex < runCharIndices[runIndex + 1]):
                # If it isn't the same run, the previous run, or the next run,
                # give up and do a binary search.
                runIndex = None
        if runIndex is None:
            runIndex = bisect(runCharIndices, characterIndex) - 1
            assert 0 <= runIndex < numRuns
        return runIndex

    def iterSplitForShaping(self):
        #
        # Font attrs that split shaping:
        #   font
        #   fontSize
        #   lineHeight
        #   fontVariations
        #   baselineShift (???)
        #
        # Font attrs that won't split shaping:
        #   align
        #   tracking
        #   openTypeFeatures
        #   baselineShift (???)
        #
        # Paint attrs will never split shaping
        #
        return self.iterSplit({"font", "fontSize", "lineHeight", "variations"})

    def iterSplit(self, textProperties):
        prevRun = None
        currentRuns = []
        for run in self.runs:
            if (prevRun is not None and any(
                    getattr(prevRun.textStyle, prop) != getattr(run.textStyle, prop)
                    for prop in textProperties)):
                yield FormattedString(runs=currentRuns)
                currentRuns = []
            currentRuns.append(run)
            prevRun = run
        if currentRuns:
            yield FormattedString(runs=currentRuns)


class TextRun(NamedTuple):

    text: str
    textStyle: TextStyle
    fillPaint: FillPaint
    strokePaint: StrokePaint

    def addText(self, text):
        return TextRun(self.text + text, self.textStyle, self.fillPaint, self.strokePaint)

    def __len__(self):
        return len(self.text)

    def __getitem__(self, indexOrSlice):
        return TextRun(self.text[indexOrSlice], self.textStyle, self.fillPaint, self.strokePaint)

    def rsplit(self, sep=None, maxsplit=-1):
        return self._buildSplitParts(self.text.rsplit(sep, maxsplit))

    def split(self, sep=None, maxsplit=-1):
        return self._buildSplitParts(self.text.split(sep, maxsplit))

    def splitlines(self, keepends=False):
        return self._buildSplitParts(self.text.splitlines(keepends))

    def _buildSplitParts(self, parts):
        return [TextRun(t, self.textStyle, self.fillPaint, self.strokePaint) for t in parts]
