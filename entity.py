from collections import deque
from typing import Optional, List, Tuple, Dict
from abc import abstractmethod, ABC

from point import Point


class Entity(ABC):

    def __init__(self, pos: Tuple[int, int]) -> None:
        self.position = Point(pos[0], pos[1])

    def get_position(self) -> Tuple[int, int]:
        return (self.position.x, self.position.y)


class Prey(ABC):
    def make_hit(self, attacker: object) -> None:
        self.health -= attacker.damage


class Grass(Entity, Prey):
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
        del sim_map[self.get_position()]

        self.position.x = path[0]
        self.position.y = path[1]

    def check_meal(self, path: List[Tuple[int, int]]) -> bool:
        if path is None:
            return False
        if path[0] == self.get_position() and path[1] == path[-1]:
            return True
        return False

    def get_neighbors(
        self,
        poz: Tuple[int, int],
        x: int,
        y: int
    ) -> List[Tuple[int, int]]:
        my_x, my_y = poz[0], poz[1]
        circle = [[my_x - 1, my_y], [my_x - 1, my_y - 1],
                  [my_x, my_y-1], [my_x + 1, my_y],
                  [my_x, my_y + 1], [my_x + 1, my_y + 1],
                  [my_x + 1, my_y - 1], [my_x - 1, my_y + 1]]
        return [(i, j) for i, j in circle if 0 <= i < x and 0 <= j < y]

    def bfs(
        self,
        goal: Entity,
        graph: Dict[Tuple[int, int], object],
        x: int,
        y: int
    ) -> Optional[List[Tuple[int, int]]]:
        queue = deque([[self.get_position()]])
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
            neighbors = self.get_neighbors(node, x, y)

            for neighbor in neighbors:
                if neighbor in graph.keys() and graph[
                    neighbor
                ].name != goal.name:
                    continue
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

        return None


class Harbivore(Creature, Prey):
    image = ' 🐇 '
    name = 'harbivore'
    damage = 25
    health = 100


class Predator(Creature):
    image = ' 🐺 '
    name = 'predator'
    damage = 25
