import random
import pygame
import Camera
from Animation import Animation
from Constants import WIDTH, HALF_WIDTH, HALF_HEIGHT
from Maths import move_point_by_vector_on_angle

pygame.font.init()
my_font = pygame.font.SysFont('calibri', 20)
end_font = pygame.font.SysFont('calibri', 50)
show_hp = True
pocket = None
path_mode = False
clock_FPS = 30

shells = []
fleet = []
animations = []
game_speed = 1
supposed_game_speed = game_speed

turret_firing_anim = []
shell_water_splash_anim = []
shell_ship_hit = []
ship_explosion = []
water_trail = []

pocket_data_position = (10, 30)
game_data_position = (WIDTH - 10, 30)
text_spacing = 20
guns_info = False
add_targets_mode = False
water_dimensions = (100, 100)
water_animation = []
end = False
end_info = ""
i = 0


def get_start_point():
    m_x, m_y = int(Camera.position_x / water_dimensions[0]), int(Camera.position_y / water_dimensions[1])
    r_x, r_y = Camera.position_x % water_dimensions[0], Camera.position_y % water_dimensions[1]
    return m_x * water_dimensions[0] + r_x, m_y * water_dimensions[1] + r_y


def draw_water(x, y, screen):
    start_point = get_start_point()
    if abs(Camera.position_x - start_point[0]) > water_dimensions[0] or abs(Camera.position_y - start_point[1]) > water_dimensions[1]:
        start_point = get_start_point()

    water_surf = water_animation[int(i) % len(water_animation)]
    water_surf = pygame.transform.scale(water_surf, (
        int(water_dimensions[0] * Camera.scale), int(water_dimensions[1] * Camera.scale)))

    for j in range(-x + 1, x):
        for k in range(-y + 1, y):
            water_rect = water_surf.get_rect(center=Camera.l_position_to_graphical(
                (start_point[0] + j * water_dimensions[0] - j, start_point[1] + k * water_dimensions[1] - k)))
            screen.blit(water_surf, water_rect)


def draw_pocket_data(screen):
    if pocket:
        text_list = ["Ship:",
                     " Name: " + pocket.name,
                     " Hp: " + str(round(pocket.hp, 2)) + "/" + str(round(pocket.max_hp, 2)),
                     " Max speed " + str(round(pocket.max_speed * 3.6, 2)) + " km/h",
                     " Speed " + str(round(pocket.speed * 3.6, 2)) + " km/h",
                     " Side armor " + str(round(pocket.armor, 2)) + " mm",
                     " Strategy: " + str(pocket.strategy),
                     "Engine:",
                     " Max power: " + str(round(pocket.engine.power, 2)),
                     " Power: " + str(round(pocket.engine.power * (
                                 pocket.engine.hp / pocket.engine.max_hp) * pocket.engine.power_percent / 100, 2)),
                     " Throttle: " + str(round(pocket.engine.power_percent)) + " %",
                     " Hp: " + str(round(pocket.engine.hp, 2)) + "/" + str(round(pocket.engine.max_hp, 2)),
                     "Bridge:",
                     " Destroyed: " + str(pocket.bridge.destroyed)]
        if guns_info:
            text_list += ["Guns: "] + pocket.gun_info.split('\n')

        for i in range(len(text_list)):
            text_surface = my_font.render(
                text_list[i], False,
                (255, 255, 255))
            text_rect = text_surface.get_rect(
                midleft=(pocket_data_position[0], pocket_data_position[1] + text_spacing * i))
            screen.blit(text_surface, text_rect)


def draw_game_data(screen):
    text_list = ["FPS: " + str(round(clock_FPS)),
                 "Ships: " + str(len(fleet)),
                 "Scale: " + str(round(Camera.scale, 2)),
                 "Game speed: " + str(game_speed) + "s / 1s",
                 "Path mode: " + str(path_mode),
                 "Add targets mode: " + str(add_targets_mode)]

    for i in range(len(text_list)):
        text_surface = my_font.render(
            text_list[i], False,
            (255, 255, 255))
        text_rect = text_surface.get_rect(midright=(game_data_position[0], game_data_position[1] + text_spacing * i))
        screen.blit(text_surface, text_rect)


def draw_path_for_pocket(screen):
    if pocket:
        if not pocket.bot:
            start = pocket.position
            if len(pocket.course_array) > 0:
                stop = pocket.course_array[0]
                pygame.draw.line(screen, (0, 0, 255), Camera.l_position_to_graphical(start),
                                 Camera.l_position_to_graphical(stop))
                for i in range(len(pocket.course_array) - 1):
                    start = pocket.course_array[i]
                    stop = pocket.course_array[i + 1]
                    pygame.draw.line(screen, (0, 0, 255), Camera.l_position_to_graphical(start),
                                     Camera.l_position_to_graphical(stop))


