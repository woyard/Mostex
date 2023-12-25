import pygame
import math
from constants import *


class Beam(pygame.sprite.Sprite):
    """
    a physics objects that exerts force on two connected nodes when in tension
    or compression, can also be collided with by cars
    """
    property_sets = {
        "paved": {"for_saving": True, "is_vis": True, "is_solid": True,
                  "k_tens": 20000, "k_comp": -20000, "thick": 10,
                  "max_force": 30000, "fail_anim_len": 15, "color": D_GRAY,
                  "cost": 300, "preload": 1},
        "car_spring": {"for_saving": False, "is_vis": False, "is_solid": False,
                       "k_tens": 4000, "k_comp": -4000, "thick": 3,
                       "max_force": 90000, "fail_anim_len": 15, "color": WHITE,
                       "cost": 0, "preload": 1},
        "car_frame": {"for_saving": False, "is_vis": False, "is_solid": False,
                      "k_tens": 8000, "k_comp": -8000, "thick": 3,
                      "max_force": 90000, "fail_anim_len": 15, "color": WHITE,
                      "cost": 0, "preload": 1},
        "normal": {"for_saving": True, "is_vis": True, "is_solid": False,
                   "k_tens": 20000, "k_comp": -20000, "thick": 5,
                   "max_force": 30000, "fail_anim_len": 15, "color": D_BLUE,
                   "cost": 100, "preload": 1},
        "cable": {"for_saving": True, "is_vis": True, "is_solid": False,
                  "k_tens": 20000, "k_comp": -0, "thick": 2, "max_force": 50000,
                  "fail_anim_len": 15, "color": BLACK, "cost": 1,
                  "preload": 0.994},
        "ground": {"for_saving": True, "is_vis": False, "is_solid": True,
                   "k_tens": 20000, "k_comp": -20000, "thick": 10,
                   "max_force": None, "fail_anim_len": 15, "color": ORANGE,
                   "cost": 0, "preload": 1}}
    show_hidden = False
    show_force_colors = True
    last_built = None
    game = None
    paved_beams = pygame.sprite.Group()
    beams = pygame.sprite.Group()

    def __init__(self, node1, node2, curr_type="normal", base_length=None):
        """
        creates a Beam object between two nodes, retrieves and stores properties
        from the property sets dict, stores references to nodes for updating
        forces
        :param node1:
        :param node2:
        :param curr_type:
        :param base_length:
        """
        super().__init__()
        self.type = curr_type
        self.properties = Beam.property_sets[self.type]
        self.for_saving = self.properties["for_saving"]
        self.is_vis = self.properties["is_vis"]
        self.k_tens = self.properties["k_tens"]
        self.k_comp = self.properties["k_comp"]
        self.thickness = self.properties["thick"]
        self.max_force = self.properties["max_force"]
        self.fail_anim_len = self.properties["fail_anim_len"]
        self.def_color = self.color = self.properties["color"]

        self.node1 = node1
        self.node2 = node2
        self.dx = abs(self.node1.x - self.node2.x)
        self.dy = abs(self.node1.y - self.node2.y)
        self.Fx = 0
        self.Fy = 0
        self.F_total = 0
        self.breaking = 0
        if base_length is None:
            self.base_length = self.curr_length = math.sqrt(
                self.dx ** 2 + self.dy ** 2)
        else:
            self.base_length = self.curr_length = base_length

        self.base_length *= self.properties["preload"]

        if Beam.property_sets[self.type]["is_solid"]:
            self.add(Beam.paved_beams)
        self.add(Beam.beams)
        if node1.x == node2.x and node1.y == node2.y:
            self.delete_beam()
        if self.for_saving:
            Beam.last_built = self

    def update(self):
        """
        manages all update functionality of the object
        :return:
        """
        if self.node1.for_del or self.node2.for_del:
            self.delete_beam()
        elif self.breaking != 0:  # rendering simple breaking animation
            self.breaking -= 1
            pygame.draw.line(Beam.game.screen, WHITE, self.node1.center,
                             self.node2.center,
                             self.fail_anim_len - self.breaking)
            if self.breaking <= 0:
                self.delete_beam(False)
        else:  # normal element behaviour
            if self.max_force is not None:
                self.dx = abs(self.node1.x - self.node2.x)
                self.dy = abs(self.node1.y - self.node2.y)
                if self.dx != 0 or self.dy != 0:
                    self.update_physics()  # preventing div by 0 errors
                if Beam.game.gamemode == "simulation":
                    self.check_for_failure()
                if Beam.show_force_colors:
                    self.paint_force_colors()
            if self.is_vis or Beam.show_hidden:
                pygame.draw.line(Beam.game.screen, self.color,
                                 self.node1.center, self.node2.center,
                                 self.thickness)

    def update_physics(self):
        """
        updates the forces exerted on the connected nodes
        :return:
        """
        self.curr_length = math.sqrt(self.dx ** 2 + self.dy ** 2)
        if self.base_length > self.curr_length:
            self.F_total = abs(
                self.base_length - self.curr_length) * self.k_comp
        else:
            self.F_total = abs(
                self.base_length - self.curr_length) * self.k_tens
        # if self.node1.anchored or self.node2.anchored:
        #     self.F_total *= 2  # newtons third law (maybe)
        self.Fx = self.F_total * self.dx / (self.dx + self.dy)
        self.Fy = self.F_total - self.Fx
        if self.node1.x > self.node2.x:
            self.node1.Fx -= self.Fx
            self.node2.Fx += self.Fx
        else:
            self.node1.Fx += self.Fx
            self.node2.Fx -= self.Fx
        if self.node1.y > self.node2.y:
            self.node1.Fy -= self.Fy
            self.node2.Fy += self.Fy
        else:
            self.node1.Fy += self.Fy
            self.node2.Fy -= self.Fy

    def collide_beam(self, colliding_node):
        """
        checks for collisions with a car wheel node, called from the car object.
        updates the forces on the wheel and its nodes using simple analytic
        geometry
        :param colliding_node:
        :return:
        """
        if min(self.node1.x, self.node2.x) <= colliding_node.x <= max(
                self.node1.x, self.node2.x):
            xc = colliding_node.x
            yc = colliding_node.y
            a_coefficient = (self.node1.y - self.node2.y) / (
                    self.node1.x - self.node2.x)
            y_diff = abs(self.thickness * self.dx / self.curr_length)
            if yc + y_diff > a_coefficient * (
                    xc - self.node1.x) + self.node1.y > yc - y_diff * 2:
                x_diff = abs(self.thickness * self.dy / self.curr_length)
                xd = ((a_coefficient *
                      (a_coefficient * self.node1.x + yc - self.node1.y) + xc)
                      / (a_coefficient ** 2 + 1))
                yd = a_coefficient * (xd - self.node1.x) + self.node1.y
                colliding_node.y = yd - y_diff * 1.1
                self.node1.Fy += colliding_node.Fy * abs(
                    (self.node1.x - xc) / self.dx)
                self.node2.Fy += colliding_node.Fy * abs(
                    (self.node2.x - xc) / self.dx)
                if a_coefficient < 0:
                    colliding_node.x = xd - x_diff * 1.1
                else:
                    colliding_node.x = xd + x_diff * 1.1
                colliding_node.Fy = 0
                return True
        return False

    def paint_force_colors(self):
        """
        blends the beam color based on the forces its exerting on nodes
        blue - base
        red - compression
        green - tension
        :return:
        """
        if self.base_length > self.curr_length:
            if abs(self.F_total) / self.max_force * 1.2 >= 1:
                self.color = (255, 0, self.def_color[2])
            else:
                self.color = (
                    int(abs(self.F_total / self.max_force) * 1.2 * 255), 0,
                    self.def_color[2])
        else:
            if abs(self.F_total) / self.max_force * 1.2 >= 1:
                self.color = (0, 255, self.def_color[2])
            else:
                self.color = (
                    0, int(abs(self.F_total / self.max_force) * 1.2 * 255),
                    self.def_color[2])

    def check_for_failure(self):
        """
        checks if the force the beam is exerting is greater than its maximum
        strength
        :return:
        """
        if self.breaking == 0 and self.F_total > self.max_force:
            self.breaking = self.fail_anim_len

    def delete_beam(self, refundable=True):
        """
        handles beam deletion and refunding when playing with limited resources
        :param refundable:
        :return:
        """
        Beam.last_built = None
        if refundable:
            Beam.game.update_money(Beam.property_sets[self.type][
                                       "cost"] / 100000 * self.base_length ** 2)
        self.kill()

    class SavedBeam:
        """
        basically a named tuple for storing saved beam values
        """

        def __init__(self, node1_id, node2_id, beam_type, base_length):
            self.id1 = node1_id
            self.id2 = node2_id
            self.type = beam_type
            self.base_length = base_length

    def save_beam(self):
        """
        if the object is marked as for_saving, the function returns a SavedBeam
        object of the values needed to recreate the beam when reloading the game
        """
        if self.for_saving:
            return Beam.SavedBeam(self.node1.id, self.node2.id, self.type,
                                  self.base_length *
                                  (1 / Beam.property_sets[self.type][
                                      "preload"]))
        else:
            return None

    @classmethod
    def load_game_rq(cls, game):
        """
        loads a reference to the 'game' game handler object to avoid circular
        import issues after splitting into multiple files
        :param game:
        :return:
        """
        Beam.game = game


