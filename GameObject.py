

class GameObject:
    def __init__(self, image, heading, position, dimensions):
        self.image = image
        self.heading = heading
        self.position = position
        self.dimensions = dimensions

    def tick(self):
        pass

    def get_surf_rect(self):
        pass

    def is_clicked(self):
        pass


class ShipElement:
    def __init__(self, position_on_ship_surf, dimensions):
        self.position_on_ship_surf = position_on_ship_surf
        self.dimensions = dimensions

    def copy(self):
        pass

    def tick(self):
        pass