def draw_targets_for_pocket(screen):
    if pocket:
        if not pocket.bot:
            for target in pocket.strategy.targets:
                pygame.draw.line(screen, (255, 0, 0), Camera.l_position_to_graphical(pocket.position),
                             Camera.l_position_to_graphical(target.position))


def draw_endgame_info(info, screen):
    text_surface = end_font.render(
        info, False,
        (255, 255, 255))
    text_rect = text_surface.get_rect(
        center=(HALF_WIDTH, HALF_HEIGHT))
    screen.blit(text_surface, text_rect)


def manage_game(screen, game_factor):
    global end_info, end
    if water_animation:
        draw_water(30, 20, screen)
    draw_pocket_data(screen)
    draw_game_data(screen)
    draw_path_for_pocket(screen)
    draw_targets_for_pocket(screen)

    global pocket
    if pocket:
        if pocket.hp < 0:
            pocket = None

    # Tick all animations
    for anim in animations:
        anim.tick()
        if anim.end:
            animations.remove(anim)

    # Tick all ships
    for ship_ in fleet:
        if Camera.time % 0.3 - game_factor < 0:
            dimension = ship_.dimensions[1]
            animations.append(Animation(move_point_by_vector_on_angle(ship_.position, [-ship_.dimensions[0]/3, 0], ship_.heading), water_trail, 1.5, (dimension, dimension), angle=random.random() * 360, over_water=False))
        ship_.tick(game_factor)

    # Tick all shells
    for shell in shells:
        shell.tick(game_factor)

    # Hitting
    for shell in shells:
        for ship_ in fleet:
            if shell.mother_ship != ship_.name and ship_.is_clicked(shell.position, shell, random.random()):
                animations.append(Animation(shell.position, shell_ship_hit, 0.25, (25, 25), angle=random.random() * 360,
                                            over_water=True, bind_object=ship_))
                if shell in shells:
                    shells.remove(shell)

    for ship_ in fleet:
        if ship_.hp < 0:
            explosion_size = ship_.dimensions[1] * 12
            animations.append(Animation(ship_.position, ship_explosion, 0.25, (explosion_size, explosion_size),
                                        angle=random.random() * 360,
                                        over_water=True))
            ship_surf = ship_.image
            array = [ship_surf, ship_surf, ship_surf, ship_surf, ship_surf, ship_surf, ship_surf, ship_surf, ship_surf,
                     ship_surf]
            animations.append(Animation(ship_.position, array, 0.25, ship_.dimensions, angle=ship_.heading,
                                        over_water=False))
            fleet.remove(ship_)

    # Remove shells
    for shell in shells:
        if shell.shell_splash:
            animations.append(
                Animation(shell.position, shell_water_splash_anim, 0.25, (25, 25), angle=random.random() * 360,
                          over_water=False))
            if shell in shells:
                shells.remove(shell)

    # Draw not over water animations
    for anim in animations:
        if anim.over_water is False:
            surf_rect = anim.get_surf_rect()
            if surf_rect:
                screen.blit(*surf_rect)

    # Drawing ships
    for ship_ in fleet:
        surf_rect = ship_.get_surf_rect()
        if surf_rect:
            screen.blit(*surf_rect)

    # Hp drawing
    for ship_ in fleet:
        # Hp drawing
        if show_hp or pocket == ship_:
            text_surface = my_font.render(str(ship_), False, (255, 255, 255))
            position = Camera.l_position_to_graphical(
                (ship_.position[0], ship_.position[1] + ship_.dimensions[1] / 2))
            text_rect = text_surface.get_rect(center=(position[0], position[1] - 20))
            screen.blit(text_surface, text_rect)

    # Draw shells
    for shell in shells:
        surf_rect = shell.get_surf_rect()
        if surf_rect:
            screen.blit(*surf_rect)

    # Draw over water animations
    for anim in animations:
        if anim.over_water is True:
            surf_rect = anim.get_surf_rect()
            if surf_rect:
                screen.blit(*surf_rect)

    global i
    i += 1 * game_factor
    if i > 100000000000:
        i = 0

    if Camera.time % 20 - game_factor < 0:
        bots = 0
        player = 0
        global game_speed
        for ship in fleet:
            if not ship.bot:
                player += 1
            else:
                bots += 1
        if bots == 0 and player == 0:
            end_info = "Draw"
            end = True
            pocket = None
            game_speed = 0
        if bots == 0 and player != 0:
            end_info = "Victory!"
            end = True
            pocket = None
            game_speed = 0
        if bots != 0 and player == 0:
            end_info = "Defeat"
            end = True
            pocket = None
            game_speed = 0

    if end:
        draw_endgame_info(end_info, screen)

