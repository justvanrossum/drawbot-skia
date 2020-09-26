values = [
    # sw, lj, lc, dash
    (5, "miter", "butt", [5]),
    (12, "miter", "butt", [5, 10]),
    (8, "round", "round", [8, 10, 15]),
    (5, "round", "round", [0, 7, 7, 7]),
    (5, "round", "round", [None]),  # reset
    (5, "round", "round", []),  # reset
]

size(100, 100 * len(values))

stroke(0)
fill(None)

for sw, lj, lc, dash in values:
    strokeWidth(sw)
    lineJoin(lj)
    lineCap(lc)
    lineDash(*dash)
    polygon((18, 7), (10, 90), (80, 80), (60, 10), close=False)
    translate(0, 100)
