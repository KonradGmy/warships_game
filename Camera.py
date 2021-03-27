from Constants import MAX_CAMERA_VEL, MIN_CAMERA_VEL, MAX_SCALE, MIN_SCALE, HALF_HEIGHT, HALF_WIDTH, WIDTH, HEIGHT

position_x, position_y = 0, 0
velocity_x, velocity_y = 0, 0
scale = 1
time = 0
game_factor = 0
camera_draw_range = 300


def str_time():
    return ('{0:.{1}f}'.format(int(time) + ((time % 1) * 0.6), 2)).replace('.', ':')


def update_pos():
    global position_x, position_y
    manage_vel()
    position_x += velocity_x
    position_y += velocity_y


def manage_vel():
    global velocity_x, velocity_y
    if velocity_x ** 2 + velocity_y ** 2 > (MAX_CAMERA_VEL / scale ** 0.5) ** 2:
        multiplier = (MAX_CAMERA_VEL / scale ** 0.5) ** 2 / (velocity_x ** 2 + velocity_y ** 2)
        velocity_x *= multiplier
        velocity_y *= multiplier


def breaking():
    global velocity_x, velocity_y
    if velocity_x > 0:
        velocity_x -= 1
    elif velocity_x < 0:
        velocity_x += 1

    if velocity_y > 0:
        velocity_y -= 1
    elif velocity_y < 0:
        velocity_y += 1

    if abs(velocity_x) < MIN_CAMERA_VEL:
        velocity_x = 0
    if abs(velocity_y) < MIN_CAMERA_VEL:
        velocity_y = 0


def scaling(scale_speed):
    global scale
    if scale_speed > 1 and MAX_SCALE > scale:
        scale *= scale_speed
        if scale > MAX_SCALE:
            scale = MAX_SCALE
    if scale_speed < 1 and MIN_SCALE < scale:
        scale *= scale_speed
        if scale < MIN_SCALE:
            scale = MIN_SCALE
    scale = round(scale, 2)


def g_position_to_logical(g_position):
    x, y = g_position
    x -= HALF_WIDTH
    y -= HALF_HEIGHT
    x /= scale
    y /= scale
    x += position_x
    y -= position_y
    y = -y
    return int(x), int(y)


def l_position_to_graphical(l_position):
    x, y = l_position
    y = -y
    x -= position_x
    y += position_y
    x *= scale
    y *= scale
    x += HALF_WIDTH
    y += HALF_HEIGHT
    return x, y


def over_edge(g_position):
    return g_position[0] < -camera_draw_range or g_position[1] < -camera_draw_range or g_position[0] > WIDTH + camera_draw_range or g_position[1] > HEIGHT + camera_draw_range