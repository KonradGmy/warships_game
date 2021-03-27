import numpy as np
import math
import random


def collide_line_line(P0, P1, Q0, Q1):
    d = (P1[0] - P0[0]) * (Q1[1] - Q0[1]) + (P1[1] - P0[1]) * (Q0[0] - Q1[0])
    if d == 0:
        return None
    t = ((Q0[0] - P0[0]) * (Q1[1] - Q0[1]) + (Q0[1] - P0[1]) * (Q0[0] - Q1[0])) / d
    u = ((Q0[0] - P0[0]) * (P1[1] - P0[1]) + (Q0[1] - P0[1]) * (P0[0] - P1[0])) / d
    if 0 <= t <= 1 and 0 <= u <= 1:
        return P1[0] * t + P0[0] * (1 - t), P1[1] * t + P0[1] * (1 - t)
    return None


def to_rad(degrees):
    return np.deg2rad(degrees)


def to_deg(rad):
    return np.rad2deg(rad)


def two_points_length(a, b):
    return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5


def repair_deg_angle(angle):
    if angle >= 180:
        angle -= 360
    elif angle < -180:
        angle += 360
    return angle


def polygon_hit(list_, a_point, b_point):
    intersection_points = []
    for i in range(len(list_) - 1):
        intersection_points.append(collide_line_line(list_[i], list_[i + 1], a_point, b_point))
    intersection_points.append(collide_line_line(list_[-1], list_[0], a_point, b_point))

    intersections = 0
    for item in intersection_points:
        if item:
            intersections += 1
    return intersections == 1


def find_rect_hitbox(dimensions, position, heading):
    length = ((dimensions[0] / 2) ** 2 + (dimensions[1] / 2) ** 2) ** 0.5
    change_rad = math.atan2((dimensions[1]), (dimensions[0]))
    rad1 = to_rad(heading) + change_rad
    x1 = math.cos(rad1) * length
    y1 = math.sin(rad1) * length
    rad2 = to_rad(heading) - change_rad
    x2 = math.cos(rad2) * length
    y2 = math.sin(rad2) * length

    rect = [(position[0] - x1, position[1] - y1),  # Four points of clicker rectangle
            (position[0] + x2, position[1] + y2),
            (position[0] + x1, position[1] + y1),
            (position[0] - x2, position[1] - y2)]

    return rect


def move_point_by_vector_on_angle(P, V, angle):
    angle2 = 90 - angle
    x1 = V[0] * math.cos(to_rad(angle))
    y1 = V[0] * math.sin(to_rad(angle))
    x2 = V[1] * math.cos(to_rad(angle2))
    y2 = V[1] * math.sin(to_rad(angle2))
    return P[0] + x1 + x2, P[1] + y1 - y2


def find_shooting_spot_for_target_ship(ship, shell_speed, distance, precision):
    flight_time = distance / shell_speed
    half_error = distance / (precision * 2)
    shift_x = random.random() * distance / precision - half_error
    shift_y = random.random() * distance / precision - half_error
    return move_point_by_vector_on_angle(ship.position, (ship.speed * flight_time + shift_x, shift_y), ship.heading)

