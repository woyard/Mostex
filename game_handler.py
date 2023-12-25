import pickle
import pygame
from phys import Beam, Node
from cars import Car
from ui_prefabs import *
from constants import *


class Game:
    """
    a game handler object that stores game-wide information that can be accessed
    by other objects
    """
    def __init__(self):
        """
        initializes the game handler, loads some ui elements that need to
        accessed from other parts of the program
        """
        pygame.init()
        pygame.key.set_repeat(25, 5)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.window = self.screen.get_rect()
        self.curr_beam_type = "normal"
        self.curr_node_type = "normal"
        self.is_level_editing_on = False
        self.water_level = 0
        self.car_pool = None
        self.spawn_index = 0
        self.spawned_cars = 0
        self.base_levelname = "savegame"
        self.curr_levelname = "savegame"
        self.gamemode = "builder"
        self.state = "normal"
        self.money = 0
        self.budget = 1000
        self.death_toll = 0
        self.background = pygame.image.load("level0.png").convert()
        self.money_disp = DataDisplay((460, 10), 300, 40,
                                      "will print remaining budget", BLACK)
        self.cost_disp = DataDisplay((750, 50), 300, 40, "", RED)
        self.build_disp = DataDisplay((1150, 50), 300, 40,
                                      f"beam type: {self.curr_beam_type}",
                                      BLACK)
        self.death_disp = DataDisplay((1150, 100), 300, 40, "", RED)

    def clear_all_sprites(self):
        """
        empties all sprite groups
        (hopefully the contents get garbage collected)
        :return:
        """
        Beam.beams.empty()
        Node.nodes.empty()
        Car.cars.empty()
        Beam.paved_beams.empty()

    def clear_player_sprites(self):
        """
        deletes all player created sprites
        (hopefully the contents get garbage collected)
        :return:
        """
        Car.cars.empty()
        for beam in Beam.beams:
            if beam.type != "ground":
                beam.kill()
        for node in Node.nodes:
            if not node.anchored:
                node.kill()
        self.update_money(0, True)

    def change_gamemode(self, gamemode):
        """
        handles changing of game mode, starts and stops spawning of cars
        on toggle
        :param gamemode:
        :return:
        """
        if gamemode == "builder":
            if self.gamemode == "simulation":
                self.load_game(self.curr_levelname)
            Node.is_gravity_on = False
            Node.is_frozen = True
            self.gamemode = "builder"
            pygame.time.set_timer(CAR_SPAWN, 0)
        elif gamemode == "simulation":
            if self.gamemode == "builder":
                self.save_game(self.curr_levelname)
                self.update_death_toll(0, True)
                self.spawn_index = 0
                self.spawned_cars = 0
                self.spawn_car()
            Node.is_gravity_on = True
            Node.is_frozen = False
            self.gamemode = "simulation"
        elif gamemode == "creative":
            self.gamemode = "creative"

    def toggle_level_editing(self):
        """
        dev tool for building collision beams in levels
        :return:
        """
        if self.is_level_editing_on:
            self.is_level_editing_on = False
            self.curr_node_type = "normal"
            self.curr_beam_type = "normal"
            Beam.show_hidden = False
            Node.show_hidden = False
            Car.show_hidden = False
        else:
            self.is_level_editing_on = True
            self.curr_node_type = "ground"
            self.curr_beam_type = "ground"
            Beam.show_hidden = True
            Node.show_hidden = True
            Car.show_hidden = True

    def change_built_type(self):
        """
        changes the beam/node type being built
        :return:
        """
        if self.is_level_editing_on:
            self.curr_beam_type = "ground"
            if self.curr_node_type == "ground":
                self.curr_node_type = "based"
            else:
                self.curr_node_type = "ground"
        else:
            if self.curr_beam_type == "paved":
                self.curr_beam_type = "cable"
            elif self.curr_beam_type == "normal":
                self.curr_beam_type = "paved"
            else:
                self.curr_beam_type = "normal"
        self.build_disp.display_data(f"beam type: {self.curr_beam_type}")

    def chck_beam_cost(self, mouse_pos, incur_cost=False):
        """
        calculates and displays the cost of currently constructed beam
        also handles decreasing the money pool when the beam is finally
        built
        :param mouse_pos:
        :param incur_cost:
        :return:
        """
        beam_length = (Node.temp_node.x - mouse_pos[0]) ** 2 + (
                Node.temp_node.y - mouse_pos[1]) ** 2
        cost = round(
            beam_length / 100000 * Beam.property_sets[self.curr_beam_type][
                'cost'], 3)
        self.cost_disp.display_data(f"-{cost} mln PLN")
        self.cost_disp.update()
        if incur_cost and self.gamemode != "creative":
            if self.money >= cost:
                self.update_money(-cost)
                return True
            else:
                return False
        return True

    def update_money(self, money_delta, reset=False):
        """
        updates the money display and handle resets to original budget
        :param money_delta:
        :param reset:
        :return:
        """
        if reset:
            self.money = self.budget
            self.money_disp.display_data(
                f"remaining budget:{self.money} mln PLN")
            self.money_disp.update()
        else:
            self.money = round(self.money + money_delta, 3)
            self.money_disp.display_data(
                f"remaining budget:{self.money} mln PLN")
            self.money_disp.update()

    def update_death_toll(self, new_deaths, reset=False):
        """
        updates the death toll displays, also handles resets to 0
        :param new_deaths:
        :param reset:
        :return:
        """
        if reset:
            self.death_toll = 0
            self.death_disp.display_data("")
        else:
            self.death_toll += new_deaths
            if self.death_toll == 1:
                self.death_disp.display_data(
                    f"death toll: {1} soul")
            else:
                self.death_disp.display_data(
                    f"death toll: {self.death_toll} souls")

    def spawn_car(self):
        """
        handles spawning of cars by creating a timer based on the time specified
        in the current level's car_pool
        :return:
        """
        if self.car_pool[0][1] == 0:
            pygame.time.set_timer(CAR_SPAWN, self.car_pool[0][0])
            Car((self.window.right + 100, self.window.centery))
            return  # an infinite stream of cars
        elif self.spawn_index >= len(self.car_pool):
            if len(Car.cars.sprites()) == 0:
                pygame.time.set_timer(CAR_SPAWN, 0)
                if self.death_toll > 0:
                    self.state = "failure"
                else:
                    self.state = "success"
                self.update_death_toll(0, reset=True)
        else:
            pygame.time.set_timer(CAR_SPAWN, self.car_pool[self.spawn_index][0])
            Car((self.window.right + 100, self.window.centery))
            self.spawned_cars += 1
            if self.spawned_cars > self.car_pool[self.spawn_index][1]:
                self.spawn_index += 1
                self.spawned_cars = 0

    def save_game(self, save_name="level1"):
        print(f"saving game '{save_name}'")
        node_list = []
        beam_list = []
        for i, node in enumerate(Node.nodes):
            node.id = i
            node_list.append(node.save_node())
        for beam in Beam.beams:
            if beam.for_saving:
                beam_list.append(beam.save_beam())
        with open("savegames/"+save_name, "wb") as f:
            pickle.dump((node_list, beam_list, self.money), f)

    def load_game(self, save_name="savegame"):
        print(f"loading saved game '{save_name}'")
        try:
            with open("savegames/"+save_name, "rb") as f:
                saved_level = pickle.load(f)
                node_list = saved_level[0]
                beam_list = saved_level[1]
                saved_money = saved_level[2]
            self.update_money(saved_money - self.money)
            self.clear_all_sprites()
            node_ref_list = []
            for saved_node in node_list:
                node_ref_list.append(Node(saved_node.center, saved_node.type))
            for saved_beam in beam_list:
                Beam(node_ref_list[saved_beam.id1],
                     node_ref_list[saved_beam.id2], saved_beam.type,
                     saved_beam.base_length)
        except Exception as exception:
            print(f"Error loading save file: {exception}")
