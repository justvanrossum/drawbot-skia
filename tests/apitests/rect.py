size(200, 200)

for i in range(14):
    f = i / 14.0
    fill(f, 1 - f, 0)
    rect(10, 10, 50, 50)
    translate(10, 10)
