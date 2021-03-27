import pygame
from GameObject import GameObject
from Bridge import Bridge
from Engine import Engine
from Maths import to_rad, repair_deg_angle, find_rect_hitbox, polygon_hit
from Strategy import *
import Camera


class Ship(GameObject):
    def __init__(self, name, image, position, heading, dimensions, bridge, guns, engine, armor, hp, constants, gun_info,
                 polynomial_hitbox=(1, 1), bot=False):
        super().__init__(image, heading, position, dimensions)
        # Data
        self.name = name

        # Hitbox
        self.polynomial_hitbox = polynomial_hitbox

        # Sailing variables
        self.moving_direction = heading
        self.course_array = []

        # Ship variables
        self.speed = 3
        self.stere_angle = 0
        self.bridge: Bridge = bridge
        self.guns: list = guns
        self.engine: Engine = engine
        self.armor = armor
        self.max_hp = hp
        self.hp = self.max_hp
        self.absorb_prop = 30
        self.bot = bot
        if bot is False:
            self.strategy: Strategy = PlayerControlled(self)
        else:
            self.strategy: Strategy = Search(self, False)

        # Ship constants
        self.stere_angle_speed = constants[0]
        self.turning_factor = constants[1]
        self.broadside_braking_factor = constants[
            2]  # How much speed ship will lose if put by 90 deg angle to moving direction
        self.hull_breaking_factor = constants[3]  # How much to slow down every second without engine
        self.max_stere_angle = constants[4]

        # Constants
        self.max_speed = (self.engine.power / self.hull_breaking_factor) ** 0.5
        self.drop_course_radius = 30
        self.gun_info = gun_info
        self.ship_gun_range = max(self.guns, key=lambda x: x.range).range

        # Modules variables
        self.l_top_left = None
        self.proportions = None
        self.find_modules_data()

    def copy(self, name, position, bot=True):
        guns_copy = []
        for gun in self.guns:
            guns_copy.append(gun.copy(gun.position_on_ship_surf, gun.angle_range))
        constants_copy = [self.stere_angle_speed,
                          self.turning_factor,
                          self.broadside_braking_factor,
                          self.hull_breaking_factor,
                          self.max_stere_angle]
        return Ship(name, self.image, position, 0, self.dimensions, self.bridge.copy(), guns_copy,
                    self.engine.copy(), self.armor, self.max_hp, constants_copy, self.polynomial_hitbox, bot=bot)

    def __str__(self):
        return f"{self.name} {int(self.hp)}/{int(self.max_hp)}"

    def set_engine_power_percent(self, percent):
        if -self.engine.max_negative_percent <= percent <= 100:
            self.engine.power_percent = percent

    def find_modules_data(self):
        # Get values needed for guns hitboxes
        length = ((self.dimensions[0] / 2) ** 2 + (self.dimensions[1] / 2) ** 2) ** 0.5
        change_rad = math.asin((self.dimensions[1] / 2) / (self.dimensions[0] / 2))
        rad2 = to_rad(self.heading) - change_rad
        x2 = math.cos(rad2) * length
        y2 = math.sin(rad2) * length
        self.l_top_left = self.position[0] - x2, self.position[1] - y2
        image_size = self.image.get_rect().size
        self.proportions = (image_size[0] / self.dimensions[0], image_size[1] / self.dimensions[1])

    def tick(self, game_factor):
        # Tick all guns
        for gun in self.guns:
            gun.tick(game_factor, self.l_top_left, self.heading, self.proportions, self.name)

        # Strategy managing
        power_pl = 0
        power_bot = 0
        for ship in Controller.fleet:
            if not ship.bot:
                for gun in ship.guns:
                    power_pl += gun.caliber
            else:
                for gun in ship.guns:
                    power_bot += gun.caliber
        bot_advantage = power_bot > power_pl
        if type(self.strategy) != PlayerControlled:
            if type(self.strategy) == Search and self.strategy.target:
                if two_points_length(self.strategy.target.position, self.position) < self.ship_gun_range:
                    if bot_advantage:
                        self.strategy = Destroy(self)
                    else:
                        self.strategy = Focus(self)
            else:
                if Camera.time % 20 - game_factor < 0:
                    find = True
                    for gun in self.guns:
                        if gun.target:
                            if two_points_length(gun.target.position, self.position) < self.ship_gun_range:
                                find = False
                                break
                    if find:
                        self.strategy = Search(self, bot_advantage=bot_advantage)
        if self.strategy:
            self.strategy.tick()

        # Repair angles
        self.heading = repair_deg_angle(self.heading)
        self.moving_direction = repair_deg_angle(self.moving_direction)

        self.find_modules_data()

        # Course managing
        if self.course_array:
            course_point = self.course_array[0]
            x_diff = course_point[0] - self.position[0]
            y_diff = course_point[1] - self.position[1]

            angle = math.degrees(math.atan2(y_diff, x_diff)) - self.heading

            # Repair angle
            angle = repair_deg_angle(angle)

            if angle > self.stere_angle:
                if angle - self.stere_angle > self.stere_angle_speed:
                    self.stere_angle += self.stere_angle_speed * game_factor
                else:
                    self.stere_angle += (angle - self.stere_angle) * game_factor
            if angle < self.stere_angle:
                if angle - self.stere_angle < -self.stere_angle_speed:
                    self.stere_angle -= self.stere_angle_speed * game_factor
                else:
                    self.stere_angle -= (self.stere_angle - angle) * game_factor
            if self.stere_angle > self.max_stere_angle:
                self.stere_angle = self.max_stere_angle
            elif self.stere_angle < -self.max_stere_angle:
                self.stere_angle = -self.max_stere_angle

        if self.course_array is [] and self.stere_angle != 0:
            if self.stere_angle > 0:
                if self.stere_angle < self.stere_angle_speed:
                    self.stere_angle = 0
                else:
                    self.stere_angle -= self.stere_angle_speed * game_factor
            else:
                if self.stere_angle > -self.stere_angle_speed:
                    self.stere_angle = 0
                else:
                    self.stere_angle += self.stere_angle_speed * game_factor

        #  Engine speed up
        self.speed += self.engine.power * (self.engine.hp / self.engine.max_hp) * (
                self.engine.power_percent / 100) * game_factor

        if self.speed != 0:
            # Turn and slow down
            if self.stere_angle != 0:
                # Swinging out
                self.heading += self.stere_angle * self.turning_factor * \
                                (self.speed / self.max_speed) ** 2 \
                                * game_factor

            if self.moving_direction != self.heading:
                diff_angle = self.heading - self.moving_direction
                diff_angle = repair_deg_angle(diff_angle)
                #  Moving direction turning
                self.moving_direction += diff_angle * ((self.speed / self.max_speed) ** 2) * game_factor
                #  Side friction slow down
                self.speed -= self.speed ** 2 * abs(diff_angle) / 100 * self.broadside_braking_factor * game_factor

            #  Friction slow down
            if self.speed > 0:
                self.speed -= self.speed ** 2 * self.hull_breaking_factor * game_factor
            else:
                self.speed += self.speed ** 2 * self.hull_breaking_factor * game_factor

            # Stop if very slow
            if abs(self.speed) < 0.001:
                self.speed = 0
                self.moving_direction = self.heading

            # Relocate
            rad = to_rad(self.moving_direction)
            x = math.cos(rad) * self.speed * game_factor
            y = math.sin(rad) * self.speed * game_factor
            self.position = self.position[0] + x, self.position[1] + y

            # Drop part of path if close to point
            if self.course_array:
                distance_to_course_point = two_points_length(self.course_array[0], self.position)
                for i in range(1, len(self.course_array)):
                    distance_to_course_point_ = two_points_length(self.course_array[i], self.position)
                    if distance_to_course_point > distance_to_course_point_:
                        for j in range(i):
                            self.course_array.remove(self.course_array[0])
                        break

            # Drop actual course point
            if self.course_array and two_points_length(self.course_array[0], self.position) < self.drop_course_radius:
                self.course_array.remove(self.course_array[0])

    def is_clicked(self, mouse_position, shell=None, number=0):
        rect = find_rect_hitbox(
            (self.dimensions[0] * self.polynomial_hitbox[0], self.dimensions[1] * self.polynomial_hitbox[1]),
            self.position, self.heading)

        # Modules
        if self.bridge.is_clicked(self.l_top_left, self.heading, self.proportions, mouse_position):
            if shell:
                if shell.shell_splash:
                    self.bridge.destroyed = True
        for gun in self.guns:
            if gun.is_clicked(self.heading, mouse_position):
                if shell:
                    if shell.shell_splash:
                        if number * 100 < gun.absorb_prop and shell.penetration > gun.armor:
                            pen_diff = (shell.penetration - gun.armor) / gun.armor
                            gun.hp -= pen_diff + shell.damage * number
                            shell.penetration -= gun.armor
                            shell.damage *= shell.penetration / gun.armor
        if self.engine.is_clicked(self.l_top_left, self.heading, self.proportions, mouse_position):
            if shell:
                if shell.shell_splash:
                    self.engine.hp -= shell.damage * number
                    if self.engine.hp < 0:
                        self.engine.hp = 0

        polygon = rect
        if self.polynomial_hitbox != (1, 1):
            x = self.dimensions[0] / 2 * math.cos(to_rad(self.heading))
            y = self.dimensions[0] / 2 * math.sin(to_rad(self.heading))
            polygon.insert(2, (self.position[0] + x, self.position[1] + y))
            polygon.insert(5, (self.position[0] - x, self.position[1] - y))

        hit = polygon_hit(polygon, Camera.g_position_to_logical((0, 0)), mouse_position)
        if hit and shell:
            if shell.potential_hit_from_side:
                if number * 100 < self.absorb_prop and shell.penetration > self.armor:
                    pen_diff = (shell.penetration - self.armor) / self.armor
                    self.hp -= pen_diff + shell.damage * number
                    return True
            elif shell.shell_splash:
                if number * 100 < self.absorb_prop:
                    self.hp -= shell.damage * number * 0.5
                else:
                    self.hp -= shell.damage * number
                return True
            return False
        return hit

    def get_surf_rect(self):
        g_position = Camera.l_position_to_graphical(self.position)
        if not Camera.over_edge(g_position):
            ship_surface = self.image.copy()
            for gun in self.guns:
                ship_surface.blit(*gun.get_surf_rect())
            ship_surface = pygame.transform.scale(
                ship_surface, (int(self.dimensions[0] * Camera.scale), int(self.dimensions[1] * Camera.scale)))
            ship_surface = pygame.transform.rotate(ship_surface, self.heading)
            ship_rect = ship_surface.get_rect(center=g_position)
            return ship_surface, ship_rect

    def __getstate__(self):
        state = self.__dict__.copy()
        surface = state.pop("image")
        state["surface_string"] = (pygame.image.tostring(surface, "RGBA"), surface.get_size())
        return state

    def __setstate__(self, state):
        surface_string, size = state.pop("surface_string")
        state["image"] = pygame.image.fromstring(surface_string, size, "RGBA")
        self.__dict__.update(state)
