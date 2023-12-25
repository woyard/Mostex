import pygame
import sys
from phys import Beam, Node
from cars import Car
from constants import *
from game_handler import Game
from ui_prefabs import *


class Level:
    def __init__(self, level_name, bckgr_name, car_pool, water_level, budget):
        self.background_file = bckgr_name
        self.level_name = level_name
        self.car_pool = car_pool
        self.water_level = water_level
        self.budget = budget

    def load(self):
        game.change_gamemode("builder")
        game.load_game(self.level_name)
        game.water_level = self.water_level
        game.base_levelname = self.level_name
        game.curr_levelname = self.level_name + "_editor"
        game.car_pool = self.car_pool
        game.spawned_cars = 0
        game.background = pygame.image.load(self.background_file).convert()
        game.budget = self.budget
        game.update_money(0, True)


level0 = Level("level0", "level0.png", [(2000, 0)], 0, 9999)
level1 = Level("level1", "level1.png", [(3000, 3), (1500, 5), (900, 10)], 0,
               900)
level2 = Level("level2", "test_level_background.png",
               [(2500, 3), (1500, 5), (1000, 6), (1500, 2)], 0, 700)
level3 = Level("level3", "level3.png", [(4000, 3), (2000, 5), (1000, 5)], 0,
               800)


def welcome():
    """
    displays a welcome screen when the game is loaded,
    then waits for mouse input to continue
    """
    welcome_screen = pygame.image.load("welcome.png").convert()
    game.screen.blit(welcome_screen, game.window)
    pygame.display.flip()
    while get_event_key() is None:
        fps.tick(SET_FPS)
    game.state = "normal"


def success():
    """
    displays a success screen when the game is won,
    then waits for mouse input to continue
    """
    success_screen = pygame.image.load("great_success.png").convert()
    game.screen.blit(success_screen, game.window)
    pygame.display.flip()
    color = [0, 255, 100]
    d_color = [5, -2, 3]
    font = pygame.font.Font('freesansbold.ttf', 100)
    image = font.render("GREAT SUCCESS", True, color)
    rect = image.get_rect()
    rect.center = (800, 700)
    while get_event_key() is None:
        for i, delta in enumerate(d_color):
            if 0 < color[i] + delta < 255:
                color[i] += delta
            else:
                d_color[i] *= -1
        image = font.render("GREAT SUCCESS", True, color)
        game.screen.blit(image, rect)
        pygame.display.flip()
        fps.tick(SET_FPS)
    game.state = "normal"


def failure():
    """
    displays a failure screen when the game is lost,
    then waits for mouse input to continue
    """
    failure_screen = pygame.image.load("failure.png").convert()
    game.screen.blit(failure_screen, game.window)
    pygame.display.flip()
    color = [0, 255, 100]
    d_color = [5, -2, 3]
    font = pygame.font.Font('freesansbold.ttf', 300)
    image = font.render("FAILURE", True, color)
    rect = image.get_rect()
    rect.center = (800, 650)
    while get_event_key() is None:
        for i, delta in enumerate(d_color):
            if 0 < color[i] + delta < 255:
                color[i] += delta
            else:
                d_color[i] *= -1
        image = font.render("FAILURE", True, color)
        game.screen.blit(image, rect)
        pygame.display.flip()
        fps.tick(SET_FPS)
    game.state = "normal"


mouse_keys = {1: "r_mouse",
              2: "m_mouse",
              3: "l_mouse"}

was_up = {pygame.K_g: True,
          pygame.K_l: True,
          pygame.K_m: True,
          pygame.K_c: True,
          pygame.K_x: True,
          pygame.K_b: True,
          pygame.K_n: True,
          pygame.K_z: True}


