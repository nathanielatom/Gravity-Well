"""

Gravity-Well
============

Author: Adam Suban-Loewen

A classic 2-D gravity orbiting game. Launch your ship from Earth and explore into space!

Designed in summer 2012, for the University of Toronto computer science portion of a science summer camp, for
prospective high school students. Currently the game has 9 levels, with 24 astronomy info-bits. Levels can easily be
created by editing levels.py according to the comments, and providing appropriate PNG files. The main game code is
in engine.py, and constant game parameters can be changed in settings.py.

To play: run levels.py with python in a terminal window; type: "python levels.py" after ensuring the correct directory.



This file can be used to edit or create new levels. To see how the levels run, see engine.py. To change the game's
constant parameters see settings.py.

Levels are created simply by creating their celestial bodies! Then setting the target body, and the hero body
(recommended hero for all levels is "rocket"). It is also recommended that all levels include the earth as a body.

To create a level, simply make a function named lvl_(number), where (number) is a new integer for the new level.
Then use game.create_body() with the parameters given below, and set game.target and game.hero. If this new level is
to come after all current levels, increase the total_lvls parameter in settings.py.

game.create_body() parameters: name of body (must have a PNG file with the same name in the data folder), size, and
position (both on a scale from 1 to 500), optional: density, tuple of scores when info-bits about the body appear
(must have a PNG file named "fact_lvl_(level number)_(body)_(fact number)" in the data folder; the body's score
accumulates based on the launchable hero's position within the body's gravitational field), whether the body undergoes
gravitational acceleration or is stationary, tuple of other bodies which do not affect its gravitation,
initial velocity (-y means up).
"""
import pygame
from pygame.locals import *
import engine
import settings


def show_instructions():
    """ Shows game instructions when first launched.
    """
    game.draw_background()
    intro = pygame.transform.smoothscale(engine.load_image("introduction.png"), game.screen.get_size())
    game.screen.blit(intro, intro.get_rect(center = game.screen.get_rect().center))
    pygame.display.update()
    game.dimmer.dim()
    engine.click_to_continue()


def lvl_0():
    """ Simple level with the moon orbiting the earth.
    """
    game.create_body("earth", 72, (210, 210))
    game.create_body("moon", 22, (260, 40), 1.0, (50, 400), True, ("rocket"), (4.8, 3.0))
    game.create_body("rocket", 35, (0, 0), 0.01, (), True, (), (0.0, -18.0))
    game.target = "moon"
    game.hero = "rocket"


def lvl_1():
    """ Level with earth, mars and their moons.
    """
    game.create_body("earth", 62, (95, 315))
    game.create_body("moon", 18, (43, 322), 0.8, (), True, ("rocket", "mars", "phobos"), (1.7, -7.8))
    game.create_body("mars", 55, (385, 95), 1.0, (200, 550))
    game.create_body("phobos", 15, (345, 105), 0.6, (350), True, ("rocket", "earth", "moon", "deimos"), (1.8, -7.5))
    game.create_body("deimos", 10, (435, 165), 0.4, (), True, ("rocket", "earth", "moon", "phobos"), (-3.4, 8.5))
    game.create_body("rocket", 35, (0, 0), 0.01, (), True, (), (16.0, 0.0))
    game.target = "mars"
    game.hero = "rocket"


def lvl_2():
    """ Level with the inner solar system.
    """
    game.create_body("sun", 80, (165, 205), 3.5, (280))
    game.create_body("mercury", 25, (132, 152), 0.8, (), True, ("rocket", "venus", "earth"), (10.8, -10.8))
    game.create_body("venus", 40, (254, 420), 0.9, (220), True, ("rocket", "mercury", "earth"), (-9.8, 4.3))
    game.create_body("earth", 45, (408, 275), 1.0, (), True, ("rocket", "mercury", "venus"), (-1.2, 9.4))
    game.create_body("rocket", 35, (0, 0), 0.01, (), True, (), (0.0, -15.0))
    game.target = "venus"
    game.hero = "rocket"


