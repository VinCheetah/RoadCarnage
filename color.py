import random

Tcolor = type(tuple[int, int, int])

BLACK: Tcolor = 0, 0, 0
RED: Tcolor = 255, 0, 0
BLUE: Tcolor = 0, 0, 255
WHITE: Tcolor = 255, 255, 255
GREEN: Tcolor = 0, 255, 0
GOLD: Tcolor = 200, 150, 30
GOLD2: Tcolor = 212, 175, 55
GREY: Tcolor = 125, 125, 125
VIOLET: Tcolor = 210, 130, 210
LIGHT_BLUE: Tcolor = 140, 160, 255
LIGHT_GREEN: Tcolor = 140, 240, 160
LIGHT_RED: Tcolor = 150, 50, 50
LIGHT_GREY: Tcolor = 200, 200, 200
DARK_GREY: Tcolor = 50, 50, 50
DARK_GREY_1: Tcolor = 90, 90, 90
DARK_GREY_2: Tcolor = 70, 70, 70
DARK_GREY_3: Tcolor = 30, 30, 30
DARK_BLUE: Tcolor = 50, 50, 100
DARK_GREEN: Tcolor = 100, 150, 100
DARK_RED: Tcolor = 120, 50, 50
YELLOW: Tcolor = 190, 240, 0
BROWN: Tcolor = 200, 140, 150

CREA1: Tcolor = 70, 160, 100
CREA2: Tcolor = 100, 80, 150
CREA3: Tcolor = 200, 70, 140
CREA4: Tcolor = 107, 230, 170


def mix(c1: Tcolor, c2: Tcolor) -> Tcolor:
    return (c1[0] + c2[0]) / 2, (c1[1] + c2[1]) / 2, (c1[2] + c2[2]) / 2


def darker(c: Tcolor, darkness=30) -> Tcolor:
    return max(0, c[0] - darkness), max(0, c[1] - darkness), max(0, c[2] - darkness)


def rand_color(r_inf: int = 0, r_sup: int = 255, g_inf: int = 0, g_sup: int = 255, b_inf: int = 0, b_sup: int = 255) -> Tcolor:
    return random.randint(r_inf, r_sup), random.randint(g_inf, g_sup), random.randint(b_inf, b_sup)


def lighter(c: Tcolor, lightness=30) -> Tcolor:
    print(c)
    return min(255, c[0] + lightness), min(255, c[1] + lightness), min(255, c[2] + lightness)


def lighter_absolute(c: Tcolor, lightness=1.3) -> Tcolor:
    return min(255, c[0] * lightness), min(255, c[1] * lightness), min(255, c[2] * lightness)


def darker_absolute(c, darkness=1.3):
    return max(0, c[0] / darkness), max(0, c[1] / darkness), max(0, c[2] / darkness)


def lighter_compensative(c, lightness=30):
    comp = max(255, c[0] + lightness) + max(255, c[1] + lightness) + max(255, c[2] + lightness) - 765
    return min(255, c[0] + lightness + comp), min(255, c[1] + lightness + comp), min(255, c[2] + lightness + comp)


def darker_compensative(c, darkness=30):
    comp = - min(0, c[0] - darkness) - min(0, c[1] - darkness) - min(0, c[2] - darkness)
    return max(0, c[0] - darkness - comp), max(0, c[1] - darkness - comp), max(0, c[2] - darkness - comp)


def make_alpha(color: Tcolor, alpha: int):
    """
    Converts a color to an alpha color

    :param color: the color to convert
    :param alpha: the alpha value

    :return: the alpha color
    """
    return color + tuple([alpha])