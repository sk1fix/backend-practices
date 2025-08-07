import random
import time
from typing import Union

import keyboard

from entity import Rock, Grass, Tree, Predator, Harbivore
from const import (SPAWN_PERIOD_TREE_PREDATOR,
                   STATIC_ENTITY_PERCENTAGE,
                   SPAWN_PERIOD_HARBIVORE)


class Simulation():
    simulation_map = {}
    entity_map = {
        'grass': Grass,
        'rock': Rock,
        'tree': Tree,
        'predator': Predator,
        'harbivore': Harbivore
    }
    count_of_move = 0

    def __init__(self):
        self.x_size, self.y_size = map(int, input(
            'Введите размер карты в формате: x y\n').split(' '))
        square_percentage = int(self.x_size * self.y_size *
                                STATIC_ENTITY_PERCENTAGE)
        self.count_of_entity = {'grass': square_percentage,
                                'rock': square_percentage,
                                'tree': square_percentage}
        self.harbivore_count = int(input('Введите количество травоядных: '))
        self.predator_count = int(input('Введите количество хищников: '))
        self.count_of_entity['harbivore'] = self.harbivore_count
        self.count_of_entity['predator'] = self.predator_count
        self.start()

    def start(self):
        square = self.x_size * self.y_size
        if sum(self.count_of_entity.values()) <= square:
            self.start_similation()
        else:
            while sum(self.simulation_map.values()) > square:
                print(
                    f'Введите меньшее количество существ')
                self.harbivore_count, self.predator_count = map(
                    int, input('В формате H P').split(' '))

    def rendering(self) -> None:
        self.count_of_move += 1
        for entity_type, count in self.count_of_entity.items():
            entity_class = self.entity_map.get(entity_type)
            for _ in range(count):
                position = self.get_random_position()
                self.simulation_map[position] = entity_class(position)

    def get_random_position(self):
        free_positions = [
            (i, j)
            for i in range(self.x_size)
            for j in range(self.y_size)
            if (i, j) not in self.simulation_map
        ]
        if not free_positions:
            return None
        return random.choice(free_positions)

    def next_turn(self) -> None:
        if self.count_of_move == 0:
            self.rendering()
        self.check_fullness()
        positions = list(self.simulation_map.keys())
        for i in positions:
            if i not in self.simulation_map.keys():
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
        pos = self.get_random_position()
        if pos:
            self.simulation_map[pos] = self.entity_map.get(class_name)(pos)

    def action(
        self,
        temp: Union[Predator, Harbivore],
        temp_pred: Union[Grass, Harbivore]
    ) -> None:
        next_step = temp.bfs(temp_pred,
                             self.simulation_map,
                             self.x_size,
                             self.y_size)
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
        count_pos = self.x_size * self.y_size - len(self.simulation_map)
        if not count_pos:
            return
        if self.count_of_move % SPAWN_PERIOD_HARBIVORE == 0\
                and count_pos >= 1:
            self.new_item('harbivore')
            count_pos -= 1
        if self.count_of_move % SPAWN_PERIOD_TREE_PREDATOR == 0\
                and count_pos >= 2:
            self.new_item('tree')
            self.new_item('predator')
            count_pos -= 2
        for i in self.count_of_entity:
            if self.count_of_entity[i] < 2 and count_pos >= 1:
                self.new_item(i)
                count_pos -= 1

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
            free_positions = self.x_size * \
                self.y_size - len(self.simulation_map.keys())

            if not free_positions:
                print("Мест нет")
                break

    def print_map(self) -> None:
        for i in range(self.x_size):
            for j in range(self.y_size):
                if (i, j) in self.simulation_map.keys():
                    print(self.simulation_map[(i, j)].image, end='')
                else:
                    print(' . ', end='')
            print('\n')
        print(f"Количество ходов: {self.count_of_move}")
