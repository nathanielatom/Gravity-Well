"""
Dimmer class

Tobias Thelen (tthelen@uni-osnabrueck.de)
6 September 2001

PUBLIC DOMAIN
Use it in any way you want...

tested with: Pyton 2.0/pygame-1.1, Windows 98

A class for 'dimming' (i.e. darkening) the entire screen, useful for:
- indicating a 'paused' state
- drawing user's attention away from background to e.g. a Quit/Don't Quit
  dialog or a highscore list or...

Usage:

dim=Dimmer(keepalive=1)
  Creates a new Dimmer object,
  if keepalive is true, the object uses the same surface over and over again,
  blocking some memory, but that makes multiple undim() calls possible - 
  Dimmer can be 'abused' as a memory for screen contents this way..

dim.dim(darken_factor=64, color_filter=(0,0,0))
  Saves the current screen for later restorage and lays a filter over it -
  the default color_filter value (black) darkens the screen by blitting a 
  black surface with alpha=darken_factor over it.
  By using a different color, special effects are possible,
  darken_factor=0 just stores the screen and leaves it unchanged

dim.undim()
  restores the screen as it was visible before the last dim() call.
  If the object has been initialised with keepalive=0, this only works once.

"""

import pygame


class Dimmer:
    def __init__(self, keepalive=0):
        self.keepalive=keepalive
        if self.keepalive:
            self.buffer=pygame.Surface(pygame.display.get_surface().get_size())
        else:
            self.buffer=None

    def get_dim(self):
        return bool(self.buffer)

    def dim(self, darken_factor=64, color_filter=(0,0,0)):
        if not self.keepalive:
            self.buffer=pygame.Surface(pygame.display.get_surface().get_size())
        self.buffer.blit(pygame.display.get_surface(),(0,0))
        if darken_factor>0:
            darken=pygame.Surface(pygame.display.get_surface().get_size())
            darken.fill(color_filter)
            darken.set_alpha(darken_factor)
            # safe old clipping rectangle...
            old_clip=pygame.display.get_surface().get_clip()
            # ..blit over entire screen...
            pygame.display.get_surface().blit(darken,(0,0))
            pygame.display.update()
            # ... and restore clipping
            pygame.display.get_surface().set_clip(old_clip)

    def undim(self):
        if self.buffer:
            pygame.display.get_surface().blit(self.buffer,(0,0))
            pygame.display.update()
            if not self.keepalive:
                self.buffer=None
