modes = [
    'normal',
    'multiply',
    'screen',
    'overlay',
    'darken',
    'lighten',
    'colorDodge',
    'colorBurn',
    'softLight',
    'hardLight',
    'difference',
    'exclusion',
    'hue',
    'saturation',
    'color',
    'luminosity',
    # 'clear',
    # 'copy',
    # 'sourceIn',
    # 'sourceOut',
    # 'sourceAtop',
    # 'destinationOver',
    # 'destinationIn',
    # 'destinationOut',
    # 'destinationAtop',
    # 'xOR',
    # 'plusDarker',
    # 'plusLighter',
]

cellSize = 100
size(cellSize, cellSize * len(modes))
fill(0.5)
rect(0, 0, width(), height())

for mode in modes:
    blendMode(mode)

    fill(0, 0.4, 1)
    rect(0, 0, 0.75 * cellSize, 0.75 * cellSize)
    fill(1, 0, 0.4)
    rect(0.25 * cellSize, 0.25 * cellSize, 0.75 * cellSize, 0.75 * cellSize)
    translate(0, cellSize)
