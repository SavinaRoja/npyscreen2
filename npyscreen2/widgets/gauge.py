# -*- coding: utf-8 -*-

import curses
import math

from . import Widget

import logging
log = logging.getLogger('npyscreen2.widgets.gauge')


class Gauge(Widget):
    """
    The Gauge Widget class serves as a basic primitive for displaying a value
    in the context of a minimum and maximum value. It may be used in either
    vertical or horizontal mode. It might be used in conjunction with a feed to
    display a variable value changing over time. It might be used to show
    progress to completion of a goal, such as filling out a form or an
    experience bar. It could also be combined with other Gauges to produce a
    histogram chart.

    Owing to the diversity of uses to which the Gauge might be put, this class
    may not be sufficient to your specific needs. A similar or derived class
    may be needed, get in touch if you need help.
    """

    def __init__(self,
                 form,
                 parent,
                 horizontal=True,  # Vertical mode instead if this is False
                 reverse=False,  # H. fills from right, V. fills from bottom
                 min_val=0,
                 max_val=100,
                 theme_by_proportion=True,  # proportional by dynamic range
                 theme_breakpoints=[],  # fractions or hard values, see ^
                 themes=['DEFAULT'],  # should have a length of breakpoints + 1
                 #void_char=' ',
                 fill_char=' ',
                 editable=False,  # A typically non-interacting Widget
                 *args,
                 **kwargs):
        super(Gauge, self).__init__(form,
                                    parent,
                                    editable=editable,
                                    *args,
                                    **kwargs)

        self.horizontal = horizontal
        self.min_val = min_val
        self.max_val = max_val
        self.theme_by_proportion = theme_by_proportion
        self.theme_breakpoints = theme_breakpoints
        self.themes = themes
        self.void_char = void_char
        self.fill_char = fill_char

    def set_up_handlers(self):
        """
        In case the Gauge is editable, the basic set of handlers act as exits.
        """
        self.handlers = {curses.ascii.NL: self.h_exit_down,
                         curses.ascii.CR: self.h_exit_down,
                         curses.ascii.TAB: self.h_exit_down,
                         #curses.KEY_BTAB: self.h_exit_up,
                         curses.KEY_DOWN: self.h_exit_down,
                         curses.KEY_UP: self.h_exit_up,
                         curses.KEY_LEFT: self.h_exit_left,
                         curses.KEY_RIGHT: self.h_exit_right,
                         "^P": self.h_exit_up,
                         "^N": self.h_exit_down,
                         curses.ascii.ESC: self.h_exit_escape,
                         #curses.KEY_MOUSE: self.h_exit_mouse,
                         }
        self.complex_handlers = []

    def pre_edit(self):
        self.highlight = True

    def post_edit(self):
        self.highlight = False

    def get_fill_length(self):
        dynamic_range = float(self.max_val) - float(self.min_val)
        normalized_val = float(self.value) - float(self.min_val)
        if self.horizontal:
            length = self.width
        else:
            length = self.height
        try:
            fill_len = int(math.ceil((normalized_val / dynamic_range) * length))
        except ZeroDivisionError:
            return 0
        if fill_len > length:
            fill_len = length
        return fill_len

    def update(self):
        fill_length = self.get_fill_length()

        if not fill_length:
            return

        self.color = None

        #TODO: handle highlighting properly

        dynamic_range = self.max_val - self.min_val
        #Break points will be interpreted as a fraction of fill_len
        if self.theme_by_proportion:
            for i, point in self.theme_breakpoints:
                if self.value <= dynamic_range * point:
                    self.color = self.themes[i]
            if self.color is None:
                self.color = self.themes[-1]

            if self.horizontal:
                if not self.reverse:
                    self.addstr(self.rely, self.relx,
                                self.fill_char * fill_length)
                else:
                    self.addstr(self.rely, self.relx + self.width - fill_length)
