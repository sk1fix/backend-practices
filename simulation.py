import random
import time
from typing import Union

import keyboard

from entity import Rock, Grass, Tree, Predator, Harbivore


class Simulation():
    simulation_map = {}
    count_of_entity = {'grass': 5, 'harbivore': 5}
    entity_map = {
        'grass': Grass,
        'rock': Rock,
        'tree': Tree,
        'predator': Predator,
        'harbivore': Harbivore
    }
    count_of_move = 0

    def rendering(self) -> None:
        self.count_of_move += 1
        for i in range(5):
            rock = self.get_random_position()
            self.simulation_map[rock] = Rock(rock)
            grass  = self.get_random_position()
            self.simulation_map[grass] = Grass(grass)
            tree = self.get_random_position()
            self.simulation_map[tree] = Tree(tree)
            predator = self.get_random_position()
            self.simulation_map[predator] = Predator(predator)
            harbivore = self.get_random_position()
            self.simulation_map[harbivore] = Harbivore(harbivore)

    def get_random_position(self):
        a = random.randint(0, 9)
        b = random.randint(0, 9)
        if len(self.simulation_map) == 100:
            return None
        elif (a, b) in self.simulation_map:
            return self.get_random_position()
        else:
            return (a, b)
    def next_turn(self) -> None:
        if self.count_of_move == 0:
            self.rendering()
        self.check_fullness()
        positions = list(self.simulation_map.keys())
        for i in positions:
            if i not in self.simulation_map:
                continue
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
        poz = self.get_random_position()
        if not poz:
            return None
        else:
            self.simulation_map[poz] = self.entity_map.get(class_name)(poz)

    def action(
        self,
        temp: Union[Predator, Harbivore],
        temp_pred: Union[Grass, Harbivore]
    ) -> None:
        next_step = temp.bfs(temp_pred, self.simulation_map)
        if next_step is None:
            return
        if temp.check_meal(next_step):
            self.simulation_map[next_step[1]].make_hit(temp)
            if self.simulation_map[next_step[1]].health == 0:
                self.count_of_entity[
                    self.simulation_map[next_step[1]].name] -= 1
                del self.simulation_map[next_step[1]]
        else:
            temp.make_move(next_step[1], self.simulation_map)

    def check_fullness(self) -> None:
        count_poz = 100 - len(self.simulation_map)
        if not count_poz:
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
            free_positions = 100 - len(self.simulation_map)

            if not free_positions:
                print("Мест нет")
                break

    def print_map(self) -> None:
        for i in range(10):
            for j in range(10):
                if (i, j) in self.simulation_map:
                    print(self.simulation_map[(i, j)].image, end='')
                else:
                    print(' . ', end='')
            print('\n')
        print(f"Количество ходов: {self.count_of_move}")
