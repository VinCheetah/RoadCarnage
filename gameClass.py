import random

import roadClass
import controllerClass
import animationClass
import configClass
import windowClass

import pygame
import os
import time
import color
from math import sqrt, sin, cos, tan, pi, log, exp

# Cartesian in game coords
coord = type(tuple[float, float, float])
# Projected on ground coords from camera
Gcoord = type(tuple[float, float])
# Screen coords
Scoord = type(tuple[int, int])

class Game:

    config = configClass.default_config
    libs = [color]

    def __init__(self):

        os.environ["SDL_VIDEO_CENTERED"] = "1"

        pygame.display.set_caption("Road Carnage")
        # pygame.display.set_icon(pygame.image.load("images/icon.png"))

        self.width = 0
        self.height = 0
        self.actu_dimensions()

        self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

        self.road: roadClass.Road = ...
        self.car = ...

        self.running = True
        self.playing = False
        self.pause = False
        self.test = False
        self.god_mode_active = False

        self.original_time_speed = 1
        self.time_speed = self.original_time_speed
        self.original_frame_rate = 60
        self.frame_rate = self.original_frame_rate

        self.distance_window = 80
        self.distance_window_obj = 80
        self.distance_window_speed = 0.5

        self.advancement_mode = 0

        self.time = 0
        self.money = 1000
        self.mouse_x = 0
        self.mouse_y = 0
        self.ex_mouse_x = 0
        self.ex_mouse_y = 0
        self.px_new_car = 0.001
        self.screen_ratio = self.width / self.height

        self.zoom = 0.06

        self.init_add_cam_x: float = ...
        self.init_add_cam_y: float = ...
        self.init_add_cam_z: float = ...

        self.x_add_cam: float = 0
        self.y_add_cam: float = 0
        self.z_add_cam: float = 0

        self.x_add_cam_obj: float = ...
        self.y_add_cam_obj: float = ...
        self.z_add_cam_obj: float = ...

        self.x_add_cam_speed: float = 0.05
        self.y_add_cam_speed: float = 0.5
        self.z_add_cam_speed: float = 0.5

        self.new_road()

        self.animations = set()
        self.new_animations = set()
        self.animations_bin = set()

        self.cars = set()
        self.cars_bin = set()

        self.advancement_modes = [
            lambda y: (log(max(0.01, 1 + self.zoom * y)) / log(1 + self.zoom * self.distance_window)),
            lambda y: (1 - exp(-y * self.zoom)) / (1 - exp(-self.distance_window * self.zoom)),
            lambda y: log(max(1, y)) / log(self.distance_window),
            lambda y: y / self.distance_window,
            lambda y: (y / self.distance_window) ** 3,
            ]

        self.windows = list()


        self.controllers = list()
        self.main_controller = controllerClass.MainController(self)
        self.map_controller = controllerClass.MapController(self)
        self.menu_controller = controllerClass.MenuController(self)

        self.menu_window = windowClass.MenuWindow(self)
        self.map_window = windowClass.MapWindow(self)
        self.main_window = windowClass.MainWindow(self)

        self.retrecissement = .6

        self.start_menu()

    def start(self):
        last_frame = 0

        while self.running:
            self.clean()
            self.actu_action(time.time() - last_frame)
            self.display()
            one_loop_done = False

            while not one_loop_done or time.time() - last_frame < 1 / self.frame_rate:
                one_loop_done = True
                self.interactions()

            pygame.display.flip()
            last_frame = time.time()

    def start_main(self):
        self.playing = True
        self.new_road()
        self.main_window.set_window()
        self.road.new_car()

    def new_road(self):
        self.road = roadClass.Road(self, {})
        self.distance_window_obj = self.distance_window
        self.init_add_cam_x = self.road.lines / 2
        self.init_add_cam_y = 0
        self.init_add_cam_z = 20
        self.restore_cam()

    def restore_cam(self):
        self.x_add_cam_obj = self.init_add_cam_x
        self.y_add_cam_obj = self.init_add_cam_y
        self.z_add_cam_obj = self.init_add_cam_z

    def start_menu(self):
        self.menu_window.set_window()

    def interactions(self):
        self.update_mouse_pos()
        for event in pygame.event.get():
            translated_event = self.main_controller.translate(event)
            arg = []
            if translated_event is None:
                continue
            if type(translated_event) is tuple:
                translated_event, arg = translated_event
            for controller in self.controllers:
                if controller.apply(translated_event, *arg):
                    if controller.controller_debug:
                        print(f"I have applied {translated_event} with {controller.name}")
                    break
                elif controller.controller_debug:
                    print(f"Couldn't apply {translated_event} with {controller.name}")
            else:
                if translated_event is not None and self.main_controller.controller_debug:
                    print(f"Couldn't match event {translated_event}")

    def display(self):
        for window in self.windows:
            window.print_window()

    def clean(self):
        for set_name in ["animations", "cars"]:
            bin_set = self.__getattribute__(set_name + "_bin")
            if len(bin_set) > 0:
                for item in bin_set:
                    self.__getattribute__(set_name).discard(item)
                    del item
                bin_set.clear()
        for set_name in ["animations"]:
            new_set = self.__getattribute__("new_" + set_name)
            if len(new_set) > 0:
                for item in new_set:
                    self.__getattribute__(set_name).add(item)
                new_set.clear()

    def actu_action(self, dt):
        delta = dt * 1000
        for param in ["distance_window", "x_add_cam", "y_add_cam", "z_add_cam"]:
            actual = self.__getattribute__(param)
            speed = self.__getattribute__(param + "_speed")
            objective = self.__getattribute__(param + "_obj")
            if objective > actual + 2 * speed:
                self.__setattr__(param, actual + speed)
            elif objective < actual - 2 * speed:
                self.__setattr__(param, actual - speed)
            else:
                self.__setattr__(param, objective)

        if self.playing and not self.pause:
            self.time += delta
            self.road.distance += self.road.speed * delta
            for car in self.cars:
                car.move(delta)
            if random.random() < self.px_new_car:
                self.road.new_car()
                self.px_new_car /= 10
            else:
                self.px_new_car += 0.0001
            self.road.check_crash_line()

    def transaction(self, value):
        if self.money >= value:
            self.money -= value
            return True
        else:
            self.print_text(f"Price is {value} and you have {self.money} ...")
        return False

    def god_mode(self):
        self.god_mode_active = not self.god_mode_active
        if self.god_mode_active:
            self.print_text("God Mode Activated")
        else:
            self.print_text("God Mode Deactivated")

    def pausing(self, forced=False):
        if self.god_mode_active or forced:
            self.pause = not self.pause
        else:
            self.print_text("God Mode Required")

    def stop_running(self):
        self.running = False

    def screen_resize(self):
        self.actu_dimensions()
        self.display()
        pygame.display.flip()

    def actu_dimensions(self):
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h

    def add_controllers(self, new_controller):
        self.controllers.append(new_controller)

    def new_window(self, new_window, *args):
        self.windows.append(new_window)
        new_window.add_windows(*args)

    def update_mouse_pos(self):
        self.ex_mouse_x = self.mouse_x
        self.ex_mouse_y = self.mouse_y
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

    def print_text(self, text):
        self.animations.add(animationClass.ShowText(self, text))

    def project_ground(self, p: coord) -> Gcoord:
        x, y, z = p
        xc, yc, zc = self.road.pos_cam
        if z == zc:
            c = 1000
        else:
            c = z / (zc - z)
        return x - xc + (x - xc) * c, y - yc + (y - yc) * c

    def increase_road(self):
        self.distance_window_obj += 5

    def decrease_road(self):
        self.distance_window_obj -= 5
        self.distance_window_obj = max(5, self.distance_window_obj)

    def show_zoom(self):
        self.print_text(f"Zoom : {self.zoom}")

    def incr_zoom(self):
        self.zoom *= 1.1

    def decr_zoom(self):
        self.zoom *= 0.9
        self.zoom = max(0.0001, self.zoom)

    def add_x_view(self):
        self.x_add_cam_obj += 1

    def red_x_view(self):
        self.x_add_cam_obj -= 1

    def add_y_view(self):
        self.y_add_cam_obj += 10

    def red_y_view(self):
        self.y_add_cam_obj -= 10

    def add_z_view(self):
        self.z_add_cam_obj += 5

    def red_z_view(self):
        self.z_add_cam_obj -= 5
        self.z_add_cam_obj = max(5., self.z_add_cam_obj)

    def change_advancement_mode(self):
        self.advancement_mode += 1
        self.print_text(f"Advancement Mode: {self.advancement_mode % len(self.advancement_modes)}")

    def to_screen(self, p: Gcoord) -> Scoord:
        x, y = p
        advancement = self.advancement_modes[self.advancement_mode % len(self.advancement_modes)](y)
        # advancement = (1 - exp(-y * self.zoom)) / (1 - exp(-self.distance_window * self.zoom))
        # advancement = log(max(1, distance)) / log(self.distance_window)
        # advancement = 1 - (self.distance_window / max(1, distance))
        return int((self.width / 2 + self.road.line_size * x * (1 - self.retrecissement * advancement) / (self.road.z_cam * .05))), int(self.height - advancement * self.height)

    def view(self, p: coord) -> Scoord:
        return self.to_screen(self.project_ground(p))

    def view_old(self, p: Gcoord) -> Scoord:
        x, y = p
        return int(self.width / 2 + self.road.line_size * (-self.road.lines / 2 + x)), int((self.road.distance - y) / self.distance_window * self.height)

    def unview_old(self, p: Scoord) -> Gcoord:
        x, y = p
        return (x - self.width / 2) / self.road.line_size + self.road.lines / 2, self.road.distance - (y / self.height * self.distance_window)

    def view_group(self, group):
        return [self.view(*p) for p in group]
