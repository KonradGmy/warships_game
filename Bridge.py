
from Maths import find_rect_hitbox, polygon_hit, move_point_by_vector_on_angle
import Camera
from GameObject import ShipElement


class Bridge(ShipElement):
    def __init__(self, position_on_ship_surf, dimensions):
        super().__init__(position_on_ship_surf, dimensions)
        self.destroyed = False

    def copy(self):
        return Bridge(self.position_on_ship_surf, self.dimensions)

    def is_clicked(self, l_top_left, parent_heading, proportions, click_position):
        l_top_left_bridge_rot_center_l_pos = self.position_on_ship_surf[0] / proportions[0], self.position_on_ship_surf[
            1] \
                                             / proportions[1]

        engine_center = move_point_by_vector_on_angle(l_top_left, l_top_left_bridge_rot_center_l_pos, parent_heading)
        rect = find_rect_hitbox(self.dimensions, engine_center, parent_heading)
        return polygon_hit(rect, Camera.g_position_to_logical((0, 0)), click_position)