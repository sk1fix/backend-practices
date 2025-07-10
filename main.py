class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Entity():
    def __init__(self, x, y):
        self.pozition = Point(x, y)


class Grass(Entity):
    def __init__(self):
        pass

class Rock(Entity):
    def __init__(self):
        pass

class Tree(Entity):
    def __init__(self):
        pass

class Creature(Entity):
    def __init__(self, speed):
        self.speed = speed

    def makeMove():
        pass

class Harbivore(Creature):
    health = 100


class Predator(Creature):
    damage = 25


class Simulation():
    pass

