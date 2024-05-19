import pygame

import buttonClass
import color
import boundedValue


class Window:

    def __init__(self, game, config, controller):
        self.game = game
        self.controller = controller
        controller.window = self
        config |= game.config.window.basics

        self.x = config.x
        self.y = config.y

        self.view_x = boundedValue.BoundedValue(0, 0, 0)
        self.view_y = boundedValue.BoundedValue(0, 0, 0)

        self.content_height = 0

        self.font = pygame.font.SysFont("Courier New", 20)
        self.width = self.game.width if config.width == "_" else config.width
        self.height = self.game.height if config.height == "_" else config.height
        self.alpha = config.alpha
        self.background_color = color.BLACK
        self.writing_color = color.WHITE
        self.name = config.name
        self.border_x = 5
        self.border_y = 5
        self.moveable = config.moveable
        self.selectable = config.selectable
        self.closable = config.closable

        self.buttons = set()

        self.window = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.active = True
        self.content = None

        self.additionnal_init()

    def additionnal_init(self):
        pass

    def collide(self, x, y):
        return 0 <= x - self.x <= self.width and 0 <= y - self.y <= self.height

    def collide_mouse(self):
        return 0 <= self.game.mouse_x - self.x <= self.width and 0 <= self.game.mouse_y - self.y <= self.height

    def set_dim(self, new_height=None, new_width=None):
        self.width = new_width or self.width
        self.height = new_height or self.height
        self.window = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def window_view_down(self):
        if self.moveable and self.collide_mouse():
            self.view_y += 4
            self.check_down()
            return True
        return False

    def get_font(self, size=None):
        if size is None:
            return self.font
        else:
            return pygame.font.SysFont("Courier New", size)

    def window_view_up(self):
        if self.moveable and self.collide_mouse():
            self.view_y -= 4
            self.check_down()
            return True
        return False

    def check_down(self):
        if self.view_y.is_max():
            self.down = True
        else:
            self.down = False

    def print_window(self):
        self.window.fill(self.background_color)
        pygame.draw.rect(self.window, color.BLACK, [0, 0, self.width, self.height], 1)

        self.update_content()
        self.update_extremum_view()
        self.print_content()

        self.game.screen.blit(self.window, (self.x, self.y))
        self.clean()

    def clean(self):
        self.window.fill(self.background_color)

    def window_blit(self, content, x=0, y=0, loc=[], border_x=None, border_y=None):
        border_x = self.border_x if border_x is None else border_x
        border_y = self.border_y if border_y is None else border_y
        content_width, content_height = content.get_size()
        if "center" in loc:
            x, y = self.width / 2 - content_width / 2, self.height / 2 - content_height
        if "top" in loc:
            y = border_y
        if "bottom" in loc:
            y = self.height - content_height.height / 2 - border_y
        if "left" in loc:
            x = border_x
        if "right" in loc:
            x = self.width - content_width - border_x
        if "over" in loc:
            pygame.draw.rect(self.game.screen, self.background_color,
                             [self.x, self.y + content_height, content_width, content_height])
            self.game.screen.blit(content, (self.x, self.y + content_height))
            return None
        self.window.blit(content, (x, y))

    def update_extremum_view(self):
        self.view_x.set_max(0)
        self.view_y.set_max(max(0, max([(button.y + button.height / 2 + 1) for button in self.buttons] + [self.content_height]) - self.height))

    def format_text(self, text, font, x_space=5, y_space=5):
        text_surface = pygame.Surface((self.width, self.height))
        text_surface.fill((0, 0, 0))
        space = font.size(' ')[0]
        line = font.size('I')[1]
        min_x, min_y = x_space, y_space
        max_x, max_y = self.width - x_space, self.height - y_space
        x, y = min_x, min_y
        for paragraph in text.split('\n'):
            for paragraph2 in paragraph.split('\t'):
                for word in paragraph2.split(' '):
                    rendered_word = self.font.render(word, 0, self.writing_color)
                    word_width = rendered_word.get_width()
                    if x + word_width >= max_x:
                        x = min_x
                        y += line
                    text_surface.blit(rendered_word, (x - self.view_x, y - self.view_y))

                    x += word_width + space
                x += 4 * space
            y += line
            x = min_x
        return text_surface, y

    def update_content(self):
        pass

    def print_content(self):
        if self.content is not None:
            self.window_blit(self.content)
        for button in self.buttons:
            button.display()

    def move(self, rel_x, rel_y):
        if self.moveable and self.collide_mouse():
            self.go_front()
            self.x += rel_x
            self.y += rel_y
            return True
        return False

    def go_front(self):
        if self.selectable and self.game.windows[-1] != self:
            self.game.windows.remove(self)
            self.game.windows.append(self)

    def close(self):
        if self.closable:
            self.controller.disable()
            if self.game.windows[-1] == self:
                self.game.windows.pop()
            else:
                self.game.windows.remove(self)

    def new_button(self, button):
        self.buttons.add(button)
        self.controller.buttons.add(button)

    def erase_button(self, button):
        self.buttons.discard(button)
        self.controller.buttons.discard(button)

    def erase_buttons(self):
        for button in self.buttons:
            buttonClass.MultiButton.info[button.key] = None
            button.clicked = False
        self.buttons.clear()
        self.controller.buttons.clear()

    def select(self, x, y):
        if self.selectable and self.collide(x, y):
            self.go_front()
            self.controller.activize()
            return True
        return False

    def retire_windows(self, *args):
        if self in self.game.windows:
            self.game.windows.remove(self)
        else:
            self.game.add_debug(f"{type(self)} is already not in windows")
        self.controller.disable()
        self.add_retire_windows(*args)

    def add_retire_windows(self, *args):
        pass

    def add_windows(self, *args):
        self.controller.enable()
        self.add_add_windows(*args)

    def add_add_windows(self, *args):
        pass

    def set_window(self):
        for window in self.game.windows:
            window.retire_windows()
        self.game.new_window(self)

        
