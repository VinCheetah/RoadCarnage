import pygame

import buttonClass


class Controller:

    name = "Default Controller"
    controller_debug = False

    def __init__(self, game):
        self.game = game
        self.active: bool = False
        self.window = None
        self.game.add_controllers(self)
        self.buttons: set[buttonClass.Button] = set()
        self.active_commands, self.commands, self.inactive_commands = self.create_commands()

        self.add_init()

    def add_init(self) -> None:
        pass

    def apply(self, command, *arg):
        if self.active and command in self.active_commands:
            return self.active_commands.get(command)(*arg) or str(command)[0] != "_"
        elif command in self.commands:
            return self.commands.get(command)(*arg) or str(command)[0] != "_"
        elif not self.active and command in self.inactive_commands:
            return self.inactive_commands.get(command)(*arg) or str(command)[0] != "_"
        else:
            if command in self.inactive_commands and self.controller_debug:
                print(f"WARNING: The command ({command}) is in inactive_commands of {self.name}")
            return False

    @classmethod
    def translate(cls, event):
        if event.type == pygame.QUIT:
            return "QUIT"
        elif event.type == pygame.VIDEORESIZE:
            return "RESIZE"
        elif event.type == pygame.MOUSEMOTION:
            return "_MOUSE_MOTION", event.rel
        elif event.type == pygame.KEYDOWN:
            return cls.key_down_translate(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return cls.mouse_button_up_translate(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return cls.mouse_button_down_translate(event)

    @staticmethod
    def key_down_translate(event):
        if 97 <= event.key <= 122:
            return event.unicode
        else:
            return event.key

    @staticmethod
    def mouse_button_up_translate(event):
        return {1: "_l_click", 2: "_m_click", 3: "_r_click", 4: "_d_up_click", 5: "_d_down_click"}.get(event.button), event.pos

    @staticmethod
    def mouse_button_down_translate(event):
        return {1: "_l_down", 2: "_m_down", 3: "_r_down", 4: "_d_up_down", 5: "_d_down_down"}.get(event.button), event.pos

    def create_commands(self):
        return {}, {}, {}

    def enable(self, *args):
        self.active = True
        self.add_enable(*args)

    def add_enable(self, *args):
        pass

    def disable(self):
        self.active = False
        self.add_disable()

    def add_disable(self):
        pass

    def check_buttons(self, *args):
        for button in self.buttons.copy():
            if button.is_clicked(*args):
                return True
        return False


class MainController(Controller):

    name = "Main Controller"
    controller_debug = False

    def create_commands(self):
        return ({
                    pygame.K_ESCAPE: self.game.stop_running,
                    pygame.K_DOLLAR: self.money_bonus,

                    "g": self.game.god_mode,
                    "t": self.game.pausing,

                },
                {
                    "QUIT": self.game.stop_running,
                    "RESIZE": self.game.screen_resize,
                    "q": self.show_controllers,
                    "w": self.show_windows,
                },
                {})

    def print_infos(self):
        print(self.game.game_stats())

    def money_bonus(self):
        self.game.money_prize(10000)

    def increase_time_speed(self):
        self.game.change_time_speed(1.5)

    def reduce_time_speed(self):
        self.game.change_time_speed(2 / 3)


    def show_controllers(self):
        # self.game.add_debug("\n".join(controller.name for controller in self.game.controllers if controller.active))
        print("\n".join(controller.name for controller in self.game.controllers if controller.active))


    def show_windows(self):
        # self.game.add_debug("\n".join(controller.name for controller in self.game.controllers if controller.active))
        print("\n".join(window.name for window in self.game.windows))


class MapController(Controller):

    name = "Map Controller"
    controller_debug = False

    def create_commands(self):
        return (
            {
                "_l_click": self.left_click,
                "_r_click": self.right_click,

                "c": self.new_car,
                "i": self.game.show_zoom,

                "p": self.game.increase_road,
                "m": self.game.decrease_road,

                "o": self.game.incr_zoom,
                "l": self.game.decr_zoom,

                "e": self.game.add_y_view,
                "d": self.game.red_y_view,
                "f": self.game.add_x_view,
                "s": self.game.red_x_view,
                "r": self.game.add_z_view,
                "z": self.game.red_z_view,

                "h": self.game.restore_cam,
                "a": self.game.change_advancement_mode,


            },
            {},
            {}
        )

    def left_click(self, *args):
        if self.check_buttons(*args):
            return True

    def right_click(self, *args):
        if self.check_buttons(*args):
            return True

    def new_car(self):
        self.game.road.new_car()


class MenuController(Controller):
    name = "Menu Controller"

    def create_commands(self):
        return (
            {
                "_l_click": self.left_click,


                pygame.K_RETURN: self.enter,
                pygame.K_ESCAPE: self.game.stop_running,
            },
            {},
            {
            }
        )


    def enter(self):
        return self.game.menu_window.start_button.action()

    def left_click(self, *args):
        return self.check_buttons(*args)


class WindowController(Controller):

    name = "Window Controller"
    controller_debug = False

    def __init__(self, game):
        super().__init__(game)
        self.disable()

    def create_commands(self):

        return (
            {
                "_d_up_click": self.game.window_view_up,
                "_d_down_click": self.game.window_view_down,

                pygame.K_DOWN: self.game.window_view_down,
                pygame.K_UP: self.game.window_view_up,

                pygame.K_BACKSPACE: self.game.delete_selected_window,
            },
            {
                "_MOUSE_MOTION": self.game.move_window,
                "_l_click": self.game.find_window,
            },
            {}
        )


class DebugWindowController(WindowController):

    name = "Debug Window Controller"

    def create_commands(self):
        active, general, inactive = super().create_commands()
        return (active | {
            "l": self.game.lock_target,
            "b": self.game.get_basics_parameters,
            "a": self.game.get_all_parameters
        },
            general | {},
            inactive | {}
        )





class SelectionController(Controller):

    name = "Selection Controller"

    def __init__(self, game):
        super().__init__(game)
        self.disable()


    def create_commands(self):
        return (
            {
                pygame.K_BACKSPACE: self.game.delete_selected,

                "d": self.create_debug_window,
                "i": self.print_infos
            },
            {
                "_l_click": self.find_selected
            },
            {}
        )

    def create_debug_window(self):
        self.game.new_debug_window()
        self.game.lock_target()

    def find_selected(self, x, y):
        x, y = self.game.unview((x, y))
        if not self.game.moving_map:
            for tower in self.game.attack_towers.union(self.game.effect_towers):
                if tower.dist_point(x, y) < tower.size:
                    self.game.select(tower)
                    self.game.view_move(tower.x, tower.y, self.game.zoom if not self.game.zoom_change else self.game.height / (3 * tower.range), 1.5)
                    self.enable()
                    self.game.tower_controller.enable()
                    return True
            else:
                for zombie in self.game.zombies:
                    if zombie.dist_point(x, y) < zombie.size:
                        self.game.select(zombie)
                        self.game.view_move(zombie.x, zombie.y, speed=3, tracking=True)
                        return True
                else:
                    for wall in self.game.walls:
                        if wall.dist_point(x, y) < 20:
                            self.game.select(wall)
                            self.game.view_move(*wall.mid())
                            return True
                return False
            return False
        return False


    def print_infos(self):
        assert self.game.selected is not None
        print(self.game.selected.info())


class ZombieController(Controller):

    name = "Zombie Controller"
    def create_commands(self):
        return (
            {},
            {},
            {}
        )

class TowerController(Controller):

    name = "Tower Controller"

    def __init__(self, game):
        super().__init__(game)
        self.disable()

    def create_commands(self):
        return (
            {
                "u": self.game.upgrade_selected,
                "i": self.game.forced_upgrade,
                # "_l_click": self.game.find_canon
            },
            {},
            {}
        )

class WallController(Controller):

    name = "Wall Controller"
    controller_debug = False

    def __init__(self, game):
        super().__init__(game)
        self.disable()

    def create_commands(self):
        return (
            {
                "e": self.show_extremity,
                "c": self.show_chain,
            },
            {},
            {}
        )

    def show_extremity(self):
        [self.game.show.add(self.game.view(extremity)) for extremity in self.game.selected.extremity]

    def show_chain(self):
        [self.game.show.add(self.game.view(wall.p1), self.game.view(wall.p2)) for wall in self.game.selected.chain()]


class ShopController(WindowController):

    def enable(self):
        super().enable()
        self.game.pausing(True)

    def disable(self):
        super().disable()
        self.game.pausing(True)



class BuildController(Controller):

    name = "Build Controller"

    def __init__(self, game):
        super().__init__(game)
        self.disable()

    def create_commands(self):
        return (
            {
                #pygame.K_KP_ENTER: ,
            },
            {},
            {}
        )

class WallBuildController(BuildController):

    name = "Wall Build Controller"

    def __init__(self, game):
        super().__init__(game)
        self.disable()

    def link_window(self):
        self.window = self.game.build_window


    def create_commands(self):
        return (
            {
                "_l_click": self.left_click,
                "_MOUSE_MOTION": self.check_merge,
                pygame.K_ESCAPE: self.stop_build
            },
            {},
            {}
        )

    def check_merge(self, *args):
        return self.window.check_merge(*args)

    def stop_build(self):
        return self.window.stop_wall_build()

    def left_click(self, x, y):
        return self.game.build_window.wall_build(x, y)