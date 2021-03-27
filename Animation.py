import Camera
import pygame


class Animation:
    def __init__(self, position, images_set, animation_speed, dimensions, angle=0, over_water=True, bind_object=None):
        self.position = position
        self.angle = angle
        self.dimensions = dimensions
        self.images_set = images_set
        self.animation_speed = animation_speed
        self.i = 0
        self.image = images_set[self.i]
        self.last_change = Camera.time
        self.end = False
        self.over_water = over_water
        self.bind_object = bind_object
        if self.bind_object:
            self.diff = self.bind_object.position[0] - self.position[0], self.bind_object.position[1] - self.position[1]

    def tick(self):
        if self.bind_object:
            self.position = self.bind_object.position[0] - self.diff[0], self.bind_object.position[1] - self.diff[1]
        if self.last_change + self.animation_speed < Camera.time:
            if len(self.images_set) <= self.i + 1:
                self.end = True
            else:
                self.last_change = Camera.time
                self.i += 1
                self.image = self.images_set[self.i]

    def get_surf_rect(self):
        g_position = Camera.l_position_to_graphical(self.position)
        if not Camera.over_edge(g_position):
            anim_surface = self.image.copy()
            anim_surface = pygame.transform.scale(
                anim_surface, (int(self.dimensions[0] * Camera.scale), int(self.dimensions[1] * Camera.scale)))
            anim_surface = pygame.transform.rotate(anim_surface, self.angle)
            anim_rect = anim_surface.get_rect(center=g_position)
            return anim_surface, anim_rect
