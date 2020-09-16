size(200, 200)

fill(1, 0, 0, 0.5)

with savedState():
    translate(100, 100)
    fill(0.5, 0, 0)
    for i in range(8):
        rect(0, -5, 100, 10)
        rotate(45)
        scale(0.9)

rect(10, 10, 75, 75)
