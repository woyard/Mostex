import pygame
from constants import *


class MenuButton(pygame.sprite.Sprite):
    """
    an object for making mouse-interactive UI, the last button that was hovered
    on can be checked at last_butt and used when mouse is clicked
    """
    last_butt = None
    game = None
    menu_buttons = pygame.sprite.Group()

    def __init__(self, position, text, width, height, color, hil_color=MAGENTA,
                 padding=0.75):
        super().__init__()
        self.rect = pygame.Rect(position, (width, height))
        self.textrect = pygame.Rect(position,
                                    (int(width * padding),
                                     int(height * padding)))
        self.textrect.center = self.rect.center
        self.text = text
        self.color = self.def_color = color
        self.hil_color = hil_color
        self.font = pygame.font.Font('freesansbold.ttf', 30)
        self.image = self.font.render(text, True, BLACK)
        self.width = width
        self.height = height

    def update(self, mouse_pos):
        """
        draws itself to display, handles collisions with mouse
        :param mouse_pos:
        :return:
        """
        pygame.draw.rect(MenuButton.game.screen, self.color, self.rect)
        self.textrect.center = self.rect.center
        MenuButton.game.screen.blit(self.image, self.textrect)
        if self.rect.collidepoint(mouse_pos):
            MenuButton.last_butt = self
            self.color = self.hil_color
        else:
            self.color = self.def_color

    @classmethod
    def load_game_rq(cls, game):
        """
        loads a reference to the 'game' game handler object to avoid circular
        import issues after splitting into multiple files
        :param game:
        :return:
        """
        MenuButton.game = game


class MenuTray:
    """
    object for making fancy unfolding animations and managing an array of
    buttons
    """

    def __init__(self, location, text, width, height, color, direction, spacing,
                 *menu_buttons):
        """
        initializes the tray object and creates a cover button that can fold
        and unfold the tray. also puts all the included buttons into a sprite
        group that is only updated when the tray is not folded
        :param location:
        :param text:
        :param width:
        :param height:
        :param color:
        :param direction:
        :param spacing:
        :param menu_buttons:
        """
        self.cover_button = MenuButton(location, text, width, height, color)
        self.cover_button.add(MenuButton.menu_buttons)
        self.direction = direction
        self.location = location
        if self.direction in ("+x", "-x"):
            self.extn_spacing = spacing
            self.fold_spacing = -width
        else:
            self.extn_spacing = spacing
            self.fold_spacing = -height
        self.curr_spacing = 0
        self.buttons = pygame.sprite.Group()
        self.buttons.add(menu_buttons)
        self.folded = True

    def update(self, mouse_pos):
        """
        handles update of the tray, gradual extension and folding
        :param mouse_pos:
        :return:
        """
        if self.folded:
            if self.curr_spacing >= self.fold_spacing:
                self.curr_spacing -= 1
                self.display_menu_tray(self.curr_spacing)
                self.buttons.update(mouse_pos)
        elif not self.folded:
            if self.curr_spacing <= self.extn_spacing:
                self.curr_spacing += 1
                self.display_menu_tray(self.curr_spacing)
            self.buttons.update(mouse_pos)

    def display_menu_tray(self, spacing):
        """
        displays a tray at set extension
        :param spacing:
        :return:
        """
        x = self.location[0]
        y = self.location[1]
        if self.direction == "-x":
            for button in self.buttons:
                x -= spacing + button.width
                button.rect.topleft = (x, y)
        elif self.direction == "+x":
            for button in self.buttons:
                x += (spacing + button.width)
                button.rect.topleft = (x, y)
        elif self.direction == "-y":
            for button in self.buttons:
                y += (spacing + button.height)
                button.rect.topleft = (x, y)
        elif self.direction == "+y":
            for button in self.buttons:
                y -= (spacing + button.height)
                button.rect.topleft = (x, y)
        else:
            raise Exception(
                "unknown direction input! possible:('+x'', '-x', '+y', '-y')")

    def toggle_tray(self):
        """
        toggles whether the tray is folded or unfolded,
        called in main when the button is pressed
        :return:
        """
        if self.folded:
            self.folded = False
        else:
            self.folded = True


class DataDisplay(pygame.sprite.Sprite):
    """
    a simple object for printing various counters and such to the display
    """
    data_displays = pygame.sprite.Group()
    game = None

    def __init__(self, position, width, height, data, color):
        """
        initializes a data display object that handles printing data onto the
        display
        :param position:
        :param width:
        :param height:
        :param data:
        :param color:
        """
        super().__init__()
        self.position = position
        self.font = pygame.font.Font('freesansbold.ttf', 30)
        self.stuff_to_display = data
        self.color = color
        self.image = self.font.render(str(self.stuff_to_display), True,
                                      self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position
        self.add(DataDisplay.data_displays)

    def update(self):
        """
        draws the text image to display
        :return:
        """
        DataDisplay.game.screen.blit(self.image, self.rect)

    def display_data(self, data, position=None, color=None):
        """
        updates the displayed text image
        :param data:
        :param position:
        :param color:
        :return:
        """
        self.stuff_to_display = data
        if color is not None:
            self.color = color
        self.image = self.font.render(str(self.stuff_to_display), True,
                                      self.color)
        self.rect = self.image.get_rect()
        if position is not None:
            self.rect.topleft = position
        else:
            self.rect.topleft = self.position

    @classmethod
    def load_game_rq(cls, game):
        """
        loads a reference to the 'game' game handler object to avoid circular
        import issues after splitting into multiple files
        :param game:
        :return:
        """
        DataDisplay.game = game
