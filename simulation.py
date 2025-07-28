import random
import time
from typing import Union

import keyboard

from entity import Rock, Grass, Tree, Predator, Harbivore


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
