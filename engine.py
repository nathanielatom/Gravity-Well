""" Contains all key code to power the game. To change various constant parameters used in this code,
see settings.py. To edit or create new levels, see levels.py. Also see levels.py for the game description.
"""
import pygame
from pygame.locals import *
import dimmer
import TextWidget
import SliderWidget
import math
import time
import sys
import settings
import os


def load_image(name, colorkey=None):
    """ Returns a pygame surface object loaded from a PNG file with name (name) in the local/data directory.
    """
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image


def click_to_continue():
    """ Affective function, used to delay game until the mouse is clicked or the enter button is pressed. 
    """
    start = False
    while not start:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key in (K_ESCAPE, K_q)):
                sys.exit()
            if event.type == MOUSEBUTTONUP:
                start = True
            if event.type == KEYDOWN and event.key == K_RETURN:
                start = True


def surface_angler(surface, rect, angle):
    """ Returns a pygame surface and corresponding pygame rect rotated by the given angle.
    """
    angled_surf = pygame.transform.rotate(surface, angle)
    angled_rect = angled_surf.get_rect()
    angled_rect.center = rect.center
    return angled_surf, angled_rect


def get_center(screen_size, object_size):
    """ Returns the position for a desired object to be in the center of the screen.
    """
    return (screen_size[0] / 2 - object_size[0] / 2, screen_size[1] / 2 - object_size[1] / 2)


def vector_float_to_int(vector):
    """ Returns the rounded, integer version of a 2-tuple vector containing floats.
    """
    return (int(round(vector[0])), int(round(vector[1])))


def vector_point_exponentiate(vector, exponent_vector):
    """ Takes each entry in the given tuple vector and raises it to the exponent being the corresponding entry 
    in the tuple exponent_vector. Therefore the length of each vector must match. Else the exponent can be a single 
    number applied to every entry of the given vector. Returns the result.
    """
    resultant = None
    if type(vector) == tuple:
        if type(exponent_vector) == tuple and len(vector) == len(exponent_vector):
            resultant = range(len(vector))
            for index, entry in enumerate(vector):
                resultant[index] = entry ** exponent_vector[index]
        elif type(exponent_vector) in (int, float):
            resultant = range(len(vector))
            for index, entry in enumerate(vector):
                resultant[index] = entry ** exponent_vector
        if resultant:
            resultant = tuple(resultant)
    elif type(exponent_vector) in (int, float) and type(vector) in (int, float):
        resultant = vector ** exponent_vector
    return resultant


def vector_sum(vector):
    """ Returns the sum over a tuple vector.
    """
    resultant = 0
    if type(vector) == tuple:
        for entry in vector:
            resultant += entry
    elif type(vector) in (int, float):
        resultant = vector
    return resultant


def vector_point_multiply(vector, multiple_vector):
    """ Takes each entry in the given tuple vector and multiplies it by the corresponding entry in the tuple 
    multiple_vector. Therefore the length of each vector must match. Else the multiple can be a single number 
    applied to every entry of the given vector. Returns the result.
    """
    resultant = None
    if type(vector) == tuple:
        if type(multiple_vector) == tuple and len(vector) == len(multiple_vector):
            resultant = range(len(vector))
            for index, entry in enumerate(vector):
                resultant[index] = entry * multiple_vector[index]
        elif type(multiple_vector) in (int, float):
            resultant = range(len(vector))
            for index, entry in enumerate(vector):
                resultant[index] = entry * multiple_vector
        if resultant:
            resultant = tuple(resultant)
    return resultant


def vector_cap(vector, cap_vector):
    """ Takes each entry in the given tuple vector and ensures that it's lower than the corresponding entry in the 
    tuple cap_vector. Therefore the length of each vector must match. Else the cap can be a single number applied 
    to every entry of the given vector. Returns the result.
    """
    resultant = None
    if type(vector) == tuple:
        if type(cap_vector) == tuple and len(vector) == len(cap_vector):
            resultant = range(len(vector))
            for index, entry in enumerate(vector):
                if entry > cap_vector[index]:
                    resultant[index] = cap_vector[index]
                else:
                    resultant[index] = entry
        elif type(cap_vector) in (int, float):
            resultant = range(len(vector))
            for index, entry in enumerate(vector):
                if entry > cap_vector:
                    resultant[index] = cap_vector
                else:
                    resultant[index] = entry
        if resultant:
            resultant = tuple(resultant)
    return resultant


def vector_add(vectors):
    """ Takes a list of 2-tuple vectors and performs vector addition,
     returning the resultant 2-tuple vector.
    """
    resultant = [0, 0]
    for vector in vectors:
        resultant[0] += vector[0]
        resultant[1] += vector[1]
    return tuple(resultant)


def vector_negate(vector):
    """ Takes a 2-tuple vector and returns the vector multiplied by -1.
    """
    return (vector[0] * - 1, vector[1] * - 1)


def cartesian_to_polar(vector):
    """ Returns the 2-tuple cartesian vector converted to a polar vector.
    """
    magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    angle = math.atan2(vector[1], vector[0])
    return (magnitude, angle)


def polar_to_cartesian(vector):
    """ Returns the 2-tuple polar vector converted to a cartesian vector.
    """
    x = vector[0] * math.cos(vector[1])
    y = vector[0] * math.sin(vector[1])
    return (x, y)


