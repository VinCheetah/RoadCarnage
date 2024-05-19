import carClass
import pygame

import random as rd
import color
from math import atan


class Road:

    def __init__(self, game, config):
        self.game = game
        self.config = config | self.game.config.road.basics
        self.lines = self.config.lines
        self.cars: set[carClass.Car] = set()
        self.cars_line = {i: [] for i in range(self.lines)}
        self.color = self.config.color
        self.line_size = 200
        self.distance = 0
        self.basic_speed = self.config.speed
        self.speed = self.basic_speed

        self.horizon_point = 2
        self.top_road_size = 0.6
        self.bottom_road_size = 0.9

        self.alpha = atan((2 * self.game.height) / (self.game.width * self.bottom_road_size / 2))

        self.left_top_road = ...

    @property
    def x_cam(self):
        return 0 + self.game.x_add_cam

    @property
    def y_cam(self):
        return self.distance + self.game.y_add_cam

    @property
    def z_cam(self):
        return self.game.z_add_cam

    @property
    def alpha_cam(self):
        return self.game.alpha_add_cam

    @property
    def theta_cam(self):
        return self.game.theta_add_cam

    @property
    def pos_cam(self):
        return self.x_cam, self.y_cam, self.z_cam

    def get_alpha(self, x, y):
        x, y = self.game.unview(x, y)
        return atan((x + self.game.height) / (y / 2))

    def insert_car_line(self, car, line):
        self.game.cars.add(car)
        i = 0
        while i < len(self.cars_line[line]) and self.cars_line[line][i].x > car.x:
            i += 1
        self.cars_line[line].insert(i, car)

    def adjacent_lines(self, line):
        return [line + i for i in (-1, 0, 1) if 0 <= line + i < self.lines]

    def adjacent_cars(self, cline):
        return [car for line in self.adjacent_lines(cline) for car in self.cars_line[line] ]

    def check_crash_line(self):
        for line in self.cars_line.values():
            for i in range(len(line)-1):
                if line[i].y_bottom < line[i+1].y_top:
                    line[i].crash()
                    line[i+1].crash()

    def get_coord(self, line):
        return line + 0.5

    def new_car(self):
        rd.choice([carClass.ClassicCar, carClass.Truck, carClass.Motorbike, carClass.BigTruck])(self.game)

    def display(self, window):
        pygame.draw.polygon(window, self.color, [self.game.view((0, self.distance, 0)),
                                                        self.game.view((self.lines, self.distance, 0)),
                                                        self.game.view((self.lines, self.distance + self.game.distance_window, 0)),
                                                        self.game.view((0, self.distance + self.game.distance_window, 0)),
        ])
        for i in range(self.lines + 1):
            size = 10
            n = self.game.distance_window / size
            for j in range(int(n)+1):
                pygame.draw.line(window, color.WHITE, self.game.view((i, self.distance + self.game.distance_window * max(0, min(1, (j + .5 - (self.distance / size) % 1) / n)), 0)),
                                 self.game.view((i, self.distance + self.game.distance_window * max(0, min(1, (j - (self.distance / size) % 1) / n)), 0)))

        cars = []
        cam_line = max(0, min(self.lines-1, int(self.x_cam)))
        for i in range(cam_line):
            cars += self.cars_line[i]
        for i in range(self.lines-1, cam_line, -1):
            cars += self.cars_line[i]
        cars += self.cars_line[cam_line]

        for car in cars:
            car.display(window)


class EmptyRoad(Road):

    def __init__(self):
        pass