def get_event_key():
    """
    scans the event queue for recognized events, also handles continuous press
    protection
    :return:
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            if event.key in was_up.keys() and was_up[event.key]:
                was_up[event.key] = False
                return event.key
        if event.type == pygame.KEYUP:
            if event.key in was_up.keys():
                was_up[event.key] = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in mouse_keys.keys():
                button = mouse_keys[event.button]
                if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                    return button + "_LCTRL"
                else:
                    return button
        if event.type == CAR_SPAWN:
            return "car_spawn"
    return None


if __name__ == "__main__":
    game = Game()
    fps = pygame.time.Clock()
    Beam.load_game_rq(game)
    Node.load_game_rq(game)
    Car.load_game_rq(game)
    MenuButton.load_game_rq(game)
    DataDisplay.load_game_rq(game)

    butt_l1 = MenuButton((0, 0), "level 1", 180, 40, YELLOW)
    butt_l2 = MenuButton((0, 0), "level 2", 180, 40, YELLOW)
    butt_l3 = MenuButton((0, 0), "level 3", 180, 40, YELLOW)
    butt_sav = MenuButton((0, 0), "save", 180, 40, ORANGE)
    butt_lod = MenuButton((0, 0), "load", 180, 40, ORANGE)
    tray1 = MenuTray((0, 0), "Select Level", 250, 40, YELLOW, "-y", 10, butt_l1,
                     butt_l2, butt_l3, butt_sav, butt_lod)
    butt_run = MenuButton((1300, 0), "Simulation Mode", 300, 40, ORANGE)
    butt_stp = MenuButton((1000, 0), "Editing Mode", 300, 40, YELLOW)
    butt_del = MenuButton((250, 0), "Delete All", 200, 40, RED)
    MenuButton.menu_buttons.add(butt_del, butt_run, butt_stp)

    welcome()
    level0.load()
    game.change_gamemode("simulation")
    running = True
    mouse_offset = 0
    while running:
        if game.state == "failure":
            failure()
        elif game.state == "success":
            success()
        mouse = list(pygame.mouse.get_pos())
        mouse[0] += mouse_offset
        key = get_event_key()
        if key == "car_spawn":
            game.spawn_car()
        elif key == pygame.K_g:
            Node.switch_gravity()
        elif key == pygame.K_l:
            game.load_game()
        elif key == pygame.K_m:
            game.save_game(game.base_levelname)
        elif key == pygame.K_n:
            game.save_game("welcome")
        elif key == pygame.K_c:
            Car(mouse)
        elif key == pygame.K_z:
            if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                if Beam.last_built is not None:
                    Beam.last_built.delete_beam()
        elif key == pygame.K_x:  # used for placing ground outside game window
            if mouse_offset == 0:
                if mouse[0] < game.window.centerx:
                    mouse_offset = -400
                else:
                    mouse_offset = 400
            else:
                mouse_offset = 0
        elif key == pygame.K_b:
            game.toggle_level_editing()
        elif key == "l_mouse":
            game.change_built_type()
        elif key == "r_mouse_LCTRL":
            if pygame.key.get_mods() & pygame.KMOD_LCTRL:
                if Node.last_node is not None:
                    Node.last_node.delete_node()
                else:
                    Node.temp_node = None
        elif key == "r_mouse":
            if MenuButton.last_butt is not None:
                if MenuButton.last_butt == tray1.cover_button:
                    tray1.toggle_tray()
                elif MenuButton.last_butt == butt_l1:
                    level1.load()
                elif MenuButton.last_butt == butt_l2:
                    level2.load()
                elif MenuButton.last_butt == butt_l3:
                    level3.load()
                elif MenuButton.last_butt == butt_lod:
                    game.load_game(game.base_levelname + "_saved")
                elif MenuButton.last_butt == butt_sav:
                    game.save_game(game.base_levelname + "_saved")
                elif MenuButton.last_butt == butt_run:
                    game.change_gamemode("simulation")
                elif MenuButton.last_butt == butt_stp:
                    game.change_gamemode("builder")
                elif MenuButton.last_butt == butt_del:
                    game.clear_player_sprites()
            elif Node.last_node is not None:
                if Node.temp_node is None:
                    Node.temp_node = Node.last_node
                elif Node.last_node == Node.temp_node:
                    Node.temp_node = None
                else:
                    if game.chck_beam_cost(mouse, True):
                        Beam(Node.last_node, Node.temp_node,
                             game.curr_beam_type)
                        Node.temp_node = None
            elif Node.temp_node is not None:
                if game.chck_beam_cost(mouse, True):
                    Beam(Node(mouse, game.curr_node_type), Node.temp_node,
                         game.curr_beam_type)
                    Node.temp_node = None
            elif game.is_level_editing_on:
                Node.temp_node = Node(mouse, game.curr_node_type)
        game.screen.fill(BLACK)
        game.screen.blit(game.background, game.window)
        if Node.temp_node is not None:
            game.chck_beam_cost(mouse, False)
            if Node.temp_node.for_del:
                Node.temp_node = None
            elif game.curr_beam_type == "paved":
                pygame.draw.circle(game.screen, D_BLUE, mouse, 7)
                pygame.draw.line(game.screen, D_BLUE, mouse,
                                 Node.temp_node.center, 10)
            elif game.curr_beam_type == "cable":
                pygame.draw.circle(game.screen, D_BLUE, mouse, 7)
                pygame.draw.line(game.screen, GRAY, mouse,
                                 Node.temp_node.center, 2)
            elif game.curr_beam_type == "ground":
                pygame.draw.line(game.screen, ORANGE, mouse,
                                 Node.temp_node.center, 10)
                if game.curr_node_type == "based":
                    pygame.draw.circle(game.screen, GRAY, mouse, 10)
                else:
                    pygame.draw.circle(game.screen, ORANGE, mouse, 10)
            else:
                pygame.draw.circle(game.screen, BLUE, mouse, 7)
                pygame.draw.line(game.screen, BLUE, mouse,
                                 Node.temp_node.center, 5)
        pygame.draw.circle(game.screen, WHITE, mouse, 1)
        Node.last_node = None
        MenuButton.last_butt = None
        Beam.beams.update()
        Car.cars.update(mouse)
        Node.nodes.update(mouse)
        tray1.update(mouse)
        MenuButton.menu_buttons.update(mouse)
        DataDisplay.data_displays.update()
        pygame.display.flip()
        if fps.get_fps() < SET_FPS * 0.90:
            print(fps.get_fps())
        fps.tick(SET_FPS)