class Body(pygame.sprite.Sprite):
    """ Creates objects that represent celestial bodies onscreen. Can be affected by gravitational forces, or simply
    stay stationary and create a gravitational field (particle parameter). Inherits from pygame's sprite class, which
    takes a surface (should be the return value of load_image function). Includes all methods needed to determine
    gravitational force, motion, and collision detection.
    """

    # Universal Gravitational Constant:
    # Actual value is 6.67 * 10 ** (-11), good default: 3.0
    # Should use floats and keep above ~1.0 to reduce low-acceleration smoothing lag
    G = settings.Settings.G_default

    def __init__(self, surface, position, mass, point_lvls=(), particle=False, rebel_scum=(), velocity=(0, 0)):
        """ Initializes body object. Parameters: surface - pygame surface (returned by load_image), position - 2-tuple
        vector with the body's initial position (top-left corner of surface) in a 1-500 point scale, mass - used to
        calculate gravitation, point_lvls - scores at which info-bits regarding the body are displayed,
        particle - whether or not the body undergoes gravitational acceleration or is stationary,
        rebel_scum - tuple containing strings of all other bodies which do not affect this body's gravitation,
        velocity - 2-tuple vetor with the body's initial velocity in pixels / game tick (dependent on fps).
        """
        pygame.sprite.Sprite.__init__(self)
        self.init_image = surface
        self.image = surface.copy()
        self.rect = surface.get_rect()
        self.init_position = position
        self.rect.topleft = position
        self.mask = pygame.mask.from_surface(surface)

        self.rebel_scum = list(rebel_scum)
        self.mass = mass
        # Assumes uniform density, calculating center of mass (com) by a body's geometric centroid:
        self.init_com = vector_add([self.mask.centroid(), position])
        self.com = self.init_com
        # A rough "radius" based on half the average of the width and height of the body in pixels. Works as a
        # good estimate when the body is a circle, which just barely fits inside a square surface. Not needed
        # to be precise: used for scoring system where points accumulate based on position in a body's gravitational
        # field.
        self.rough_radius = ((surface.get_height() + surface.get_width()) / 2.0) / 2.0
        # Stores acculated score
        self.points = 0.0
        # used to display info-bits when it surpasses the values in
        self.point_lvls = []
        for point_lvl in point_lvls: self.point_lvls.append(point_lvl)
        self.visible = True
        self.particle = particle
        self.init_velocity = velocity
        self.velocity = velocity
        self.acceleration = (0.0, 0.0)
        self.smoother = [0.0, 0.0]

    def reset_particle(self):
        """ Affective method, resets the body to its initial state.
        """
        self.points = 0.0
        if self.particle:
            self.rect.topleft = self.init_position
            self.com = self.init_com
            self.velocity = self.init_velocity
            self.acceleration = (0.0, 0.0)
            self.smoother = [0.0, 0.0]

    def visify(self):
        """ Changes and returns the new state of self.visible.
        """
        if self.visible:
            self.visible = False
            return False
        else:
            self.visible = True
            return True

    def descumifier(self, bodies):
        """ Parameter: bodies - dictionary of all badies with their names as keys and objects as values.
        Returns a list of body objects corresponding to the names of the bodies in self.rebel_scum.
        """
        rebel_bodies = []
        for name in self.rebel_scum:
            if name in bodies.keys():
                rebel_bodies.append(bodies[name])
        return rebel_bodies

    def get_seperation(self, other):
        """ Takes another body object and returns a cartesian 2-tuple vector with the distance in pixels between
        their center of masses.
        """
        return vector_add([vector_negate(self.com), other.com])

    def get_gravitational_force(self, other):
        """ Takes another body object and returns a cartesian 2-tuple vector with the gravitational force between them.
        """
        r, angle = cartesian_to_polar(self.get_seperation(other))
        # Force is calculated for demonstration purposes, using gravitational acceleration due to each body would be
        # more computationally efficient (see get_acceleration method).
        # Newton's Universal Law of Gravitation F_g = G * m * M / r ** 2:
        magnitude = self.G * self.mass * other.mass / float(r ** 2)
        return polar_to_cartesian((magnitude, angle))

    def get_acceleration(self, bodies):
        """ Parameter: bodies - dictionary of all badies with their names as keys and objects as values.
        Returns the net gravitational acceleration cartesian 2-tuple vector of this body.
        Excludes all rebel bodies - bodies named in self.rebel_scum.
        """
        forces = []
        for body in bodies.values():
            if body != self and body not in self.descumifier(bodies):
                forces.append(self.get_gravitational_force(body))
        # Net force:
        magnitude, angle = cartesian_to_polar(vector_add(forces))
        # Newton's Second Law a = F_net / m
        return polar_to_cartesian((magnitude / float(self.mass), angle))

    def update_velocity(self, bodies):
        """  Affective method, updates the body's acceleration and updates the body's velocity using discrete
        integration (cumulative sum), if the body is allowed to move.
        """
        if self.particle:
            self.acceleration = self.get_acceleration(bodies)
            self.velocity = vector_add([self.velocity, self.acceleration])

    def update_points(self, hero):
        """ Affective method, updates the body's score, used in a scoring system where points accumulate based on
        the position of the launchable "hero" (taken as a body object parameter) in this body's gravitational field.
        The score for each body is used to determine when to reveal info-bits regarding the body.
        """
        if self != hero and hero.visible:
            points = settings.Settings.point_modifier / (cartesian_to_polar(self.get_seperation(hero))[0] -
                                                         self.rough_radius) ** 2
            if points > settings.Settings.point_modifier / settings.Settings.point_max_increment_distance ** 2:
                self.points += \
                    settings.Settings.point_modifier / settings.Settings.point_max_increment_distance ** 2
            else:
                self.points += points

    def move(self):
        """ Affective method, moves the body if it is allowed to move. Includes a smoother, which accumulates when
        a component of the body's motion rounds to zero, keeping the body moving in that component realistically,
        dealing with the issue of rounding and motion by integer number of pixels.
        """
        if self.particle:
            if round(self.velocity[0]) == 0.0:
                self.smoother[0] += self.velocity[0]
            if round(self.velocity[1]) == 0.0:
                self.smoother[1] += self.velocity[1]
            x, y = vector_float_to_int(self.velocity)
            if round(self.smoother[0]) != 0.0:
                x += vector_float_to_int(self.smoother)[0]
                self.smoother[0] = 0.0
            if round(self.smoother[1]) != 0.0:
                y += vector_float_to_int(self.smoother)[1]
                self.smoother[1] = 0.0
            self.rect = self.rect.move(x, y)
            self.com = vector_add([self.com, (x, y)])

    def angler(self, angle):
        """ Affective method, angles the body in the direction of motion, if the body is allowed to move.
        Handles changes in the position of the center of mass as well.
        """
        if self.particle:
            self.image, self.rect = surface_angler(self.init_image, self.rect, angle)
            self.mask = pygame.mask.from_surface(self.image)
            self.com = vector_add([self.mask.centroid(), self.rect.topleft])

    def check_collision(self, other):
        """ Uses pygame mask objects for pixel perfect collision detection, takes another body object, and returns the
        number of pixels overlapping.
        """
        return self.mask.overlap_area(other.mask, vector_add([vector_negate(self.rect.topleft), other.rect.topleft]))

    def check_overlap(self, other):
        """ Uses pygame rect objects to check if two surfaces are overlapping, for clean drawing purposes.
        """
        return self.rect.colliderect(other.rect)


