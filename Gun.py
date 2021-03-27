import pygame
from GameObject import GameObject
from Animation import Animation
from Maths import repair_deg_angle, find_rect_hitbox, polygon_hit, to_deg, move_point_by_vector_on_angle, \
    two_points_length, find_shooting_spot_for_target_ship
import math
import Camera, Controller
from Shell import Shell


class Gun(GameObject):
    def __init__(self, image, position_on_ship_surf, heading, angle_range, dimensions, angular_speed, caliber,
                 gun_firing_pos, range_, armor, hp, shell_speed, shell_dam, cooldown_time, precision, penetration,
                 center_diff=0):
        super().__init__(image, heading, None, dimensions)

        # Drawing
        self.position_on_ship_surf = position_on_ship_surf
        self.angle_range = angle_range
        self.center_diff = center_diff

        # Gun variables
        self.angular_speed = angular_speed
        self.cooldown_time = cooldown_time
        self.cooldown = self.cooldown_time
        self.gun_firing_pos = gun_firing_pos
        self.caliber = caliber
        self.armor = armor
        self.max_hp = hp
        self.hp = self.max_hp
        self.shell_speed = shell_speed
        self.shell_dam = shell_dam
        self.precision = precision
        self.range = range_
        self.penetration = penetration

        self.absorb_prop = 30
        self.target = None
        self.aiming = False
        self.shooting = True
        self.rot_center_pos = (0, 0)
        self.target_in_blank_range = False

    def copy(self, position_on_ship_surf, angle_range=None, heading=None):
        if not heading:
            heading = self.heading

        if not angle_range:
            angle_range = self.angle_range
        return Gun(self.image, position_on_ship_surf, heading, angle_range, self.dimensions,
                   self.angular_speed, self.caliber, self.gun_firing_pos, self.range, self.armor, self.max_hp,
                   self.shell_speed, self.shell_dam, self.cooldown_time, self.precision, self.penetration,
                   self.center_diff)

    def find_rot_center_pos(self, l_top_left, parent_heading, proportions):
        l_top_left_gun_rot_center_l_pos = self.position_on_ship_surf[0] / proportions[0], self.position_on_ship_surf[1] \
                                          / proportions[1]

        rot_center = move_point_by_vector_on_angle(l_top_left, l_top_left_gun_rot_center_l_pos, parent_heading)
        rot_corr_center = move_point_by_vector_on_angle(rot_center, (self.center_diff, 0),
                                                        self.heading + parent_heading)

        return rot_corr_center

    def is_clicked(self, parent_heading, click_position):
        rect = find_rect_hitbox(self.dimensions, self.rot_center_pos, self.heading + parent_heading)
        return polygon_hit(rect, Camera.g_position_to_logical((0, 0)), click_position)

    def diff_angle_to(self, target, parent_heading):
        x_diff = target.position[0] - self.rot_center_pos[0]
        y_diff = target.position[1] - self.rot_center_pos[1]
        to_target = repair_deg_angle(to_deg(math.atan2(y_diff, x_diff)))

        return repair_deg_angle(to_deg(math.atan2(y_diff, x_diff))), \
               repair_deg_angle(self.heading + parent_heading - to_target)  # Difference of angle to target

    def in_blank_range(self, heading):
        heading = repair_deg_angle(heading)
        if self.angle_range[0] > self.angle_range[1]:
            self.target_in_blank_range = self.angle_range[1] < heading < self.angle_range[0]
            return self.target_in_blank_range
        else:
            self.target_in_blank_range = heading > self.angle_range[1] or heading < self.angle_range[0]
            return self.target_in_blank_range

    def tick(self, game_factor, l_top_left, parent_heading, proportions, ship_name):
        self.rot_center_pos = self.find_rot_center_pos(l_top_left, parent_heading, proportions)

        # Repair angle
        self.heading = repair_deg_angle(self.heading)

        if self.hp > 0:
            if self.target and self.target.hp < 0:
                self.target = None

            if self.target:
                #  Find diff angle
                to_target, diff_angle = self.diff_angle_to(self.target, parent_heading)

                def turn_right():
                    if 0 < diff_angle < self.angular_speed * game_factor:
                        ang = repair_deg_angle(to_target - parent_heading)
                        if not self.in_blank_range(ang):
                            self.heading = ang
                            self.aiming = True
                        else:
                            self.aiming = False
                    else:
                        ang = self.heading - self.angular_speed * game_factor
                        if not self.in_blank_range(ang):
                            self.heading = ang
                            self.aiming = False
                        else:
                            self.aiming = False

                def turn_left():
                    if self.angular_speed * game_factor < 0:
                        ang = repair_deg_angle(to_target - parent_heading)
                        if not self.in_blank_range(ang):
                            self.heading = ang
                            self.aiming = True
                        else:
                            self.aiming = False
                    else:
                        ang = self.heading + self.angular_speed * game_factor
                        if not self.in_blank_range(ang):
                            self.heading = ang
                            self.aiming = False
                        else:
                            self.aiming = False

                def range_in_way():
                    diff_1 = repair_deg_angle(self.heading - self.angle_range[0])
                    diff_2 = repair_deg_angle(self.heading - self.angle_range[1])
                    if diff_angle < 0 and diff_1 < 0 and diff_2 < 0:
                        return diff_1 > diff_angle and diff_2 > diff_angle
                    elif diff_angle > 0 and diff_1 > 0 and diff_2 > 0:
                        return diff_1 < diff_angle and diff_2 < diff_angle
                    else:
                        return False

                if diff_angle != 0:
                    if diff_angle > 0:
                        if range_in_way():
                            turn_left()
                        else:
                            turn_right()
                    else:
                        if range_in_way():
                            turn_right()
                        else:
                            turn_left()
                #  Repair angle
                self.heading = repair_deg_angle(self.heading)

                # Shooting
                if self.shooting:
                    if self.cooldown < self.cooldown_time:
                        self.cooldown += Camera.game_factor
                        if self.cooldown > self.cooldown_time:
                            self.cooldown = self.cooldown_time

                    if self.aiming and self.cooldown == self.cooldown_time:
                        for firing_gun in self.gun_firing_pos:
                            firing_position = tuple(self.rot_center_pos)
                            firing_position = move_point_by_vector_on_angle(firing_position, firing_gun,
                                                                            self.heading + parent_heading)
                            distance = two_points_length(firing_position, tuple(self.target.position))
                            if distance < self.range:
                                target_position = find_shooting_spot_for_target_ship(self.target, self.shell_speed,
                                                                                     distance, self.precision)
                                shell_dim = (int(self.caliber / 100) * 2, int(self.caliber / 100))
                                Controller.animations.append(
                                    Animation(firing_position, Controller.turret_firing_anim, 0.04,
                                              (self.dimensions[0] * 4, self.dimensions[1] * 2),
                                              angle=self.heading + parent_heading))
                                Controller.shells.append(
                                    Shell(firing_position, target_position, self.shell_speed, shell_dim,
                                          self.range / (distance + self.range) * self.penetration, self.shell_dam,
                                          distance < self.range * 0.3, ship_name))
                        self.cooldown = 0

    def get_surf_rect(self):
        gun_surface = self.image.copy()
        gun_surface = pygame.transform.rotate(gun_surface, self.heading)
        gun_rect = gun_surface.get_rect(center=self.position_on_ship_surf)
        return gun_surface, gun_rect

    def __getstate__(self):
        state = self.__dict__.copy()
        surface = state.pop("image")
        state["surface_string"] = (pygame.image.tostring(surface, "RGBA"), surface.get_size())
        return state

    def __setstate__(self, state):
        surface_string, size = state.pop("surface_string")
        state["image"] = pygame.image.fromstring(surface_string, size, "RGBA")
        self.__dict__.update(state)