class DebugWindow(Window):

    def __init__(self, game, target=None):
        Window.__init__(self, game, game.config.window.debug, self.game.debug_window)
        self.target_lock = target is not None
        self.target = target
        self.parameters = "basics"

    def update_content(self):
        if not self.target_lock and self.game.selected is not None:
            self.target = self.game.selected
        if self.target is not None:
            self.content, self.content_height = self.format_text(self.get_brut_content(), self.font)
            self.update_extremum_view()

    def get_brut_content(self):
        if self.parameters == "all":
            parameters = self.target.__dict__
        elif self.parameters == "basics":
            parameters = self.target.config.basics_parameters
        elif type(self.parameters) == list:
            parameters = self.parameters

        return "\n".join(
            str(key) + (max(0, 10 - len(key)) * " ") + ":  " + self.game.make_str(getattr(self.target, key)) for key in
            parameters if hasattr(self.target, key))

    def get_basics_parameters(self):
        self.parameters = "basics"

    def get_all_parameters(self):
        self.parameters = "all"

    def lock_target(self):
        if self.target is not None:
            self.target_lock = not self.target_lock


class MainWindow(Window):

    def __init__(self, game):
        Window.__init__(self, game, game.config.window.main, game.main_controller)

        self.width = self.game.width
        self.height = self.game.height

    def add_add_windows(self, *args):
        self.game.new_window(self.game.map_window)

    def print_window(self):
        self.update_content()
        self.print_content()

        self.game.screen.blit(self.window, (self.x, self.y))
        self.window.fill(0)


    def update_content(self):
        ...


    # def money_display(self):
    #     money_content = pygame.font.Font(None, 50).render(str(self.game.money), True, color.WHITE)
    #     money_width, money_height = money_content.get_size()
    #     pygame.draw.rect(self.window, color.DARK_GREY_2, [self.width - money_width - 2 * self.border_x, 0, money_width + 2 * self.border_x, 2 * self.border_y + money_height])
    #     self.window_blit(money_content, loc=["top", "right"])


class MenuWindow(Window):

    def __init__(self, game):
        Window.__init__(self, game, game.config.window.menu, game.menu_controller)
        self.start_button = buttonClass.Button(self, "center", 3 * self.height / 4, "START", value=True,
                                   func_action=self.game.start_main)
        self.new_button(self.start_button)

    def add_add_windows(self):
        self.start_button.reset()


class MapWindow(Window):

    def __init__(self, game):
        Window.__init__(self, game, game.config.window.map, game.map_controller)

        self.window = pygame.Surface((self.width, self.height))
        self.alpha_window = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def update_content(self):

        self.game.road.display(self.window)

        for animation in self.game.animations:
            animation.anime(0)

        self.window.blit(self.alpha_window, (0, 0))

    def clean(self):
        super().clean()
        self.alpha_window.fill(0)




