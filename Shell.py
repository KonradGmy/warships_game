import pygame
from Maths import repair_deg_angle, to_rad, find_rect_hitbox, polygon_hit, to_deg, two_points_length
import math
import Camera


class Shell:
    def __init__(self, fire_position, destination_position, speed, dimensions, penetration, damage, potential_hit_from_side, mother_ship):
        self.image = pygame.image.load("Assets/Images/Shell/shell.png")
        self.dimensions = dimensions
        self.fire_position = fire_position
        self.position = self.fire_position
        self.destination_position = destination_position
        self.speed = speed
        self.shell_splash = False
        self.angle = None
        self.penetration = penetration
        self.damage = damage
        self.potential_hit_from_side = potential_hit_from_side
        self.mother_ship = mother_ship
        self.min_transform = (4, 2)
        self.find_angle()

    def find_angle(self):
        x = self.destination_position[0] - self.position[0]
        y = self.destination_position[1] - self.position[1]
        self.angle = math.atan2(y, x)

    def tick(self, game_factor):
        if two_points_length(self.position, self.destination_position) < self.speed * game_factor:
            self.shell_splash = True
        else:
            self.find_angle()
            x_diff = self.speed * math.cos(self.angle) * game_factor
            y_diff = self.speed * math.sin(self.angle) * game_factor

            self.position = self.position[0] + x_diff, self.position[1] + y_diff

    def get_surf_rect(self):
        g_position = Camera.l_position_to_graphical(self.position)
        shell_surface = self.image
        transform = (int(self.dimensions[0] * Camera.scale), int(self.dimensions[1] * Camera.scale))
        if transform[0] < self.min_transform[0] and transform[1] < self.min_transform[1]:
            transform = self.min_transform
        shell_surface = pygame.transform.scale(shell_surface, transform)
        shell_surface = pygame.transform.rotate(shell_surface, to_deg(self.angle))
        shell_rect = shell_surface.get_rect(center=g_position)
        return shell_surface, shell_rect