class Game:
    """ Creates the main game object, and initializes the game. Contains the main game run loop, the event loop
    for input, screen drawing procedures, user-interface procedures, and general game simulating procedures. There are
    three game states: preview, action, and reset.
    """

    def __init__(self, screen_size=None):
        """ Initializes the game. Only takes screen size as a tuple parameter, should keep above 400 by 400 pixels.
        Screen size is set to fullscreen by default. Initialization method.
        """
        pygame.init()
        if not screen_size:
            self.screen = pygame.display.set_mode((0, 0), FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_icon(load_image("cassini.png"))
        pygame.display.set_caption("Gravity Well")
        self.lvl = int
        self.clock = pygame.time.Clock()
        self.fps = settings.Settings.fps
        self.dimmer = dimmer.Dimmer()
        self.bodies = {}
        self.quit_lvl = False
        self.ask = False
        self.real_quit = False
        self.hero = None
        self.target = None
        self.halo_rect_size = None
        self.update_rects = []
        self.info_rects = []
        self.completed_facts = []
        self.widgets = []
        self.running = True
        self.launch_time = 0
        self.hero_launcher = pygame.Surface
        self.angle_hero = (False, 0.0)
        self.atmosphere = False
        self.game_state = "preview"
        self.screen_breakout = 0
        self.pause_breakout = 0
        self.current_overlap = False
        self.replay = {}
        self.replay_count = 0
        self.q_mode = False
        self.g_default = Body.G
        text_size = int(round(settings.Settings.text_size *
                                                (self.screen.get_width() * self.screen.get_height())))
        self.font = pygame.font.Font(None, text_size)
        settings.Settings.point_modifier = settings.Settings.percent_point_modifier * (self.screen.get_width() *
                                                                               self.screen.get_height())
        self.pause_widget = TextWidget.TextWidget("PAUSE", settings.Settings.widget_colour, 30, 5)
        self.reset_widget = TextWidget.TextWidget("RESET", settings.Settings.widget_colour, 30, 5)
        self.quit_widget = TextWidget.TextWidget("QUIT", settings.Settings.widget_colour, 30, 5)
        self.start_widget = TextWidget.TextWidget("READY LAUNCH", settings.Settings.widget_colour, 80, 10)
        self.observe_widget = TextWidget.TextWidget("OBSERVE", settings.Settings.widget_colour, 40, 3)
        self.launch_widget = TextWidget.TextWidget("LAUNCH", settings.Settings.widget_colour, 40, 3)
        for instant_replays in range(settings.Settings.instant_replays):
            var_str = "replay_%i_widget" % instant_replays
            colour = vector_cap(vector_point_multiply(settings.Settings.widget_colour, vector_point_exponentiate(
                settings.Settings.replay_colours, instant_replays)), 255)
            vars(self)[var_str] = TextWidget.TextWidget("", colour, 32, 2)
        self.angle_widget = SliderWidget.SliderWidget(pygame.transform.smoothscale(load_image("slidy_bar.png"),
            (200, 80)), (420, 40), pygame.Rect(0, 22, 10, 30), (-180.0, 180.0), settings.Settings.widget_colour)
        self.speed_widget = SliderWidget.SliderWidget(pygame.transform.smoothscale(load_image("slidy_bar.png"),
            (200, 80)), (650, 40), pygame.Rect(0, 22, 10, 30), (settings.Settings.min_speed,
                                                                 settings.Settings.max_speed),
            settings.Settings.widget_colour)
        self.set_widgets()

    def draw_background(self):
        """ Draws background.png file as the background. Affective method.
        """
        self.background_surf = pygame.transform.smoothscale(load_image("background.png"), self.screen.get_size())
        self.screen.blit(self.background_surf, (0, 0))
        pygame.display.update()

    def screen_update(self):
        """ Updates necessary parts of the screen. Affective method.
        """
        pygame.display.update(self.update_rects)
        self.update_rects = []

    def coordinate_conversion(self, coordinate):
        """ Takes a 2-tuple for a coordinate in a 500x500 screen, and returns a correspondingly converted floated
        value for the current screen. If an int is passed, then it returns floated square coordinates correspondingly
        converted for the current screen, such that they can be as large as the screen's minimum dimension.
        Functional method.
        """
        if type(coordinate) == tuple:
            return ((coordinate[0] / 500.0) * self.screen.get_size()[0], (coordinate[1] / 500.0) *
                                                                         self.screen.get_size()[1])
        elif type(coordinate) == int:
            # A squire must prove himself to earn the right to become a square.
            squire = (coordinate / 500.0) * min(self.screen.get_size())
            return (squire, squire)

    def create_body(self, name, size, position, density=1.0, point_lvls=(), particle=False, rebel_scum=(),
                    velocity=(0.0, 0.0)):
        """ Creates a body called name, with the given size (converted from a 1-500 point scale),
        position (same scale for each coordinate), optional: density used to calculate the body's mass, list of scores
        for which info-bits regarding this body appear, affected by gravitational force (True) or stationary (False),
        a tuple containing the names of other bodies which do not affect its gravitational field, an
        initial velocity vector (should use floats and keep under (12.0, 12.0) to avoid inconsistent simulations
        caused by large jumps). Initialization method.
        """
        self.bodies[name] = Body(pygame.transform.smoothscale(load_image(name + ".png"),
            vector_float_to_int(self.coordinate_conversion(size))),
            vector_float_to_int(self.coordinate_conversion(position)),
            (vector_sum(vector_point_exponentiate(size, 2)) * density), point_lvls, particle, rebel_scum, velocity)
        if name == "earth":
            self.hero_launcher = pygame.transform.smoothscale(load_image("rocket_launcher_right.png"),
                vector_float_to_int(self.coordinate_conversion(size + 10)))
            self.hero_launcher_rect = self.hero_launcher.get_rect()
            self.hero_launcher_rect.center = self.bodies["earth"].rect.center

    def draw_body(self, name):
        """ Draws the named body. Affective method.
        """
        if self.bodies[name].visible:
            self.screen.blit(self.bodies[name].image, self.bodies[name].rect)
            self.update_rects.append(self.bodies[name].rect.copy())

    def draw_all_bodies(self):
        """ Draws all bodies to the screen and also modifies self.update_rects. Affective method.
        """
        for name in self.bodies.keys():
            self.draw_body(name)

    def draw_all_particles(self):
        """ Draws all particles to the screen and also modifies self.update_rects. Affective method.
        """
        if not self.current_overlap:
            for name in self.bodies.keys():
                if self.bodies[name].particle:
                    self.draw_body(name)
        else:
            self.draw_all_bodies()

    def erase_body(self, name):
        """ Erases the named body. Affective method.
        """
        if self.bodies[name].visible:
            self.screen.blit(self.background_surf, self.bodies[name].rect, self.bodies[name].rect)
            self.update_rects.append(self.bodies[name].rect.copy())

    def erase_all_bodies(self):
        """ Erases all bodies from the screen and also modifies self.update_rects,
        and is meant to be called before draw_all_bodies() or draw_all_particles(). Affective method.
        """
        for name in self.bodies.keys():
            self.erase_body(name)

    def erase_all_particles(self):
        """ Erases all particles from the screen and also modifies self.update_rects,
        and is meant to be called before draw_all_bodies() or draw_all_particles(). Affective method.
        """
        self.current_overlap = self.check_all_overlap()
        if not self.current_overlap:
            for name in self.bodies.keys():
                if self.bodies[name].particle:
                    self.erase_body(name)
        else:
            self.erase_all_bodies()

    def get_hero(self):
        """ Returns the name of the hero. Functional method.
        """
        return self.hero

    def hero_hide(self):
        """ Hides the hero from the screen and simulation. Affective method.
        """
        name = self.get_hero()
        if self.bodies[name].visible:
            self.erase_body(name)
            if not self.bodies[name].visify():
                self.bodies[name].particle = False
                for body in self.bodies.values():
                    body.rebel_scum.append(name)

    def hero_seek(self):
        """ Brings the hero back to the screen and simulation. Affective method.
        """
        name = self.get_hero()
        if not self.bodies[name].visible:
            if self.bodies[name].visify():
                self.bodies[name].particle = True
                for body in self.bodies.values():
                    body.rebel_scum.remove(name)

    def toggle_halo(self):
        """ Sets the target halo appropriately, during various game states. Affective method.
        """
        if self.target:
            if not self.halo_rect_size:
                new_image = pygame.transform.smoothscale(load_image("halo.png"),
                    vector_add([self.bodies[self.target].init_image.get_rect().size, (10, 10)]))
                new_image.blit(self.bodies[self.target].init_image, (5, 5))
                self.bodies[self.target].image = new_image.copy()
                self.halo_rect_size = self.bodies[self.target].rect.size
                self.bodies[self.target].rect.size = vector_add([self.bodies[self.target].init_image.get_rect().size, (10, 10)])
            else:
                self.bodies[self.target].image = self.bodies[self.target].init_image.copy()
                self.screen.blit(self.background_surf, self.bodies[self.target].rect, self.bodies[self.target].rect)
                self.update_rects.append(self.bodies[self.target].rect.copy())
                self.bodies[self.target].rect.size = self.halo_rect_size
                self.halo_rect_size = None

    def hero_launch_time(self):
        """ Draws the launchable hero to the screen, as it changes angle to match the player's input trajectory.
        Affective method.
        """
        if self.game_state == "reset" and not self.dimmer.get_dim():
            self.erase_all_bodies()
            self.screen.blit(self.background_surf, self.hero_launcher_rect, self.hero_launcher_rect)
            self.update_rects.append(self.hero_launcher_rect.copy())
            self.angled_hero_launcher, self.hero_launcher_rect = surface_angler(self.hero_launcher,
                self.hero_launcher_rect, self.hero_angle)
            self.screen.blit(self.angled_hero_launcher, self.hero_launcher_rect)
            self.update_rects.append(self.hero_launcher_rect.copy())
            self.draw_all_bodies()

    def draw_info(self, info, position, colour = (255, 255, 255)):
        """ Draws any type of info to the screen (but does not update it). Affective method.
        """
        txt = self.font.render(info, True, colour)
        info_rect = txt.get_rect()
        info_rect.topleft = position
        self.screen.blit(txt, info_rect.topleft)
        self.update_rects.append(info_rect.copy())
        self.info_rects.append(info_rect)

    def erase_last_info(self):
        """ Erases everything inside the most recent info rect (but does not update it), intended to be info.
        Affective method.
        """
        if self.info_rects != []:
            info_rect = self.info_rects[-1]
            self.screen.blit(self.background_surf, info_rect, info_rect)
            self.update_rects.append(info_rect.copy())
            self.info_rects.remove(info_rect)

    def erase_all_info(self):
        """ Erases all info onscreen but does not update it. Affective method.
        """
        while self.info_rects != []:
            self.erase_last_info()

    def get_text_size(self, text):
        """ Returns a 2-tuple representing the size of the rendered text on the screen. Functional method.
        """
        rect = self.font.render(text, True, (255, 255, 255)).get_rect()
        return rect.size

    def draw_velocity_info(self, velocity):
        """ Draws velocity info and causes related effects. Affective method.
        """
        if self.game_state == "reset":
            angle = math.degrees(cartesian_to_polar(velocity)[1]) * - 1
            self.angle_widget.value = angle * - 1
            self.speed_widget.value = cartesian_to_polar(velocity)[0]
            if round(angle, 1) == - 0.0:
                angle = 0.0
            if angle < 0:
                angle += 360
            self.erase_all_info()
            self.draw_info("Angle: %3.0f" % angle,
                ((self.screen.get_width() / 2) - settings.Settings.vel_info_x_gap -
                 settings.Settings.vel_info_angle_width, settings.Settings.vel_info_y_down))
            self.draw_info("Speed: %3.1f" % (cartesian_to_polar(velocity)[0]),
                ((self.screen.get_width() / 2) + settings.Settings.vel_info_x_gap, settings.Settings.vel_info_y_down))
            if self.replay and settings.Settings.instant_replays:
                self.draw_info("Previous Attempts:", settings.Settings.previous_attempts_info_pos)
            self.hero_angle = angle

    def draw_all_widgets(self):
        """ Draws all widgets to the screen (but does not update it). Affective method.
        """
        for widget in self.widgets:
            self.update_rects.append(widget.draw(self.screen).copy())

    def erase_all_widgets(self):
        """ Erases all widgets from the screen (but does not update it). Affective method.
        """
        for widget in self.widgets:
            self.update_rects.append(widget.erase(self.screen, self.background_surf).copy())

    def set_widgets(self):
        """ Puts all widgets onscreen for the appropriate game state. Affective method.
        """
        for widget in self.widgets:
            widget.highlight = False
        self.erase_all_widgets()
        if self.game_state == "preview":
            self.pause_widget.rect.topleft = (settings.Settings.pause_reset_info_x,
                                              self.screen.get_rect().bottom - settings.Settings.pause_info_y_up)
            self.reset_widget.rect.topleft = (settings.Settings.pause_reset_info_x,
                                              self.pause_widget.rect.bottom + settings.Settings.y_info_gap)
            self.start_widget.rect.center = self.screen.get_rect().center
            if self.observe_widget in self.widgets:
                self.widgets.remove(self.observe_widget)
            if self.launch_widget in self.widgets:
                self.widgets.remove(self.launch_widget)
            if self.angle_widget in self.widgets:
                self.widgets.remove(self.angle_widget)
            if self.speed_widget in self.widgets:
                self.widgets.remove(self.speed_widget)
            for instant_replays in range(settings.Settings.instant_replays):
                var_str = "replay_%i_widget" % instant_replays
                if vars(self)[var_str] in self.widgets:
                    self.widgets.remove(vars(self)[var_str])
            if not self.pause_widget in self.widgets:
                self.widgets.append(self.pause_widget)
            if not self.reset_widget in self.widgets:
                self.widgets.append(self.reset_widget)
            if not self.start_widget in self.widgets:
                self.widgets.append(self.start_widget)
        if self.game_state == "reset":
            self.observe_widget.rect.topleft = (self.screen.get_rect().right - settings.Settings.observe_launch_info_x,
                                                settings.Settings.observe_info_y_down)
            self.launch_widget.rect.topleft = (self.screen.get_rect().right - settings.Settings.observe_launch_info_x,
                                               self.observe_widget.rect.bottom + settings.Settings.y_info_gap)
            self.pause_widget.rect.topleft = self.reset_widget.rect.copy().topleft
            for instant_replays in range(settings.Settings.instant_replays):
                var_str = "replay_%i_widget" % instant_replays
                if not instant_replays:
                    vars(self)[var_str].rect.topleft = vector_add([settings.Settings.previous_attempts_info_pos,
                                                                   settings.Settings.replay_info_relative_pos])
                else:
                    vars(self)[var_str].rect.left = self.replay_0_widget.rect.left
                    var_str_last = "replay_%i_widget" % (instant_replays - 1)
                    vars(self)[var_str].rect.top = vars(self)[var_str_last].rect.bottom + settings.Settings.y_info_gap
            if self.reset_widget in self.widgets:
                self.widgets.remove(self.reset_widget)
            if self.start_widget in self.widgets:
                self.widgets.remove(self.start_widget)
            if not self.observe_widget in self.widgets:
                self.widgets.append(self.observe_widget)
            if not self.launch_widget in self.widgets:
                self.widgets.append(self.launch_widget)
            if not self.angle_widget in self.widgets:
                self.widgets.append(self.angle_widget)
            if not self.speed_widget in self.widgets:
                self.widgets.append(self.speed_widget)
            for instant_replays in range(settings.Settings.instant_replays):
                var_str = "replay_%i_widget" % instant_replays
                if not vars(self)[var_str] in self.widgets and vars(self)[var_str].text:
                    self.widgets.append(vars(self)[var_str])
        if self.game_state == "action":
            self.pause_widget.rect.topleft = (settings.Settings.pause_reset_info_x,
                                              self.screen.get_rect().bottom - settings.Settings.pause_info_y_up)
            if self.observe_widget in self.widgets:
                self.widgets.remove(self.observe_widget)
            if self.launch_widget in self.widgets:
                self.widgets.remove(self.launch_widget)
            if self.angle_widget in self.widgets:
                self.widgets.remove(self.angle_widget)
            if self.speed_widget in self.widgets:
                self.widgets.remove(self.speed_widget)
            for instant_replays in range(settings.Settings.instant_replays):
                var_str = "replay_%i_widget" % instant_replays
                if vars(self)[var_str] in self.widgets:
                    self.widgets.remove(vars(self)[var_str])
            if not self.reset_widget in self.widgets:
                self.widgets.append(self.reset_widget)
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        self.draw_all_widgets()

    def draw_fact(self, factname):
        """ Displays an info-bit on the screen. Affective method.
        """
        fact_surface = load_image(factname + ".png")
        fact_rect = fact_surface.get_rect(center = self.screen.get_rect().center)
        self.screen.blit(fact_surface, fact_rect)
        self.update_rects.append(fact_rect.copy())
        self.screen_update()
        click_to_continue()
        self.screen.blit(self.background_surf, fact_rect, fact_rect)
        self.update_rects.append(fact_rect.copy())

    def reward_facts(self):
        """ Shows the player info-bits regarding certain bodies whose accumulated score (based on the launchable
        hero's position in their gravitational field) surpasses the score levels set in body.point_lvls.
        """
        for body_name in self.bodies.keys():
            for index, point_lvl in enumerate(self.bodies[body_name].point_lvls):
                if self.bodies[body_name].points > point_lvl:
                    factname = "fact_lvl_%d_%s_%d" % (self.lvl, body_name, index)
                    if not factname in self.completed_facts:
                        self.draw_fact(factname)
                        self.completed_facts.append(factname)

    def check_all_collisions(self):
        """ Returns a dictionary where the keys are 2-tuples of colliding (visible) bodies, and the values are the
        number of pixels involved in the collision. Functional method.
        """
        collision_status = {}
        body_list = self.bodies.items()
        for index in range(len(body_list)):
            for inceptiondex in range(index + 1, len(body_list)):
                collision_area = body_list[index][1].check_collision(body_list[inceptiondex][1])
                if collision_area != 0 and (body_list[index][1].particle or body_list[inceptiondex][1].particle) \
                and body_list[index][1].visible and body_list[inceptiondex][1].visible:
                    collision_status[(body_list[index][0], body_list[inceptiondex][0])] = collision_area
        return collision_status

    def check_all_overlap(self):
        """ Returns true if any body.rects or widget.rects are overlapping, false otherwise. Functional method.
        """
        overlap = False
        body_list = self.bodies.values()
        for index in range(len(body_list)):
            for inceptiondex in range(index + 1, len(body_list)):
                if body_list[index].visible and body_list[inceptiondex].visible:
                    overlap = overlap or body_list[index].check_overlap(body_list[inceptiondex])
        for body in body_list:
            for widget in self.widgets:
                overlap = overlap or widget.rect.colliderect(body.rect)
        return overlap

    def special_collision(self):
        """ Used to check if hero crashes, if so, resets. Affective and functional method.
        """
        collision = self.check_all_collisions().keys()
        if (self.get_hero(), self.target) in collision or (self.target, self.get_hero()) in collision:
            self.quit_lvl = True
        if self.atmosphere and (not ((("earth", self.get_hero()) in collision) or ((self.get_hero(),
                                                                                    "earth") in collision))
                                or cartesian_to_polar(self.bodies[self.get_hero()].velocity)[0] <=
                                settings.Settings.min_escape_speed):
            self.atmosphere = False
        if not self.atmosphere and self.get_time() >= settings.Settings.max_escape_well_time:
            for body_pair in collision:
                if self.get_hero() in body_pair:
                    if self.get_hero() == body_pair[0]:
                        collision_body = body_pair[1]
                    else:
                        collision_body = body_pair[0]
                    self.replay[self.replay_count]["collision_body"] = collision_body
                    self.replay[self.replay_count]["time"] = self.get_time()
                    self.draw_all_bodies()
                    if not self.quit_lvl:
                        self.dimmer.dim(settings.Settings.shade_of_death, settings.Settings.colour_of_death)
                        pygame.time.delay(settings.Settings.crash_delay)
                    self.reset_all()
                    return True
            return False

    def escape_wellist(self):
        """ Resets the game if the hero has been offscreen for settings.Settings.offscreen_reset_time.
        Affective method.
        """
        hero = self.bodies[self.get_hero()]
        if hero.visible:
            if hero.com[0] < 0 or hero.com[0] > self.screen.get_width() or hero.com[1] < 0 or \
               hero.com[1] > self.screen.get_height():
                if not self.screen_breakout:
                    self.screen_breakout = time.time()
                    self.fps *= 2
                if self.screen_breakout and \
                   time.time() - self.screen_breakout > settings.Settings.offscreen_reset_time:
                    self.fps /= 2
                    self.screen_breakout = 0
                    self.replay[self.replay_count]["collision_body"] = "escaped"
                    self.replay[self.replay_count]["time"] = self.get_time()
                    info = "You have been unable to gather data for %i seconds. Mission Failed. Click to Continue" % \
                           settings.Settings.offscreen_reset_time
                    self.draw_info(info, get_center(self.screen.get_size(), self.get_text_size(info)))
                    self.screen_update()
                    self.dimmer.dim(settings.Settings.shade_of_death, settings.Settings.colour_of_death)
                    click_to_continue()
                    self.reset_all()
            elif not (hero.com[0] < 0 or hero.com[0] > self.screen.get_width() or hero.com[1] < 0 or
                      hero.com[1] > self.screen.get_height()) and self.screen_breakout:
                self.fps /= 2
                self.screen_breakout = 0

    def possible_quit_lvl(self):
        """ Asks the player if they want to go to the next level, or quit. Affective method.
        """
        if self.quit_lvl and not self.ask:
            self.widgets.remove(self.pause_widget)
            self.update_rects.append(self.pause_widget.erase(self.screen, self.background_surf).copy())
            self.pause()
            if self.lvl == (settings.Settings.total_lvls - 1):
                info = "Success! You've beaten the game! Do you want to quit? (y for yes/n for no)"
            else:
                info = "Success! Do you want to proceed to the next level? You'll not be able to come back. " \
                       "(y for yes/n for no)"
            self.draw_info(info, get_center(self.screen.get_size(), self.get_text_size(info)))
            self.screen_update()
            self.ask = True

    def reset_all(self):
        """ Resets the screen and simulation. Affective method.
        """
        if self.game_state != "reset":
            if self.dimmer.get_dim():
                self.dimmer.undim()
            self.erase_all_bodies()
            self.screen.blit(self.background_surf, self.hero_launcher_rect, self.hero_launcher_rect)
            self.update_rects.append(self.hero_launcher_rect.copy())
            self.erase_all_info()
            if self.replay and self.game_state == "action" and self.launch_time:
                if not "collision_body" in self.replay[self.replay_count].keys():
                    self.replay[self.replay_count]["collision_body"] = "reset"
                    self.replay[self.replay_count]["time"] = self.get_time()
                real_count_list = range(self.replay_count, -1, -1)
                if (settings.Settings.instant_replays - 1) in self.replay.keys():
                    for index in range((settings.Settings.instant_replays - 1), self.replay_count, -1):
                        real_count_list.append(index)
                for real_count, instant_replays in zip(real_count_list, range(settings.Settings.instant_replays)):
                    var_str = "replay_%i_widget" % instant_replays
                    vars(self)[var_str].text = "%s: %4.2f seconds" % (self.replay[real_count]["collision_body"].upper(),
                                               self.replay[real_count]["time"])
                if self.replay_count < (settings.Settings.instant_replays - 1):
                    self.replay_count += 1
                else:
                    self.replay_count = 0
            Body.G = self.g_default
            self.fps = settings.Settings.fps
            self.erase_all_widgets()
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            self.reward_facts()
            for body in self.bodies.values():
                body.reset_particle()
            if self.game_state == "action":
                self.hero_hide()
                self.toggle_halo()
                self.running = False
                self.atmosphere = True
                self.launch_time = 0
                self.game_state = "reset"
            elif self.game_state == "preview":
                self.running = True
            if self.quit_widget in self.widgets:
                self.erase_all_widgets()
                self.pause_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height))
                self.reset_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height))
                self.widgets.remove(self.quit_widget)
                self.update_rects.append(self.quit_widget.erase(self.screen, self.background_surf).copy())
            if not self.quit_lvl:
                self.set_widgets()
            self.draw_all_bodies()
            self.draw_velocity_info(self.bodies[self.get_hero()].velocity)
            self.screen_update()

    def pause(self):
        """ Pauses and unpauses the game in all game states. Affective method.
        """
        self.set_widgets()
        if self.game_state != "reset":
            if self.running:
                if self.screen_breakout:
                    self.pause_breakout = time.time()
                if self.start_widget in self.widgets:
                    self.widgets.remove(self.start_widget)
                    self.update_rects.append(self.start_widget.erase(self.screen, self.background_surf).copy())
                if not self.quit_widget in self.widgets:
                    self.erase_all_widgets()
                    self.quit_widget.rect.topleft = self.reset_widget.rect.topleft
                    self.pause_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height) * -1)
                    self.reset_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height) * -1)
                    self.widgets.append(self.quit_widget)
                self.draw_all_bodies()
                self.dimmer.dim()
                self.running = False
            else:
                if self.screen_breakout and self.pause_breakout:
                    self.screen_breakout += time.time() - self.pause_breakout
                self.dimmer.undim()
                if self.quit_widget in self.widgets:
                    self.widgets.remove(self.quit_widget)
                    self.update_rects.append(self.quit_widget.erase(self.screen, self.background_surf).copy())
                    self.pause_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height))
                    self.reset_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height))
                    self.set_widgets()
                self.running = True
        else:
            if not self.dimmer.get_dim():
                if self.observe_widget in self.widgets:
                    self.widgets.remove(self.observe_widget)
                    self.update_rects.append(self.observe_widget.erase(self.screen, self.background_surf).copy())
                if self.launch_widget in self.widgets:
                    self.widgets.remove(self.launch_widget)
                    self.update_rects.append(self.launch_widget.erase(self.screen, self.background_surf).copy())
                if self.angle_widget in self.widgets:
                    self.widgets.remove(self.angle_widget)
                    self.update_rects.append(self.angle_widget.erase(self.screen, self.background_surf).copy())
                if self.speed_widget in self.widgets:
                    self.widgets.remove(self.speed_widget)
                    self.update_rects.append(self.speed_widget.erase(self.screen, self.background_surf).copy())
                for instant_replays in range(settings.Settings.instant_replays):
                    var_str = "replay_%i_widget" % instant_replays
                    if vars(self)[var_str] in self.widgets:
                        self.widgets.remove(vars(self)[var_str])
                        self.update_rects.append(vars(self)[var_str].erase(self.screen, self.background_surf).copy())
                self.erase_all_info()
                if not self.quit_widget in self.widgets:
                    self.erase_all_widgets()
                    self.quit_widget.rect.topleft = self.reset_widget.rect.topleft
                    self.pause_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height) * -1)
                    self.reset_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height) * -1)
                    self.widgets.append(self.quit_widget)
                self.draw_all_bodies()
                self.dimmer.dim()
            else:
                self.dimmer.undim()
                if self.quit_widget in self.widgets:
                    self.erase_all_widgets()
                    self.pause_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height))
                    self.reset_widget.rect.move_ip(0, (settings.Settings.y_info_gap + self.quit_widget.rect.height))
                    self.widgets.remove(self.quit_widget)
                    self.update_rects.append(self.quit_widget.erase(self.screen, self.background_surf).copy())
                self.draw_velocity_info(self.bodies[self.get_hero()].velocity)

    def observe(self):
        """ Sets the game state to "preview". Affective method.
        """
        if self.game_state == "reset":
            self.game_state = "preview"
            self.reset_all()

    def ready_launch(self):
        """ Sets the game state to "reset", where the player can change the hero's initial launch trajectory.
        Affective method.
        """
        if self.game_state == "preview":
            self.toggle_halo()
            self.game_state = "action"
            self.reset_all()

    def launch(self):
        """ Sets the game state to "action", where the launch trajectory is simulated. Affective method.
        """
        if self.game_state == "reset":
            self.screen.blit(self.background_surf, self.hero_launcher_rect, self.hero_launcher_rect)
            self.update_rects.append(self.hero_launcher_rect.copy())
            self.bodies[self.get_hero()].angler(self.hero_angle)
            x, y = vector_add([vector_negate(self.bodies[self.get_hero()].rect.center), vector_add(
                [self.angled_hero_launcher.get_bounding_rect().copy().center, self.hero_launcher_rect.copy().topleft])])
            self.bodies[self.get_hero()].rect.move_ip(x, y)
            self.bodies[self.get_hero()].com = vector_add([self.bodies[self.get_hero()].com, (x, y)])
            self.hero_seek()
            self.toggle_halo()
            self.running = True
            self.launch_time = time.time()
            self.erase_all_info()
            self.replay[self.replay_count] = {}
            self.replay[self.replay_count]["velocity"] = self.bodies[self.get_hero()].velocity
            self.game_state = "action"
            self.set_widgets()
            self.draw_all_bodies()

    def get_time(self):
        """ Returns the current time since launch in seconds.
        """
        if self.launch_time:
            return time.time() - self.launch_time
        else:
            return 0

    def arrow_pressed(self, arrow):
        """ Takes keyboard input to modify the hero's initial launch conditions. Affective method.
        """
        if self.game_state == "reset":
            hero = self.bodies[self.get_hero()]
            if arrow == K_UP:
                if cartesian_to_polar(hero.velocity)[0] < settings.Settings.max_speed:
                    hero.velocity = polar_to_cartesian((cartesian_to_polar(hero.velocity)[0] +
                                                     settings.Settings.speed_modifier,
                                                     cartesian_to_polar(hero.velocity)[1]))
            elif arrow == K_DOWN:
                if cartesian_to_polar(hero.velocity)[0] > settings.Settings.min_speed:
                    hero.velocity = polar_to_cartesian((cartesian_to_polar(hero.velocity)[0] -
                                                     settings.Settings.speed_modifier,
                                                     cartesian_to_polar(hero.velocity)[1]))
            elif arrow == K_RIGHT:
                hero.velocity = polar_to_cartesian((cartesian_to_polar(hero.velocity)[0],
                                                 cartesian_to_polar(hero.velocity)[1] +
                                                 math.radians(settings.Settings.angle_modifier)))
            elif arrow == K_LEFT:
                hero.velocity = polar_to_cartesian((cartesian_to_polar(hero.velocity)[0],
                                                 cartesian_to_polar(hero.velocity)[1] -
                                                 math.radians(settings.Settings.angle_modifier)))
            self.draw_velocity_info(hero.velocity)

    def event_loop(self):
        """ Main event loop, which takes all user input: both keyboard input, and mouse input - interacting with
        the onscreen widgets. Affective method.
        """
        keystate = pygame.key.get_pressed()
        if keystate[K_UP] and not (keystate[K_LCTRL] or keystate[K_RCTRL]):
            self.arrow_pressed(K_UP)
        if keystate[K_DOWN] and not (keystate[K_LCTRL] or keystate[K_RCTRL]):
            self.arrow_pressed(K_DOWN)
        if keystate[K_RIGHT] and not (keystate[K_LCTRL] or keystate[K_RCTRL]):
            self.arrow_pressed(K_RIGHT)
        if keystate[K_LEFT] and not (keystate[K_LCTRL] or keystate[K_RCTRL]):
            self.arrow_pressed(K_LEFT)
        if keystate[K_UP] and self.q_mode and self.running and self.game_state == "action":
            if Body.G < settings.Settings.g_max:
                Body.G += settings.Settings.g_modifier
        if keystate[K_DOWN] and self.q_mode and self.running and self.game_state == "action":
            if Body.G > settings.Settings.g_min:
                Body.G -= settings.Settings.g_modifier
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key in (K_ESCAPE, K_q)):
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_n and self.ask:
                    self.pause()
                    self.quit_lvl = False
                    self.ask = False
                    self.widgets.append(self.pause_widget)
                    self.set_widgets()
                if event.key == K_y and self.ask:
                    self.real_quit = True
                if event.key == K_RETURN:
                    self.launch()
                    self.ready_launch()
                if event.key == K_o:
                    self.observe()
                if event.key == K_UP and (keystate[K_LCTRL] or keystate[K_RCTRL]):
                    self.arrow_pressed(K_UP)
                if event.key == K_DOWN and (keystate[K_LCTRL] or keystate[K_RCTRL]):
                    self.arrow_pressed(K_DOWN)
                if event.key == K_RIGHT and (keystate[K_LCTRL] or keystate[K_RCTRL]):
                    self.arrow_pressed(K_RIGHT)
                if event.key == K_LEFT and (keystate[K_LCTRL] or keystate[K_RCTRL]):
                    self.arrow_pressed(K_LEFT)
                if event.key == K_g and self.game_state == "reset":
                    if self.q_mode:
                        self.q_mode = False
                    else:
                        self.q_mode = True
                if event.key in (K_LSHIFT, K_RSHIFT) and self.replay and self.game_state == "reset":
                    if self.replay_count:
                        real_count = self.replay_count - 1
                    else:
                        real_count = (settings.Settings.instant_replays - 1)
                    velocity = self.replay[real_count]["velocity"]
                    self.bodies[self.get_hero()].velocity = velocity
                    self.draw_velocity_info(velocity)
                    self.screen_update()
                if event.key in (K_p, K_SPACE):
                    self.pause()
                if event.key == K_r:
                    self.reset_all()
            if event.type == MOUSEMOTION:
                tracking = False
                for widget in self.widgets:
                    if hasattr(widget, "text"):
                        widget.highlight = widget.rect.collidepoint(event.pos)
                    else:
                        widget.on_mouse_motion(event)
                        tracking = tracking or widget.tracking
                if tracking and self.game_state == "reset" and not self.dimmer.get_dim():
                    hero = self.bodies[self.get_hero()]
                    if self.angle_widget.value:
                        hero.velocity = polar_to_cartesian((cartesian_to_polar(hero.velocity)[0], math.radians(self.angle_widget.value)))
                    if self.speed_widget.value:
                        hero.velocity = polar_to_cartesian((self.speed_widget.value, cartesian_to_polar(hero.velocity)[1]))
                    self.draw_velocity_info(hero.velocity)
            if event.type == MOUSEBUTTONDOWN:
                for widget in self.widgets:
                    widget.on_mouse_button_down(event)
            if event.type == MOUSEBUTTONUP:
                for widget in self.widgets:
                    widget.on_mouse_button_up(event)
            if event.type == TextWidget.TEXT_WIDGET_CLICK:
                if event.text_widget.text == "PAUSE":
                    self.pause()
                if event.text_widget.text == "RESET":
                    self.reset_all()
                if event.text_widget.text == "QUIT":
                    sys.exit()
                if event.text_widget.text == "READY LAUNCH":
                    self.ready_launch()
                if event.text_widget.text == "OBSERVE":
                    self.observe()
                if event.text_widget.text == "LAUNCH":
                    self.launch()
                if self.replay and self.game_state == "reset":
                    if self.replay_count:
                        init_real_count = self.replay_count - 1
                    else:
                        init_real_count = (settings.Settings.instant_replays - 1)
                    real_count_list = range(init_real_count, -1, -1)
                    if (settings.Settings.instant_replays - 1) in self.replay.keys():
                        for index in range((settings.Settings.instant_replays - 1), init_real_count, -1):
                            real_count_list.append(index)
                    for real_count, instant_replays in zip(real_count_list, range(settings.Settings.instant_replays)):
                        var_str = "replay_%i_widget" % instant_replays
                        if event.text_widget.text == vars(self)[var_str].text:
                            velocity = self.replay[real_count]["velocity"]
                            self.bodies[self.get_hero()].velocity = velocity
                            self.draw_velocity_info(velocity)
                            self.screen_update()

    def simulate(self):
        """ Simulates gravity! Erases, updates and redraws all appropriate bodies to the screen. Affective method.
        """
        self.erase_all_particles()
        for body in self.bodies.values():
            body.move()
        if not self.special_collision():
            hero = self.bodies[self.get_hero()]
            hero.angler(math.degrees(cartesian_to_polar(hero.velocity)[1]) * -1)
            for body in self.bodies.values():
                body.update_velocity(self.bodies)
                body.update_points(hero)
            self.draw_all_particles()
            self.escape_wellist()

    def run(self):
        """ Contains the game's main loop. Initializes and runs the game, updating the screen every cycle based
        on the max fps (defined in settings.py). Affective method.
        """
        self.draw_background()
        self.hero_hide()
        self.toggle_halo()
        self.draw_all_bodies()
        while True:
            self.possible_quit_lvl()
            if not self.real_quit:
                self.event_loop()
                self.erase_all_widgets()
                if self.running:
                    self.simulate()
                self.hero_launch_time()
                self.draw_all_widgets()
                self.screen_update()
                self.clock.tick(self.fps)
            else:
                break