def lvl_3():
    """ Level with jupiter and ceres.
    """
    game.create_body("earth", 30, (110, 85), 1.5)
    game.create_body("mars", 28, (90, 170), 1.5)
    game.create_body("jupiter", 80, (365, 320), 1.0, (250))
    game.create_body("ceres", 16, (360, 255), 1.0, (200))
    game.create_body("rocket", 30, (0, 0), 0.01, (), True, (), (0.0, 14.0))
    game.target = "ceres"
    game.hero = "rocket"


def lvl_4():
    """ Level with the asteroid belt - every asteroid is a different body!
    """
    game.create_body("sun", 80, (-1000, 1000), 3.5)
    game.create_body("earth", 35, (98, 442), 0.8, (), True, ("rocket", "jupiter", "asteroid_0", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (-0.6, -1.6))
    game.create_body("jupiter", 60, (435, 255), 1.8, (280), True, ("rocket", "earth", "asteroid_0", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (-0.4, -1.7))
    game.create_body("asteroid_9", 15, (34, 105), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_0",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (-1.0, -0.8))
    game.create_body("asteroid_3", 15, (74, 115), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_0", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (-0.8, -0.8))
    game.create_body("asteroid_5", 15, (124, 145), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_0", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (-0.7, -1.0))
    game.create_body("asteroid_13", 15, (169, 185), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_0"), (-0.6, -1.4))
    game.create_body("asteroid_11", 15, (174, 245), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_0", "asteroid_12", "asteroid_13"), (-0.5, -1.8))
    game.create_body("asteroid_0", 15, (214, 295), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (-0.4, -2.0))
    game.create_body("asteroid_1", 15, (234, 365), 0.5, (75), True, ("rocket", "earth", "jupiter", "asteroid_0",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (-0.4, -2.2))
    game.create_body("asteroid_12", 15, (239, 425), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_0", "asteroid_13"), (-0.2, -2.4))
    game.create_body("asteroid_8", 15, (269, 515), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_0", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (0.0, -2.5))
    game.create_body("asteroid_2", 15, (284, 585), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_0", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (0.2, -2.6))
    game.create_body("asteroid_10", 15, (314, 735), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_0", "asteroid_11", "asteroid_12", "asteroid_13"), (0.4, -2.7))
    game.create_body("asteroid_6", 15, (354, 875), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_0", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (0.4, -2.8))
    game.create_body("asteroid_4", 15, (384, 985), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_0", "asteroid_5", "asteroid_6", "asteroid_7", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (0.4, -3.2))
    game.create_body("asteroid_7", 15, (404, 1095), 0.5, (), True, ("rocket", "earth", "jupiter", "asteroid_1",
        "asteroid_2", "asteroid_3", "asteroid_4", "asteroid_5", "asteroid_6", "asteroid_0", "asteroid_8", "asteroid_9",
        "asteroid_10", "asteroid_11", "asteroid_12", "asteroid_13"), (0.4, -3.4))
    game.create_body("rocket", 35, (0, 0), 0.01, (), True, ("sun"), (8.84, -8.84))
    game.target = "jupiter"
    game.hero = "rocket"


def lvl_5():
    """ Level with jupiter, saturn and some of their largest moons.
    """
    game.create_body("earth", 50, (65, 60))
    game.create_body("jupiter", 90, (200, 300), 1.8, (300))
    game.create_body("saturn", (100, 60), (380, 155), 1.0, (200, 320))
    game.create_body("europa", 21, (120, 375), 1.2, (), True, ("earth", "rocket", "saturn", "titan", "ganymede", "io", "callisto"), (4.5, 9.5))
    game.create_body("ganymede", 25, (255, 445), 1.2, (250), True, ("earth", "rocket", "saturn", "titan", "europa", "io", "callisto"), (12.8, -3.8))
    game.create_body("io", 22, (335, 325), 1.2, (), True, ("earth", "rocket", "saturn", "titan", "ganymede", "europa", "callisto"), (-2.0, -11.5))
    game.create_body("callisto", 23, (155, 255), 1.2, (), True, ("earth", "rocket", "saturn", "titan", "ganymede", "europa", "io"), (-8.5, 10.5))
    game.create_body("titan", 20, (320, 90), 1.2, (150), True, ("earth", "rocket", "jupiter", "callisto", "ganymede", "europa", "io"), (-3.5, 10.5))
    game.create_body("rocket", 35, (0, 0), 0.01, (), True, (), (9.9, 9.9))
    game.target = "saturn"
    game.hero = "rocket"


def lvl_6():
    """ Level among the gas giants.
    """
    game.create_body("sun", 70, (375, 220), 3.5)
    game.create_body("earth", 30, (305, 205), 1.0, (), True, ("rocket", "jupiter", "saturn", "uranus"), (-3.2, 12.4))
    game.create_body("jupiter", 45, (260, 70), 1.2, (), True, ("rocket", "earth", "saturn", "uranus"), (-5.8, 7.8))
    game.create_body("saturn", (60, 35), (150, 195), 2.0, (150, 350), True, ("rocket", "earth", "jupiter", "uranus"), (-3.5, 10.4))
    game.create_body("uranus", 38, (70, 25), 1.0, (350), True, ("rocket", "jupiter", "saturn", "earth"), (-3.2, 6.0))
    game.create_body("rocket", 30, (0, 0), 0.01, (), True, (), (-11.3, -11.3))
    game.target = "uranus"
    game.hero = "rocket"


def lvl_7():
    """ Level among more gas giants.
    """
    game.create_body("earth", 30, (410, 430))
    game.create_body("jupiter", 90, (300, 235))
    game.create_body("saturn", (100, 60), (105, 275), 1.0, (280, 500))
    game.create_body("uranus", 38, (180, 120))
    game.create_body("neptune", 40, (40, 65), 1.0, (380))
    game.create_body("triton", 15, (55, 140), 1.0, (320), True, ("earth", "jupiter", "saturn", "uranus"), (5.5, 0.2))
    game.create_body("rocket", 30, (0, 0), 0.01, (), True, (), (-11.3, -11.3))
    game.target = "neptune"
    game.hero = "rocket"


def lvl_8():
    """ Level with the outer solar system.
    """
    game.create_body("earth", 30, (210, 430))
    game.create_body("jupiter", 90, (300, 235))
    game.create_body("uranus", 38, (100, 130))
    game.create_body("neptune", 40, (400, 65))
    game.create_body("triton", 15, (415, 140), 1.0, (), True, ("rocket", "earth", "jupiter", "uranus", "pluto", "charon"), (5.5, 0.2))
    game.create_body("pluto", 20, (250, 35), 1.5, (180), True, ("rocket", "earth", "jupiter", "uranus", "neptune", "triton"), (-3.0, 0))
    game.create_body("charon", 18, (251, 85), 1.85, (), True, ("rocket", "earth", "jupiter", "uranus", "neptune", "triton"), (3.0, 0))
    game.create_body("rocket", 30, (0, 0), 0.01, (), True, (), (0.0, -12.0))
    game.target = "pluto"
    game.hero = "rocket"


def run_lvl(lvl_num):
    """ Runs a level based on the integer parameter.
    """
    # call game.__init__(settings.Settings.screen_size) for windowed version. Screen_size defined in settings.py.
    game.__init__()
    game.lvl = lvl_num
    globals()["lvl_" + str(lvl_num)]()
    game.run()


def launcher(num_lvls):
    """ Runs all game levels up to the integer parameter.
    """
    globals()["game"] = engine.Game()
    show_instructions()
    for lvl_num in range(num_lvls):
        run_lvl(lvl_num)

if __name__ == "__main__":
    launcher(settings.Settings.total_lvls)
