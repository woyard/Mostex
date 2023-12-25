import math
import pygame
import phys


class Car(pygame.sprite.Sprite):
    """
    a class for simulating and displaying a car over a frame created from
    my phys.py beams and nodes
    """
    car_image = pygame.image.load("test_car.png")
    game = None
    show_hidden = False
    cars = pygame.sprite.Group()

    def __init__(self, center, body_l=40, body_h=20, susp_l=30, susp_h=20,
                 def_fg=1500, mass=1000):
        """
        creates the car and its physics components to simulate a basic frame
        and suspension, the dimensions can be quite freely adjusted
        :param center:
        :param body_l:
        :param body_h:
        :param susp_l:
        :param susp_h:
        :param def_fg:
        :param mass:
        """
        super().__init__()
        self.car_nodes = pygame.sprite.Group()
        self.image = Car.car_image
        self.rect = Car.car_image.get_rect()
        self.center = center
        self.cntrx = center[0]
        self.cntry = center[1]
        self.wheel1 = phys.Node(
            (self.cntrx - (body_l + susp_l) / 2, self.cntry + susp_h),
            "car_wheel")
        self.wheel2 = phys.Node(
            (self.cntrx + (body_l + susp_l) / 2, self.cntry + susp_h),
            "car_wheel")
        self.suspNode1l = phys.Node(
            (self.cntrx - body_l / 2 - susp_l, self.cntry), "car_light")
        self.suspNode1r = phys.Node((self.cntrx - body_l / 2, self.cntry),
                                    "car_custom", def_fg, mass)
        self.suspNode2r = phys.Node(
            (self.cntrx + body_l / 2 + susp_l, self.cntry), "car_light")
        self.suspNode2l = phys.Node((self.cntrx + body_l / 2, self.cntry),
                                    "car_custom", def_fg, mass)
        self.frameNodel = phys.Node(
            (self.cntrx - body_l / 2 - susp_l / 2, self.cntry - body_h),
            "car_light")
        self.frameNoder = phys.Node(
            (self.cntrx + body_l / 2 + susp_l / 2, self.cntry - body_h),
            "car_light")

        self.car_nodes.add(self.wheel1, self.wheel2, self.suspNode1l,
                           self.suspNode1r, self.suspNode2r, self.suspNode2l,
                           self.frameNoder, self.frameNodel)

        phys.Beam(self.suspNode1l, self.frameNodel, "car_frame")
        phys.Beam(self.suspNode1r, self.frameNodel, "car_frame")
        phys.Beam(self.suspNode2l, self.frameNoder, "car_frame")
        phys.Beam(self.suspNode2r, self.frameNoder, "car_frame")
        phys.Beam(self.frameNodel, self.frameNoder, "car_frame")
        phys.Beam(self.frameNoder, self.suspNode1r, "car_frame")
        phys.Beam(self.frameNodel, self.suspNode2l, "car_frame")
        phys.Beam(self.suspNode1l, self.suspNode1r, "car_frame")
        phys.Beam(self.suspNode2l, self.suspNode2r, "car_frame")
        phys.Beam(self.suspNode1r, self.suspNode2l, "car_frame")
        phys.Beam(self.wheel1, self.suspNode1l, "car_spring")
        phys.Beam(self.wheel1, self.suspNode1r, "car_spring")
        phys.Beam(self.wheel2, self.suspNode2l, "car_spring")
        phys.Beam(self.wheel2, self.suspNode2r, "car_spring")
        phys.Beam(self.wheel2, self.wheel1, "car_spring")
        self.add(Car.cars)

    def update(self, mouse):
        """
        handles updates for the car object, makes the wheels check for collision
        with paved beams
        :param mouse:
        :return:
        """

        for node in self.car_nodes:
            if node.for_del:
                self.delete_car()
                break
        for beam in phys.Beam.paved_beams:
            if beam.collide_beam(self.wheel1):
                self.wheel1.Fx -= 1000
                self.suspNode1r.Fx -= 1000
            if beam.collide_beam(self.wheel2):
                self.wheel2.Fx -= 1000
                self.suspNode2l.Fx -= 1000
        self.center = ((self.suspNode1r.x + self.suspNode2l.x) / 2,
                       (self.suspNode1r.y + self.suspNode2l.y) / 2)
        self.car_nodes.update(mouse)
        if not Car.show_hidden:
            self.draw_car_body()

    def draw_car_body(self):
        """
        rotates and blits an image over the physics frame underneath
        :return:
        """
        if abs(self.frameNodel.y - self.frameNoder.y) == 0:
            angle = 0
        else:
            angle = math.atan((self.frameNodel.y - self.frameNoder.y) / (
                        self.frameNodel.x - self.frameNoder.x))
        if self.frameNodel.x >= self.frameNoder.x:
            self.image = pygame.transform.rotate(Car.car_image,
                                                 -angle / 3.14 * 180 + 180)
            self.rect = self.image.get_rect()
            self.rect.center = self.center
        else:
            self.image = pygame.transform.rotate(Car.car_image,
                                                 -angle / 3.14 * 180)
            self.rect = self.image.get_rect()
            self.rect.center = self.center
        Car.game.screen.blit(self.image, self.rect)

    def delete_car(self):
        """
        handles deletion of the car object and its physics components, also
        check whether the car fell off from the bridge and updates death toll
        :return:
        """
        if Car.game.window.left < self.center[0] < Car.game.window.right:
            Car.game.update_death_toll((int(self.center[0]) % 3) + 1)
        for node in self.car_nodes:
            node.delete_node()
        self.kill()

    @classmethod
    def load_game_rq(cls, game):
        """
        loads a reference to the 'game' game handler object to avoid circular
        import issues after splitting into multiple files
        :param game:
        :return:
        """
        Car.game = game
