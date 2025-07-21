import random
from collections import deque

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

class Creature(Entity):
    
    speed = 2

    def makeMove(self, path, sim_map, image):
        sim_map[self.get_pozition()] = ' . '
        sim_map[(path[0][0], path[0][1])] = image
        self.pozition.x = path[0][0]
        self.pozition.y = path[0][1]

    def check_meal(self, path):
        if path[0] == self.get_pozition() and path[1] == path[-1]:
            return True
        return False

    def get_neighbors(self, poz):
        my_x, my_y = poz[0], poz[1]
        circle = [[my_x - 1, my_y], [my_x - 1, my_y - 1], [my_x, my_y-1], [my_x + 1, my_y], [my_x, my_y + 1], [my_x + 1, my_y + 1], [my_x + 1, my_y - 1], [my_x - 1, my_y + 1]]
        for i in range(7, -1, -1):
            
            if (-1 in circle[i]) or (10 in circle[i]):
                circle.pop(i)
        return [tuple(i) for i in circle]

    def bfs(self, goal, graph):
        queue = deque([[self.get_pozition()]])
        visited = set()
        
        
        while queue:
            path = queue.popleft()  
            node = path[-1]  
    
            if node in visited:  
                continue  
    
            visited.add(node)  
            
            if type(graph[node]) != type(''):
                if graph[node].image == goal:  
                    return path  
            neighbors = self.get_neighbors(node)

            for neighbor in neighbors:  
                if isinstance(graph[neighbor], Rock) or isinstance(graph[neighbor], Tree):
                    continue
                new_path = list(path) 
                new_path.append(neighbor)  
                queue.append(new_path)  
    
        return None  

    
        

class Harbivore(Creature):
    image = ' 🐇 '
    health = 100



class Predator(Creature):
    image = ' 🐺 '
    damage = 25


class Simulation():
    simulation_map = {(i, j): ' . ' for i in range(10) for j in range(10)}
    count_of_move = 0
    
    def rendering(self):
        temp_map = self.simulation_map.copy()
        for i in range(5):
            pozitions = random.sample(sorted(temp_map.keys()), 5)
            self.simulation_map[pozitions[0]] = Rock(pozitions[0])
            self.simulation_map[pozitions[1]] = Grass(pozitions[1])
            self.simulation_map[pozitions[2]] = Tree(pozitions[2])
            self.simulation_map[pozitions[3]] = Predator(pozitions[3])
            self.simulation_map[pozitions[4]] = Harbivore(pozitions[4])
            for key in pozitions:
                del temp_map[key]

    def next_turn(self):
        pass

    def start_similation(self):
        pass

    def pause_simulation(self):
        pass

    def print_map(self):
        for i in range(10):
            for j in range(10):
                if type(self.simulation_map[(i, j)]) == type(''):
                    print(self.simulation_map[(i, j)], end='')
                else:
                    print(self.simulation_map[(i, j)].image, end='')
            print('\n')

a = Simulation()
a.rendering()
a.print_map()
for i in a.predators:
    print(i.bfs(' 🐇 ', a.simulation_map))
