

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Entity():
    def __init__(self, poz):
        self.pozition = Point(poz[0], poz[1])
        
    def get_pozition(self):
        return (self.pozition.x, self.pozition.y)

class Grass(Entity):
    image = ' 🌿 '

class Rock(Entity):
    image = ' 🪨 '

class Tree(Entity):
    image = ' 🌲 '


a = Tree

print(type(a))


# d ={(i, j): 0 for i in range(10) for j in range(10)}


# c = 0
# my_x = 3
# my_y = 3
# circle = [(my_x - 1, my_y), (my_x - 1, my_y - 1), (my_x, my_y-1), (my_x + 1, my_y), (my_x, my_y + 1), (my_x + 1, my_y + 1), (my_x + 1, my_y - 1), (my_x - 1, my_y + 1)]
# for i in circle:
#     if i in d:
#         print('Yes')
#     else: 
#         print('No')


# for i in d:
#     print(i, end='')
#     c+=1
#     if c == 10:
#         print("/n")
#         c=0