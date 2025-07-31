from collections import deque
from typing import Optional, List, Tuple, Dict

from point import Point


class Entity():

    def __init__(self, poz: Tuple[int, int]) -> None:
        self.pozition = Point(poz[0], poz[1])

    def get_pozition(self) -> Tuple[int, int]:
        return (self.pozition.x, self.pozition.y)

    def make_hit(self, attacker: object) -> None:
        self.health -= attacker.damage


class Grass(Entity):
    image = ' 🌿 '
    name = 'grass'
    health = 50


class Rock(Entity):
    image = ' 🪨 '
    name = 'rock'


class Tree(Entity):
    image = ' 🌲 '
    name = 'tree'


class Creature(Entity):

    speed = 1

    def make_move(self,
                  path: Tuple[int, int],
                  sim_map: Dict[Tuple[int, int], object]) -> None:
        sim_map[(path[0], path[1])] = self
        del sim_map[self.get_pozition()]

        self.pozition.x = path[0]
        self.pozition.y = path[1]

    def check_meal(self, path: List[Tuple[int, int]]) -> bool:
        if path is None:
            return False
        if path[0] == self.get_pozition() and path[1] == path[-1]:
            return True
        return False

    def get_neighbors(self, poz: Tuple[int, int]) -> List[Tuple[int, int]]:
        my_x, my_y = poz[0], poz[1]
        circle = [[my_x - 1, my_y], [my_x - 1, my_y - 1],
                  [my_x, my_y-1], [my_x + 1, my_y],
                  [my_x, my_y + 1], [my_x + 1, my_y + 1],
                  [my_x + 1, my_y - 1], [my_x - 1, my_y + 1]]
        for i in range(7, -1, -1):
            if (-1 in circle[i]) or (10 in circle[i]):
                circle.pop(i)
        return [tuple(i) for i in circle]

    def bfs(
        self,
        goal: Entity,
        graph: Dict[Tuple[int, int], object]
    ) -> Optional[List[Tuple[int, int]]]:
        queue = deque([[self.get_pozition()]])
        visited = set()

        while queue:
            path = queue.popleft()
            node = path[-1]

            if node in visited:
                continue

            visited.add(node)

            if node in graph:
                if graph[node].name == goal.name:
                    return path
            neighbors = self.get_neighbors(node)

            for neighbor in neighbors:
                if neighbor in graph and graph[neighbor].name != goal.name:
                    continue
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

        return None


class Harbivore(Creature):
    image = ' 🐇 '
    name = 'harbivore'
    damage = 25
    health = 100


class Predator(Creature):
    image = ' 🐺 '
    name = 'predator'
    damage = 25