class Node(pygame.sprite.Sprite):
    """
    a class for Node physics objects, basically material points with inertia and
    gravity that Beam objects connected to them can act upon with forces
    """
    property_sets = {
        "normal": {"is_vis": True, "def_Fg": 1500, "mass": 3000, "damp_fact": 3,
                   "radius": 9, "def_color": YELLOW, "hil_color": MAGENTA,
                   "anchored": False, "window_coll": True},
        "car_custom": {"is_vis": False, "def_Fg": None, "mass": None,
                       "damp_fact": 3, "radius": 7, "def_color": GRAY,
                       "hil_color": MAGENTA, "anchored": False,
                       "window_coll": False},
        "car_light": {"is_vis": False, "def_Fg": 200, "mass": 100,
                      "damp_fact": 2, "radius": 6, "def_color": GRAY,
                      "hil_color": MAGENTA, "anchored": False,
                      "window_coll": False},
        "car_wheel": {"is_vis": True, "def_Fg": 200, "mass": 100,
                      "damp_fact": 2, "radius": 12, "def_color": GRAY,
                      "hil_color": MAGENTA, "anchored": False,
                      "window_coll": False},
        "based": {"is_vis": True, "def_Fg": 1000, "mass": 250, "damp_fact": 1,
                  "radius": 11, "def_color": GRAY, "hil_color": MAGENTA,
                  "anchored": True, "window_coll": False},
        "ground": {"is_vis": False, "def_Fg": 1000, "mass": 250, "damp_fact": 1,
                   "radius": 11, "def_color": ORANGE, "hil_color": MAGENTA,
                   "anchored": True, "window_coll": False}}
    DEL_RANGE = 200

    is_gravity_on = True
    is_frozen = False
    show_force_lines = False
    show_hidden = False

    last_node = None
    temp_node = None

    game = None
    nodes = pygame.sprite.Group()

    def __init__(self, center, curr_type="normal", def_fg=None, mass=None):
        """
        creates aa Node object at a position center, loads values from the
        property sets dict based on the type
        :param center:
        :param curr_type:
        :param def_fg:
        :param mass:
        """
        super().__init__()
        self.id = None  # used for data serialization when saving game-state
        self.type = curr_type
        self.properties = Node.property_sets[self.type]
        self.is_vis = self.properties["is_vis"]
        self.anchored = self.properties["anchored"]
        self.Fg = self.properties["def_Fg"]
        self.mass = self.properties["mass"]
        self.radius = self.properties["radius"]
        self.damp_factor = self.properties["damp_fact"]
        self.def_color = self.properties["def_color"]
        self.hil_color = self.properties["hil_color"]
        self.collideable_with_game_window = self.properties["window_coll"]
        if self.type == "car_custom":
            if def_fg is None or mass is None:
                raise Exception("custom node created without critical data")
            else:
                self.Fg = def_fg
                self.mass = mass
        self.for_del = False
        self.color = self.def_color
        self.center = center
        self.x = center[0]
        self.y = center[1]
        self.vx = 0
        self.vy = 0
        self.Fx = 0
        self.Fy = self.Fg
        self.Ftx = 0  # Friction force in x
        self.Fty = 0  # Friction force in y
        if self.type not in ("car_wheel", "car_custom", "car_light"):
            self.add(Node.nodes)

    def check_mouse(self, mouse):
        """
        checks for collision with the mouse, updates the reference last_node
        to itself
        :param mouse:
        :return:
        """
        if (mouse[0] - self.x) ** 2 + (
                mouse[1] - self.y) ** 2 <= self.radius ** 2 * 3:
            self.color = self.hil_color
            Node.last_node = self
        else:
            self.color = self.def_color

    def update(self, mouse, delta_t=0.1):
        """
        handles updating for the node objects, the delta_t argument regulates
        the speed & time resolution of the simulation at a given framerate
        :param mouse:
        :param delta_t:
        :return:
        """
        if self.for_del:
            self.kill()
        if not self.anchored:
            self.update_physics(delta_t)
        self.center = (self.x, self.y)
        if self.is_vis or Node.show_hidden:
            self.check_mouse(mouse)
            pygame.draw.circle(Node.game.screen, self.color, self.center,
                               self.radius)
        if Node.show_force_lines:
            pygame.draw.line(Node.game.screen, GRAY, self.center,
                             (self.x + self.Fx, self.y + self.Fy), 1)
        # resetting the forces for the next simulation tick:
        self.Fx = 0
        if Node.is_gravity_on:
            self.Fy = self.Fg
        else:
            self.Fy = 0
        if Node.is_frozen:
            self.vx = 0
            self.vy = 0

    def update_physics(self, delta_t):
        """
        updates the nodes velocity based on its mass and currently acting forces
        also includes a friction and damping component to stabilize the sim
        :param delta_t:
        :return:
        """
        self.Ftx = self.vx * abs(self.vx) * self.damp_factor
        self.Fty = self.vy * abs(self.vy) * self.damp_factor
        if abs(self.Ftx) > abs(self.Fx):
            self.vx *= 0.99
        else:
            self.vx += (self.Fx - self.Ftx) / self.mass * delta_t
        if abs(self.Fty) > abs(self.Fy):
            self.vy *= 0.99
        else:
            self.vy += (self.Fy - self.Fty) / self.mass * delta_t
        if self.vx < 0.01:
            self.vx *= 0.99
        if self.vy < 0.01:
            self.vy *= 0.99
        self.x += self.vx * delta_t
        self.y += self.vy * delta_t
        if self.collideable_with_game_window:
            if self.x < Node.game.window.left:
                self.x = Node.game.window.left
                self.vx *= -0.5
            elif self.x > Node.game.window.right:
                self.x = Node.game.window.right
                self.vx *= -0.5
            if self.y > Node.game.window.bottom:
                self.y = Node.game.window.bottom
                self.vy *= -0.5
            if self.y < Node.game.window.top:
                self.y = Node.game.window.top
                self.vy *= -0.5
        elif (self.x > Node.game.window.right + Node.DEL_RANGE or
              self.x < Node.game.window.left - Node.DEL_RANGE or
              self.y > Node.game.window.bottom + Node.DEL_RANGE or
              self.y < Node.game.window.top - Node.DEL_RANGE):
            self.delete_node()

    def delete_node(self):
        """
        marks the node for deletion so the connected beams know they are no
        longer connected to anything in the next update tick, the Node is
        deleted shortly after
        :return:
        """
        self.for_del = True

    class SavedNode:
        """
        basically a named tuple for storing node data when saving
        """

        def __init__(self, center, node_type, node_id):
            self.center = center
            self.type = node_type
            self.id = node_id

    def save_node(self):
        """
        returns a SavedNode object with all the values necessary to recreate the
        Node when reloading the save
        :return:
        """
        return Node.SavedNode(self.center, self.type, self.id)

    @classmethod
    def switch_gravity(cls):
        """
        toggles the class-wide gravity setting
        :return:
        """
        if Node.is_gravity_on:
            Node.is_gravity_on = False
        else:
            Node.is_gravity_on = True

    @classmethod
    def load_game_rq(cls, game):
        """
        loads a reference to the 'game' game handler object to avoid circular
        import issues after splitting into multiple files
        :param game:
        :return:
        """
        Node.game = game
