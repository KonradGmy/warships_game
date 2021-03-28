import pygame
import pickle
from Strategy import *
from Constants import *


# Init game
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(GAME_NAME)
clock = pygame.time.Clock()
Controller.game_speed = 1
Controller.supposed_game_speed = Controller.game_speed

# Fleet
bismarck = pickle.load(open("Assets/ShipsData/bismarck", 'rb'))
hipper = pickle.load(open("Assets/ShipsData/hipper", 'rb'))
zestorer = pickle.load(open("Assets/ShipsData/zestorer", 'rb'))

Controller.water_dimensions = (100, 100)


menu_run = True
start = False
fleet = []


def menu():
    player_spawn = (-200, -1000)
    bot_spawn = (-200, 1000)

    def draw_ship_on(screen, g_position, ship, scale):
        ship_surface = ship.image.copy()
        for gun in ship.guns:
            ship_surface.blit(*gun.get_surf_rect())
        ship_surface = pygame.transform.scale(
            ship_surface, (int(ship.dimensions[0] * scale), int(ship.dimensions[1] * scale)))
        ship_surface = pygame.transform.rotate(ship_surface, ship.heading)
        ship_rect = ship_surface.get_rect(center=g_position)
        screen.blit(ship_surface, ship_rect)

    def print_(font, text, position):
        text_surface = font.render(
            text, False,
            (255, 255, 255))
        text_rect = text_surface.get_rect(
            center=position)
        screen.blit(text_surface, text_rect)

    main_font = pygame.font.SysFont('calibri', 50)
    middle_font = pygame.font.SysFont('calibri', 30)
    small_font = pygame.font.SysFont('calibri', 15)
    player = []
    bot = []
    global menu_run, start
    while menu_run:
        m_x, m_y = pygame.mouse.get_pos()

        label_pl = pygame.Rect(100, 100, 400, 800)
        label_bot = pygame.Rect(WIDTH - 500, 100, 400, 800)

        player_bismarck = pygame.Rect(HALF_WIDTH - 160, 300, 150, 50)
        bot_bismarck = pygame.Rect(HALF_WIDTH + 10, 300, 150, 50)

        player_hipper = pygame.Rect(HALF_WIDTH - 160, 600, 150, 50)
        bot_hipper = pygame.Rect(HALF_WIDTH + 10, 600, 150, 50)

        player_zestorer = pygame.Rect(HALF_WIDTH - 160, 900, 150, 50)
        bot_zestorer = pygame.Rect(HALF_WIDTH + 10, 900, 150, 50)


        screen.fill((32, 85, 158))
        # Labels
        pygame.draw.rect(screen, (32, 56, 73), label_pl)
        pygame.draw.rect(screen, (32, 56, 73), label_bot)

        # Buttons
        pygame.draw.rect(screen, (58, 27, 73), player_bismarck)
        pygame.draw.rect(screen, (58, 27, 73), bot_bismarck)

        pygame.draw.rect(screen, (58, 27, 73), player_hipper)
        pygame.draw.rect(screen, (58, 27, 73), bot_hipper)

        pygame.draw.rect(screen, (58, 27, 73), player_zestorer)
        pygame.draw.rect(screen, (58, 27, 73), bot_zestorer)

        # Text
        print_(main_font, "Choose fleets", (HALF_WIDTH, 50))
        print_(middle_font, "Player " + str(len(player)) + "/" + str(MAX_SHIPS), (300, 150))
        print_(middle_font, "Bot " + str(len(bot)) + "/" + str(MAX_SHIPS), (WIDTH - 300, 150))

        print_(small_font, "Add for player", (HALF_WIDTH - 160 + 75, 325))
        print_(small_font, "Add for bot", (HALF_WIDTH + 160 - 75, 325))

        print_(small_font, "Add for player", (HALF_WIDTH - 160 + 75, 625))
        print_(small_font, "Add for bot", (HALF_WIDTH + 160 - 75, 625))

        print_(small_font, "Add for player", (HALF_WIDTH - 160 + 75, 925))
        print_(small_font, "Add for bot", (HALF_WIDTH + 160 - 75, 925))

        # Ship on middle
        draw_ship_on(screen, (HALF_WIDTH, 200), bismarck, 3)
        draw_ship_on(screen, (HALF_WIDTH, 500), hipper, 3)
        draw_ship_on(screen, (HALF_WIDTH, 800), zestorer, 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # quiting game
                menu_run = False
            if event.type == pygame.KEYDOWN:
                #  Game speed managing
                if event.key == pygame.K_SPACE:
                    menu_run = False
                    start = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if player_bismarck.collidepoint((m_x, m_y)):
                        if len(player) < MAX_SHIPS:
                            player.append(bismarck.copy("Bismarck" + str(len(player)),
                                                    (player_spawn[0] + len(player) * 300, player_spawn[1]), False))
                    if bot_bismarck.collidepoint((m_x, m_y)):
                        if len(bot) < MAX_SHIPS:
                            bot.append(bismarck.copy("BBismarck" + str(len(player)),
                                                    (bot_spawn[0] + len(bot) * 300, bot_spawn[1]), True))
                    if player_hipper.collidepoint((m_x, m_y)):
                        if len(player) < MAX_SHIPS:
                            player.append(hipper.copy("Hipper" + str(len(player)),
                                                    (player_spawn[0] + len(player) * 300, player_spawn[1]), False))
                    if bot_hipper.collidepoint((m_x, m_y)):
                        if len(bot) < MAX_SHIPS:
                            bot.append(hipper.copy("BHipper" + str(len(player)),
                                                    (bot_spawn[0] + len(bot) * 300, bot_spawn[1]), True))
                    if player_zestorer.collidepoint((m_x, m_y)):
                        if len(player) < MAX_SHIPS:
                            player.append(zestorer.copy("Zestorer" + str(len(player)),
                                                    (player_spawn[0] + len(player) * 300, player_spawn[1]), False))
                    if bot_zestorer.collidepoint((m_x, m_y)):
                        if len(bot) < MAX_SHIPS:
                            bot.append(zestorer.copy("BZestorer" + str(len(player)),
                                                    (bot_spawn[0] + len(bot) * 300, bot_spawn[1]), True))

        for ship in player:
            draw_ship_on(screen, (300, 200 + player.index(ship) * 70), ship, 1)

        for ship in bot:
            draw_ship_on(screen, (WIDTH - 300, 200 + bot.index(ship) * 70), ship, 1)

        pygame.display.update()
        clock.tick(30)
    global fleet
    fleet = player + bot


menu()

Controller.fleet = fleet


def load_animations():
    Controller.water_animation = [pygame.image.load("Assets/Animations/Water/1.jpg").convert_alpha(),
                                  pygame.image.load("Assets/Animations/Water/2.jpg").convert_alpha(),
                                  pygame.image.load("Assets/Animations/Water/3.jpg").convert_alpha(),
                                  pygame.image.load("Assets/Animations/Water/4.jpg").convert_alpha(),
                                  pygame.image.load("Assets/Animations/Water/3.jpg").convert_alpha(),
                                  pygame.image.load("Assets/Animations/Water/2.jpg").convert_alpha()]

    Controller.turret_firing_anim = [pygame.image.load("Assets/Animations/TurretFiring/1.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/2.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/3.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/4.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/5.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/6.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/7.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/8.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/9.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/10.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/11.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/12.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/13.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/14.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/15.png").convert_alpha(),
                                     pygame.image.load("Assets/Animations/TurretFiring/16.png").convert_alpha()]

    Controller.shell_water_splash_anim = [pygame.image.load("Assets/Animations/ShellWaterSplash/1.png").convert_alpha(),
                                          pygame.image.load("Assets/Animations/ShellWaterSplash/2.png").convert_alpha(),
                                          pygame.image.load("Assets/Animations/ShellWaterSplash/3.png").convert_alpha(),
                                          pygame.image.load("Assets/Animations/ShellWaterSplash/4.png").convert_alpha(),
                                          pygame.image.load("Assets/Animations/ShellWaterSplash/5.png").convert_alpha()]

    Controller.shell_ship_hit = [pygame.image.load("Assets/Animations/ShellShipHit/1.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShellShipHit/2.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShellShipHit/3.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShellShipHit/4.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShellShipHit/5.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShellShipHit/6.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShellShipHit/7.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShellShipHit/8.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShellShipHit/9.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShellShipHit/10.png").convert_alpha()]

    Controller.ship_explosion = [pygame.image.load("Assets/Animations/ShipExplosion/1.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/2.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/3.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/4.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/5.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/6.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/7.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/8.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/9.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/10.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/11.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/12.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/13.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/14.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/15.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/16.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/17.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/18.png").convert_alpha(),
                                 pygame.image.load("Assets/Animations/ShipExplosion/19.png").convert_alpha()]

    Controller.water_trail = [pygame.image.load("Assets/Animations/WaterTrail/1.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/2.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/3.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/4.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/5.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/6.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/7.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/8.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/9.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/10.png").convert_alpha(),
                              pygame.image.load("Assets/Animations/WaterTrail/11.png").convert_alpha()]

    for i in range(4):
        Controller.water_trail.insert(0, Controller.water_trail[0])


if start:
    load_animations()

    mouse_pos = 0, 0
    drag_origin_x, drag_origin_y = 0, 0
    drag = False
    running = True
    paused = False
    Controller.path_mode = False
    Camera.game_factor = Controller.game_speed / FPS
    while running:
        if clock.get_fps() == 0:
            clock_FPS = FPS
        else:
            clock_FPS = clock.get_fps()
        Camera.game_factor = Controller.game_speed / clock_FPS
        game_factor = Camera.game_factor
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # quiting game
                running = False
            if event.type == pygame.KEYDOWN:
                #  Game speed managing
                if event.key == pygame.K_u:
                    if Controller.supposed_game_speed < MAX_GAME_SPEED:
                        Controller.supposed_game_speed += 1
                if event.key == pygame.K_j:
                    if Controller.supposed_game_speed > 1:
                        Controller.supposed_game_speed -= 1
                if not paused:
                    Controller.game_speed = Controller.supposed_game_speed
                if event.key == pygame.K_h:
                    if Controller.path_mode:
                        Controller.path_mode = False
                        if Controller.pocket:
                            if not Controller.pocket.bridge.destroyed:
                                if len(Controller.pocket.course_array) == 1:
                                    Controller.pocket.course_array = [Controller.pocket.course_array[0]]
                                else:
                                    Controller.pocket.course_array = []
                    else:
                        Controller.path_mode = True
                #  Pausing
                if event.key == pygame.K_SPACE:
                    if paused:
                        paused = False
                        Controller.game_speed = Controller.supposed_game_speed
                    else:
                        paused = True
                        Controller.game_speed = 0
                if event.key == pygame.K_v:
                    Controller.show_hp = not Controller.show_hp
                if event.key == pygame.K_t:
                    Controller.add_targets_mode = not Controller.add_targets_mode
                if event.key == pygame.K_q:
                    if Controller.pocket:
                        if not Controller.pocket.bridge.destroyed:
                            if type(Controller.pocket.strategy) == PlayerControlled:
                                Controller.pocket.strategy.targets = []
                if event.key == pygame.K_k:
                    if Controller.pocket:
                        if not Controller.pocket.bridge.destroyed:
                            Controller.pocket.set_engine_power_percent(Controller.pocket.engine.power_percent + 10)
                if event.key == pygame.K_m:
                    if Controller.pocket:
                        if not Controller.pocket.bridge.destroyed:
                            Controller.pocket.set_engine_power_percent(Controller.pocket.engine.power_percent - 10)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # start camera drag
                    mouse_pos = pygame.mouse.get_pos()
                    drag_origin_x, drag_origin_y = Camera.g_position_to_logical(mouse_pos)
                    drag = True
                elif event.button == 4:  # scale up
                    Camera.scaling(SCALE_UP_SPEED)
                elif event.button == 5:  # scale down
                    Camera.scaling(SCALE_DOWN_SPEED)
            if event.type == pygame.MOUSEMOTION and drag:  # camera drag
                x, y = Camera.g_position_to_logical(pygame.mouse.get_pos())
                Camera.position_x -= x - drag_origin_x
                Camera.position_y -= y - drag_origin_y
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # end camera drag
                    drag = False
                    if mouse_pos == pygame.mouse.get_pos():
                        if Controller.add_targets_mode is False:
                            Controller.pocket = None
                        for ship in fleet:
                            if ship.is_clicked(Camera.g_position_to_logical(mouse_pos)):
                                if Controller.add_targets_mode is True and Controller.pocket and not Controller.pocket.bot and ship.bot:
                                    Controller.pocket.strategy.targets.append(ship)
                                else:
                                    Controller.pocket = ship
                if event.button == 3:
                    if Controller.pocket:
                        if not Controller.pocket.bridge.destroyed:
                            if Controller.path_mode:
                                Controller.pocket.course_array.append(Camera.g_position_to_logical(pygame.mouse.get_pos()))
                            else:
                                if len(Controller.pocket.course_array) == 0:
                                    Controller.pocket.course_array.append(Camera.g_position_to_logical(pygame.mouse.get_pos()))
                                else:
                                    Controller.pocket.course_array[0] = Camera.g_position_to_logical(pygame.mouse.get_pos())

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:  # camera move
            if keys[pygame.K_LEFT]:
                Camera.velocity_x -= CAMERA_VEL_CHANGE / Camera.scale
            if keys[pygame.K_RIGHT]:
                Camera.velocity_x += CAMERA_VEL_CHANGE / Camera.scale
            if keys[pygame.K_UP]:
                Camera.velocity_y += CAMERA_VEL_CHANGE / Camera.scale
            if keys[pygame.K_DOWN]:
                Camera.velocity_y -= CAMERA_VEL_CHANGE / Camera.scale
        else:  # slowing down camera (when keys not pressed) until stop
            Camera.breaking()

        Camera.update_pos()  # updating camera position by velocity

        Controller.manage_game(screen, game_factor)

        pygame.display.update()
        clock.tick(FPS)
        Controller.clock_FPS = clock.get_fps()

        Camera.time += game_factor
