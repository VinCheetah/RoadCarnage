import random as rd

import pygame

import color


class Car:

    def __init__(self, game, config):
        self.game = game
        self.road = self.game.road
        self.config = self.game.config.car.basics | config
        self.color = self.config.color
        self.speed: float = (1 + rd.choice([-1]) * self.config.speed_variation) * self.road.basic_speed
        self.width: int = self.config.width
        self.length: int = self.config.length
        self.horizontal_speed: float = self.config.horizontal_speed
        self.x: float = ...
        self.y: float = ...
        self.h: float = self.config.h
        self.line: int = ...

        self.find_spawn()

    def delete(self):
        self.game.cars_bin.add(self)
        self.road.cars_line[self.line].remove(self)


    def find_spawn(self):
        random_line = [i for i in range(self.game.road.lines)]
        rd.shuffle(random_line)

        self.y = self.game.road.distance + self.game.distance_window + self.length / 2
        for line in random_line:
            self.x = self.road.get_coord(line)
            self.line = line
            if self.check_contact():
                continue
            self.road.insert_car_line(self, line)
            break
        else:
            print("Car couldn't be added")

    def crash(self):
        self.speed = 0

    def _contact(self, car: 'Car'):
        return (max(self.x_left, car.x_left) < min(self.x_right, car.x_right) and
                max(self.y_bottom, car.y_bottom) < min(self.y_top, car.y_top))

    def contact(self, car: 'Car'):
        x_overlap = (self.x_left < car.x_right) and (self.x_right > car.x_left)
        y_overlap = (self.y_bottom < car.y_top) and (self.y_top > car.y_bottom)
        return x_overlap and y_overlap

    def check_contact(self):
        for car in self.road.adjacent_cars(self.line):
            if self.contact(car):
                return True
        return False

    def display2(self, window):
        pygame.draw.rect(window, self.color, [*self.game.view((self.x_left, self.y_top, 0)), self.width * self.road.line_size, self.length * self.game.height / self.game.distance_window])
        pygame.draw.rect(window, color.BLACK, [*self.game.view((self.x_left, self.y_top, 0)), self.width * self.road.line_size, self.length * self.game.height / self.game.distance_window], 3)

    def display(self, window):
        pygame.draw.polygon(window, self.color, [self.game.view((self.x_left, self.y_top, 0)),
                                                 self.game.view((self.x_right, self.y_top, 0)),
                                                 self.game.view((self.x_right, self.y_bottom, 0)),
                                                 self.game.view((self.x_left, self.y_bottom, 0))])
        pygame.draw.polygon(window, color.BLACK, [self.game.view((self.x_left, self.y_top, 0)),
                                                 self.game.view((self.x_right, self.y_top, 0)),
                                                 self.game.view((self.x_right, self.y_bottom, 0)),
                                                 self.game.view((self.x_left, self.y_bottom, 0))],)

        if self.x < self.road.x_cam:

            pygame.draw.polygon(window, color.lighter_compensative(self.color, 30), [self.game.view((self.x_right, self.y_top, 0)),
                                                     self.game.view((self.x_right, self.y_top, self.h)),
                                                     self.game.view((self.x_right, self.y_bottom, self.h)),
                                                     self.game.view((self.x_right, self.y_bottom, 0))])

            pygame.draw.polygon(window, color.BLACK, [self.game.view((self.x_right, self.y_top, 0)),
                                                     self.game.view((self.x_right, self.y_top, self.h)),
                                                     self.game.view((self.x_right, self.y_bottom, self.h)),
                                                     self.game.view((self.x_right, self.y_bottom, 0))], 1)

        elif self.x > self.road.x_cam:
            pygame.draw.polygon(window, color.lighter_compensative(self.color, 30), [self.game.view((self.x_left, self.y_top, 0)),
                                                     self.game.view((self.x_left, self.y_top, self.h)),
                                                     self.game.view((self.x_left, self.y_bottom, self.h)),
                                                     self.game.view((self.x_left, self.y_bottom, 0))])

            pygame.draw.polygon(window, color.BLACK, [self.game.view((self.x_left, self.y_top, 0)),
                                                     self.game.view((self.x_left, self.y_top, self.h)),
                                                     self.game.view((self.x_left, self.y_bottom, self.h)),
                                                     self.game.view((self.x_left, self.y_bottom, 0))], 1)

        pygame.draw.polygon(window, self.color, [self.game.view((self.x_left, self.y_top, self.h)),
                                                 self.game.view((self.x_right, self.y_top, self.h)),
                                                 self.game.view((self.x_right, self.y_bottom, self.h)),
                                                 self.game.view((self.x_left, self.y_bottom, self.h))])
        pygame.draw.polygon(window, color.BLACK, [self.game.view((self.x_left, self.y_top, self.h)),
                                                 self.game.view((self.x_right, self.y_top, self.h)),
                                                 self.game.view((self.x_right, self.y_bottom, self.h)),
                                                 self.game.view((self.x_left, self.y_bottom, self.h))], 1)

        pygame.draw.polygon(window, color.darker_compensative(self.color, 30), [self.game.view((self.x_left, self.y_bottom, self.h)),
                                                 self.game.view((self.x_right, self.y_bottom, self.h)),
                                                 self.game.view((self.x_right, self.y_bottom, 0)),
                                                 self.game.view((self.x_left, self.y_bottom, 0))])
        pygame.draw.polygon(window, color.BLACK, [self.game.view((self.x_left, self.y_bottom, self.h)),
                                                  self.game.view((self.x_right, self.y_bottom, self.h)),
                                                  self.game.view((self.x_right, self.y_bottom, 0)),
                                                  self.game.view((self.x_left, self.y_bottom, 0))], 1)



    def move(self, delta):
        self.y += self.speed * delta

        if self.y + self.length < self.road.distance and self.speed < self.road.speed:
            self.delete()


    @property
    def x_left(self):
        return self.x - self.width / 2

    @property
    def x_right(self):
        return self.x + self.width / 2

    @property
    def y_top(self):
        return self.y + self.length / 2

    @property
    def y_bottom(self):
        return self.y - self.length / 2


class ClassicCar(Car):

    def __init__(self, game):
        Car.__init__(self, game, game.config.car.classic)


class Truck(Car):

    def __init__(self, game):
        Car.__init__(self, game, game.config.car.truck)


class Motorbike(Car):

    def __init__(self, game):
        Car.__init__(self, game, game.config.car.motorbike)


class BigTruck(Car):

    def __init__(self, game):
        Car.__init__(self, game, game.config.car.big_truck)

