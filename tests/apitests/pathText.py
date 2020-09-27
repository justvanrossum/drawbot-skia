from random import randint, random, seed

size(200, 100)

fill(1)
rect(0, 0, 200, 100)

fill(0)
path = BezierPath()
path.text("fiets", offset=(9, 18), font="../fonts/SourceSerifPro-Regular.otf", fontSize=95)

clipPath(path)

seed(8)

for i in range(79):
    fill(random(), random(), 0.5, random())
    oval(randint(0, 160), randint(0, 160), 40, 40)
