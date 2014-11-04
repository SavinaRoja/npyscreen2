# -*- coding: utf-8 -*-

"""
IMPORTANT - COLOUR SUPPORT IS CURRENTLY EXTREMELY EXPERIMENTAL.  THE API MAY
CHANGE, AND NO DEFAULT WIDGETS CURRENTLY TAKE ADVANTAGE OF THEME SUPPORT AT ALL.
"""

import curses
from . import global_options

import logging
log = logging.getLogger('npyscreen2.theme_managers')


def disable_color():
    global_options.DISABLE_ALL_COLORS = True


def enable_color():
    global_options.DISABLE_ALL_COLORS = False


class ThemeManager(object):
    _colors_to_define = (
     # DO NOT DEFINE THIS COLOR - THINGS BREAK
     #('WHITE_BLACK',      DO_NOT_DO_THIS,      DO_NOT_DO_THIS),
     ('BLACK_WHITE',      curses.COLOR_BLACK,      curses.COLOR_WHITE),
     #('BLACK_ON_DEFAULT', curses.COLOR_BLACK,      -1),
     #('WHITE_ON_DEFAULT', curses.COLOR_WHITE,      -1),
     ('BLUE_BLACK',       curses.COLOR_BLUE,       curses.COLOR_BLACK),
     ('CYAN_BLACK',       curses.COLOR_CYAN,       curses.COLOR_BLACK),
     ('GREEN_BLACK',      curses.COLOR_GREEN,      curses.COLOR_BLACK),
     ('MAGENTA_BLACK',    curses.COLOR_MAGENTA,    curses.COLOR_BLACK),
     ('RED_BLACK',        curses.COLOR_RED,        curses.COLOR_BLACK),
     ('YELLOW_BLACK',     curses.COLOR_YELLOW,     curses.COLOR_BLACK),
     ('BLACK_RED',        curses.COLOR_BLACK,      curses.COLOR_RED),
     ('BLACK_GREEN',      curses.COLOR_BLACK,      curses.COLOR_GREEN),
     ('BLACK_YELLOW',     curses.COLOR_BLACK,      curses.COLOR_YELLOW),

     ('BLUE_WHITE',       curses.COLOR_BLUE,       curses.COLOR_WHITE),
     ('CYAN_WHITE',       curses.COLOR_CYAN,       curses.COLOR_WHITE),
     ('GREEN_WHITE',      curses.COLOR_GREEN,      curses.COLOR_WHITE),
     ('MAGENTA_WHITE',    curses.COLOR_MAGENTA,    curses.COLOR_WHITE),
     ('RED_WHITE',        curses.COLOR_RED,        curses.COLOR_WHITE),
     ('YELLOW_WHITE',     curses.COLOR_YELLOW,     curses.COLOR_WHITE),
)

    default_colors = {
        'DEFAULT'     : 'WHITE_BLACK',
        'FORMDEFAULT' : 'WHITE_BLACK',
        'NO_EDIT'     : 'BLUE_BLACK',
        'STANDOUT'    : 'CYAN_BLACK',
        'CURSOR'      : 'WHITE_BLACK',
        'LABEL'       : 'GREEN_BLACK',
        'LABELBOLD'   : 'WHITE_BLACK',
        'CONTROL'     : 'YELLOW_BLACK',
        'IMPORTANT'   : 'GREEN_BLACK',
        'SAFE'        : 'GREEN_BLACK',
        'WARNING'     : 'YELLOW_BLACK',
        'DANGER'      : 'RED_BLACK',
        'CRITICAL'    : 'BLACK_RED',
        'GOOD'        : 'GREEN_BLACK',
        'GOODHL'      : 'GREEN_BLACK',
        'VERYGOOD'    : 'BLACK_GREEN',
        'CAUTION'     : 'YELLOW_BLACK',
        'CAUTIONHL'   : 'BLACK_YELLOW',
    }

    def __init__(self):
        #curses.use_default_colors()
        self._defined_pairs = {}
        self._names = {}
        try:
            self._max_pairs = curses.COLOR_PAIRS - 1
            do_color = True
        except AttributeError:
            # curses.start_color has failed or has not been called
            do_color = False
            # Disable all color use across the application
            disable_color()
        if do_color and curses.has_colors():
            self.initialize_pairs()
            self.initialize_names()

    def find_pair(self, caller, request='DEFAULT'):
        #log.debug('ThemeManager.find_pair called by {0}, request={1}'.format(caller, request))
        if not curses.has_colors() or global_options.DISABLE_ALL_COLORS:
            return False

        if request == 'DEFAULT':
            request = caller.color
        # Locate the requested colour pair.  Default to default if not found.
        try:
            pair = self._defined_pairs[self._names[request]]
        except:
            pair = self._defined_pairs[self._names['DEFAULT']]

        #now make the actual attribute
        color_attribute = curses.color_pair(pair[0])

        return color_attribute

    def set_default(self, caller):
        return False

    def initialize_pairs(self):
        # White on Black is fixed as color_pair 0
        self._defined_pairs['WHITE_BLACK'] = (0, curses.COLOR_WHITE, curses.COLOR_BLACK)
        for cp in self.__class__._colors_to_define:
            if cp[0] == 'WHITE_BLACK':
                #silently protect the user from breaking things.
                continue
            self.initalize_pair(cp[0], cp[1], cp[2])

    def initialize_names(self):
        self._names.update(self.__class__.default_colors)

    def initalize_pair(self, name, fg, bg):
        #Initialize a color_pair for the required color and return the number.
        #Raise an exception if this is not possible.
        if (len(list(self._defined_pairs.keys())) + 1) == self._max_pairs:
            raise Exception("Too many colours")

        _this_pair_number = len(list(self._defined_pairs.keys())) + 1

        curses.init_pair(_this_pair_number, fg, bg)

        self._defined_pairs[name] = (_this_pair_number, fg, bg)

        return _this_pair_number

    def get_pair_number(self, name):
        return self._defined_pairs[name][0]
