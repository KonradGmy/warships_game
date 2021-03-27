import math
import random

import Camera

import Controller
from Maths import two_points_length


class Strategy:
    def __init__(self, ship):
        self.ship = ship

    def tick(self):
        pass


class PlayerControlled(Strategy):
    def __init__(self, ship):
        super().__init__(ship)
        self.targets = []
        for gun in ship.guns:
            gun.target = None

    def __str__(self):
        return "PlayerControlled"

    def tick(self):
        for target in self.targets:
            if target.hp < 0:
                self.targets.remove(target)

        def set_targets():
            diffs = []
            for target in self.targets:
                if target.hp > 0:
                        diffs.append(((target, Controller.fleet.index(target)), gun.diff_angle_to(target, self.ship.heading)[1]))
            if diffs:
                gun.target = Controller.fleet[min(diffs, key=lambda x: abs(x[1]))[0][1]]
            else:
                gun.target = None

        if not self.ship.bridge.destroyed and Camera.time % 5 - Camera.game_factor < 0:
            for gun in self.ship.guns:
                set_targets()


class Search(Strategy):
    def __init__(self, ship, bot_advantage):
        super().__init__(ship)
        self.target = None
        self.bot_advantage = bot_advantage
        self.vector = [random.randint(-400, 400), random.randint(-400, 400)]
        self.tick()

    def __str__(self):
        return "Reduce distance"

    def tick(self):
        def find_targets():
            targets = []
            for i_ship in range(len(Controller.fleet)):
                if Controller.fleet[i_ship] != self.ship and Controller.fleet[i_ship].bot is not True:
                    if self.bot_advantage:
                        dist = two_points_length(Controller.fleet[i_ship].position, self.ship.position)
                        targets.append((dist, i_ship))
                    else:
                        hp = Controller.fleet[i_ship].hp
                        if hp > 0:
                            targets.append((hp, i_ship))
            if targets:
                return Controller.fleet[min(targets, key=lambda x: x[0])[1]]

        self.target = find_targets()
        if self.target:
            self.ship.course_array = [(self.target.position[0] + self.vector[0], self.target.position[1] + self.vector[1])]


class Destroy(Strategy):
    def __init__(self, ship):
        super().__init__(ship)
        self.main_target = None
        self.clockwise = random.random()

    def __str__(self):
        return "Destroy"

    def tick(self):
        def find_targets():
            targets = []
            for i_ship in range(len(Controller.fleet)):
                if Controller.fleet[i_ship] != self.ship and Controller.fleet[i_ship].bot is not True:
                    dist = two_points_length(Controller.fleet[i_ship].position, self.ship.position)
                    if dist < gun.range:
                        targets.append((dist, i_ship))
            if targets:
                gun.target = Controller.fleet[min(targets, key=lambda x: x[0])[1]]
            return targets

        def set_targets():
            targets = find_targets()
            diffs = []
            for target in targets:
                if two_points_length(gun.target.position, self.ship.position) < gun.range:
                    diffs.append((target, gun.diff_angle_to(Controller.fleet[target[1]], self.ship.heading)[1]))
            if diffs:
                gun.target = Controller.fleet[min(diffs, key=lambda x: abs(x[1]))[0][1]]
            else:
                gun.target = None

        if not self.ship.bridge.destroyed and Camera.time % 5 - Camera.game_factor < 0:
            for gun in self.ship.guns:
                if gun.target is None:
                    set_targets()
                elif gun.target and (
                        two_points_length(gun.target.position, self.ship.position) > gun.range or gun.target.hp < 0):
                    set_targets()

            dict_ = dict()
            for gun in self.ship.guns:
                if gun.target not in dict_:
                    dict_[gun.target] = 0
                else:
                    dict_[gun.target] += 1

            if dict_.values():
                max_value = max(dict_.values())
                self.main_target = [k for k, v in dict_.items() if v == max_value][0]
                if self.main_target:
                    x_diff, y_diff = self.main_target.position[0] - self.ship.position[0], self.main_target.position[1] - \
                                     self.ship.position[1]
                    # Clockwise rounding (against - y, + x)
                    if self.clockwise < 0.5:
                        self.ship.course_array = [
                                (self.ship.position[0] + y_diff / 2, self.ship.position[1] - x_diff / 2)]
                    else:
                        self.ship.course_array = [
                            (self.ship.position[0] - y_diff / 2, self.ship.position[1] + x_diff / 2)]


class Focus(Strategy):
    def __init__(self, ship):
        super().__init__(ship)
        self.main_target = None
        self.clockwise = random.random()

    def __str__(self):
        return "Destroy the weakest"

    def tick(self):
        def find_targets():
            targets = []
            for i_ship in range(len(Controller.fleet)):
                if Controller.fleet[i_ship] != self.ship and Controller.fleet[i_ship].bot is not True:
                    hp = Controller.fleet[i_ship].hp
                    if hp > 0:
                        targets.append((hp, i_ship))
            if targets:
                gun.target = Controller.fleet[min(targets, key=lambda x: x[0])[1]]
            else:
                gun.target = None
            return targets

        if not self.ship.bridge.destroyed and Camera.time % 5 - Camera.game_factor < 0:
            for gun in self.ship.guns:
                if gun.target is None:
                    find_targets()
                elif gun.target and (
                        two_points_length(gun.target.position, self.ship.position) > gun.range or gun.target.hp < 0):
                    find_targets()

            dict_ = dict()
            for gun in self.ship.guns:
                if gun.target not in dict_:
                    dict_[gun.target] = 0
                else:
                    dict_[gun.target] += 1

            if dict_.values():
                max_value = max(dict_.values())
                self.main_target = [k for k, v in dict_.items() if v == max_value][0]
                if self.main_target:
                    x_diff, y_diff = self.main_target.position[0] - self.ship.position[0], self.main_target.position[1] - \
                                     self.ship.position[1]
                    angle = math.degrees(math.atan2(y_diff, x_diff)) - self.ship.heading
                    abs_ = abs(self.main_target.heading - self.ship.heading)
                    # Clockwise rounding (against - y, + x)
                    if self.clockwise < 0.5:
                        self.ship.course_array = [
                                (self.ship.position[0] + y_diff / 2, self.ship.position[1] - x_diff / 2)]
                    else:
                        self.ship.course_array = [
                            (self.ship.position[0] - y_diff / 2, self.ship.position[1] + x_diff / 2)]

