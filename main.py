import random
import time
from collections import deque
from typing import Optional, List, Tuple, Dict

import keyboard


class Point():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


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
        sim_map[self.get_pozition()] = ' . '

        self.pozition.x = path[0]
        self.pozition.y = path[1]

    def check_meal(self, path: Tuple[int, int]) -> bool:
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
        goal: str,
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

            if type(graph[node]) != type(''):
                if graph[node].image == goal:
                    return path
            neighbors = self.get_neighbors(node)

            for neighbor in neighbors:
                if isinstance(graph[neighbor], (Rock, Tree, Predator)):
                    continue
                if self.name == 'predator' and \
                        isinstance(graph[neighbor], Grass):
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


class Simulation():
    simulation_map = {(i, j): ' . ' for i in range(10) for j in range(10)}
    count_of_entity = {'grass': 5, 'harbivore': 5}
    entity_map = {
        'grass': Grass,
        'rock': Rock,
        'tree': Tree,
        'predator': Predator,
        'harbivore': Harbivore
    }
    count_of_move = 0
    health = 100

    def rendering(self) -> None:
        self.count_of_move += 1
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

    def next_turn(self) -> None:
        if self.count_of_move == 0:
            self.rendering()
        self.check_fullness()
        for i in self.simulation_map:
            temp = self.simulation_map[i]
            if isinstance(temp, Harbivore):
                temp_purpose = Grass
                self.action(temp, temp_purpose)
            elif isinstance(temp, Predator):
                temp_purpose = Harbivore
                self.action(temp, temp_purpose)
            else:
                continue
        self.count_of_move += 1
        self.print_map()

    def new_item(self, class_name: str) -> None:
        list_keys = list(self.simulation_map.keys())
        free_positions = [
            key for key,
            value in self.simulation_map.items() if value == ' . ']
        poz = random.choice(free_positions)
        if not free_positions:
            return None
        else:
            self.simulation_map[poz] = self.entity_map.get(class_name)(poz)

    def action(self, temp: object, temp_pred: object) -> None:
        next_step = temp.bfs(temp_pred.image, self.simulation_map)
        if next_step is None:
            return
        if temp.check_meal(next_step):
            self.simulation_map[next_step[1]].make_hit(temp)
            if self.simulation_map[next_step[1]].health == 0:
                self.count_of_entity[
                    self.simulation_map[next_step[1]].name] -= 1
                self.simulation_map[next_step[1]] = ' . '
        else:
            temp.make_move(next_step[1], self.simulation_map)

    def check_fullness(self) -> None:
        free_positions = [
            key for key,
            value in self.simulation_map.items() if value == ' . ']
        count_poz = len(free_positions)
        if not free_positions:
            return
        if self.count_of_move % 3 == 0 and count_poz >= 1:
            self.new_item('harbivore')
            count_poz -= 1
        if self.count_of_move % 10 == 0 and count_poz >= 2:
            self.new_item('tree')
            self.new_item('predator')
            count_poz -= 2
        for i in self.count_of_entity:
            if self.count_of_entity[i] < 2 and count_poz >= 1:
                self.new_item(i)
                count_poz -= 1

    def start_similation(self) -> None:
        if self.count_of_move == 0:
            self.rendering()
            self.print_map()

        paused = False
        while True:
            if not paused:
                self.next_turn()
                time.sleep(0.5)

            if keyboard.is_pressed('p'):
                paused = not paused
                print("\nПауза включена" if paused else "\nПауза снята")
                time.sleep(0.5)
            if keyboard.is_pressed('n') and paused:
                self.next_turn()
                time.sleep(0.5)
            if keyboard.is_pressed('s'):
                print('\nСимуляция завершена')
                return None
            free_positions = [
                key for key,
                value in self.simulation_map.items() if value == ' . ']

            if not free_positions:
                print("Мест нет")
                break

    def print_map(self) -> None:
        for i in range(10):
            for j in range(10):
                if type(self.simulation_map[(i, j)]) == type(''):
                    print(self.simulation_map[(i, j)], end='')
                else:
                    print(self.simulation_map[(i, j)].image, end='')
            print('\n')
        print(f"Количество ходов: {self.count_of_move}")


if __name__ == '__main__':
    a = Simulation()
    a.start_similation()
