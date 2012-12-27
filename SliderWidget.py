import pygame
from pygame.locals import *

SLIDER_WIDGET_CLICK = USEREVENT + 2

class SliderWidget(object):

    # Hand Cursor
    __hand_cursor_string = (
        "     XX         ",
        "    X..X        ",
        "    X..X        ",
        "    X..X        ",
        "    X..XXXXX    ",
        "    X..X..X.XX  ",
        " XX X..X..X.X.X ",
        "X..XX.........X ",
        "X...X.........X ",
        " X.....X.X.X..X ",
        "  X....X.X.X..X ",
        "  X....X.X.X.X  ",
        "   X...X.X.X.X  ",
        "    X.......X   ",
        "     X....X.X   ",
        "     XXXXX XX   ")
    __hcurs, __hmask = pygame.cursors.compile(__hand_cursor_string, ".", "X")
    __hand = ((16, 16), (5, 1), __hcurs, __hmask)

    # Image
    def __get_image(self):
        return self.__m_image
    def __set_image(self, image):
        if self.__m_image != image:
            self.__m_image = image
            self.surface = image.copy()
    def __del_image(self):
        del self.__m_image
        del self.surface
    image = property(__get_image, __set_image, __del_image)
    # Value
    def __get_value(self):
        return self.__m_value
    def __set_value(self, value):
        if self.__m_value != value:
            self.__m_value = value
            self.slide_to_value()
    value = property(__get_value, __set_value)
    # Highlight
    def __get_highlight(self):
        return self.__m_highlight
    def __set_highlight(self, highlight):
        if self.__m_highlight != highlight:
            self.__m_highlight = highlight
            self.update_cursor()
    highlight = property(__get_highlight, __set_highlight)
    # Highlight Rect
    def __get_highlight_rect(self):
        return self.__m_highlight_rect
    def __set_highlight_rect(self, highlight_rect):
        self.fill_rect = highlight_rect.copy()
        self.__m_highlight_rect = highlight_rect.copy()
        self.__m_highlight_rect.top += self.rect.top
        self.__m_highlight_rect.left += self.rect.left
    highlight_rect = property(__get_highlight_rect, __set_highlight_rect)
    # Show Highlight Cursor
    def __get_highlight_cursor(self):
        return self.__m_highlight_cursor
    def __set_highlight_cursor(self, highlight_cursor):
        if self.__m_highlight_cursor != highlight_cursor:
            self.__m_highlight_cursor = highlight_cursor
            self.update_cursor()
    highlight_cursor = property(__get_highlight_cursor, __set_highlight_cursor)

    def __init__(self, image, position, highlight_rect, value_minnmax, colour, show_highlight_cursor = True):
        """ Initialize the SliderWidget
        @param image - surface - The image for the slider widget
        @position - tuple - The position of the widget
        @param highlight_rect - rect - The rect which controls the widget
        @param size = 32 - number - The size of the text
        @param show_highlight_cursor = True - boolean - Whether or not to change
        the cursor when the image is highlighted.  The cursor will turn into
        a hand if this is true.
        """

        # inits
        self.tracking = False
        self.rect = image.get_rect()
        self.rect.topleft = position
        self.left = self.rect.left + 10
        self.right = self.rect.right - 10
        self.width = self.rect.width - 20

        # property inits
        self.__m_image = image
        self.__m_value = float
        self.__m_rect = image.get_rect()
        self.__m_highlight = False
        self.__m_highlight_rect = pygame.Rect
        self.__m_highlight_cursor = False

        self.image = image
        self.surface = image.copy()
        self.fill_rect = pygame.Rect
        self.highlight_rect = highlight_rect
        self.colour = colour
        self.highlight = False
        self.highlight_cursor = show_highlight_cursor
        self.value_min = value_minnmax[0]
        self.value_diff = value_minnmax[1] - self.value_min
        self.value = float

    def __str__(self):
        return "SliderWidget: %s widget in %s" % (self.highlight_rect, self.rect)

    def update_cursor(self):
        if self.highlight_cursor:
            if self.highlight:
                pygame.mouse.set_cursor(*self.__hand)
            else:
                pygame.mouse.set_cursor(*pygame.cursors.arrow)

    def draw(self, screen):
        """ Draw yourself slider widget
        @param screen - pygame.Surface - The surface that we will draw to
        @colour - rgb colour to fill the highlighted rectangle
        @returns - pygame.rect - If drawing has occurred this is the
        rect that we drew to.  None if no drawing has occurerd."""

        rect_return = None
        if self.image and self.surface and self.highlight_rect and self.rect:
            if self.highlight or self.tracking:
                self.surface.fill(self.colour, self.fill_rect)
            else:
                self.surface.fill((185, 185, 185), self.fill_rect)
            rect_return = self.rect
            screen.blit(self.surface, rect_return)
            self.surface = self.image.copy()
        return rect_return

    def erase(self, screen, background):
        """ Erase yourself slider widget
        @param screen - pygame.Surface - The surface that we will erase from
        @param background - pygame.Surface - The background we will draw with
        @returns - pygame.rect - If drawing has occurred this is the
        rect that we drew to.  None if no drawing has occurerd."""

        rect_return = None
        if self.image and self.highlight_rect and self.rect:
            rect_return = self.rect
            screen.blit(background, rect_return, rect_return)
        return rect_return

    def value_transform(self):
        """ Return the current value of the slider.
        """
        self.value = (((self.highlight_rect.left - self.left) / float(self.width - self.highlight_rect.width)) *
                                                                     self.value_diff) + self.value_min

    def slide_to_value(self):
        """ Moves self.highlight_rect.left to where it should be for the current value.
        """
        new_pos = ((self.value - self.value_min) * (float(self.width - self.highlight_rect.width)
                                                / self.value_diff)) + (self.left - self.rect.left)
        if self.value_min <= self.value <= self.value_min + self.value_diff and new_pos != self.highlight_rect.left - self.rect.left:
            self.highlight_rect = pygame.Rect(new_pos, self.fill_rect.top, self.fill_rect.width, self.fill_rect.height)

    def on_mouse_motion(self, event):
        """ Called by the main application when the
        MOUSEMOTION event fires.
        @param event - Pygame Mousemotion Event object
        MOUSEMOTION pos, rel, buttons
        Modifies self.value to the value that the widget got dragged to, according to the min and max value
        """
        old_centerx = self.highlight_rect.centerx
        self.highlight = self.highlight_rect.collidepoint(event.pos)
        if self.tracking:
            if self.left <= self.highlight_rect.left <= self.right - self.highlight_rect.width \
            or (self.highlight_rect.left < self.left and event.pos[0] - self.highlight_rect.centerx >= 0) \
            or (self.highlight_rect.right > self.right and event.pos[0] - self.highlight_rect.centerx <= 0):
                self.highlight_rect.centerx = event.pos[0]
            if self.highlight_rect.left < self.left:
                self.highlight_rect.left = self.left
            elif self.highlight_rect.right > self.right:
                self.highlight_rect.right = self.right
            self.fill_rect.move_ip(self.highlight_rect.centerx - old_centerx, 0)
            self.value_transform()

    def on_mouse_button_down(self, event):
        """ Called by the main application when the
        MOUSEBUTTONDOWN event fires.
        @param event - Pygame Event object
        MOUSEBUTTONDOWN  pos, button
        """
        # Check for collision
        self.tracking = False
        if self.highlight_rect.collidepoint(event.pos):
            self.tracking = True

    def on_mouse_button_up(self, event):
        """ Called by the main application when the
        MOUSEBUTTONUP event fires.
        @param event - Pygame Event object
        MOUSEBUTTONUP  pos, button
        """
        # Check for collision
        if self.tracking and self.highlight_rect.collidepoint(event.pos):
            # Not Tracking anymore
            self.tracking = False
            self.on_mouse_click(event)

    def on_mouse_click(self, event):
        """ Called by the main application when the
        MOUSEBUTTONDOWN event fires, and the slider widget
        has been clicked on. You can either let
        this post the event (default) or you can override this
        function call in your app.
        ie. mySliderWidget.on_mouse_click = my_click_handler
        @param event - Pygame Event object
        MOUSEBUTTONDOWN  pos, button
        """
        # Create the SLIDER_WIDGET_CLICK event
        event_attrib = {}
        event_attrib["button"] = event.button
        event_attrib["pos"] = event.pos
        event_attrib["text_widget"] = self
        e = pygame.event.Event(SLIDER_WIDGET_CLICK, event_attrib)
        pygame.event.post(e)
