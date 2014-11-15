# -*- coding: utf-8 -*-

from . import Widget

import curses

import logging
log = logging.getLogger('npyscreen2.widgets.borderbox')


class BorderBox(Widget):
    """
    """
    def __init__(self,
                 form,
                 parent,
                 top=True,
                 bottom=True,
                 left=True,
                 right=True,
                 editable=False,
                 use_margins=False,
                 *args, **kwargs):
        super(BorderBox, self).__init__(form,
                                        parent,
                                        editable=editable,
                                        *args,
                                        **kwargs)
        self._top = top
        self._bottom = bottom
        self._left = left
        self._right = right
        self._use_margins = use_margins

    def clear(self, usechar=' '):
        """
        Blank the screen area used by this widget, ready for redrawing
        """
        self.print_borders(blank=True)

    def pre_edit(self):
        self.highlight = True

    def post_edit(self):
        self.highlight = False

    def update(self):
        self.print_borders()

    def print_borders(self, blank=False):
        if blank:
            hbar_char = ' '
            vbar_char = ' '
            ul_c_char = ' '
            ur_c_char = ' '
            ll_c_char = ' '
            lr_c_char = ' '
        else:
            hbar_char = curses.ACS_HLINE
            vbar_char = curses.ACS_VLINE
            ul_c_char = curses.ACS_ULCORNER
            ur_c_char = curses.ACS_URCORNER
            ll_c_char = curses.ACS_LLCORNER
            lr_c_char = curses.ACS_LRCORNER

        vbar_length = self.height
        hbar_length = self.width
        ul_y, ul_x = self.rely, self.relx

        #Draw the bars
        if self._top:
            self.hline(ul_y, ul_x, hbar_char, hbar_length)
        if self._bottom:
            self.hline(ul_y + self.height - 1, ul_x, hbar_char, hbar_length)
        if self._left:
            self.vline(ul_y, ul_x, vbar_char, vbar_length)
        if self._right:
            self.vline(ul_y, ul_x + self.width - 1, vbar_char, vbar_length)

        #Draw the corners
        if self._top and self._left:
            self.addch(ul_y, ul_x, ul_c_char)
        if self._top and self._right:
            self.addch(ul_y, ul_x + self.width - 1, ur_c_char)
        if self._bottom and self._left:
            self.addch(ul_y + self.height - 1, ul_x, ll_c_char)
        if self._bottom and self._right:
            self.addch(ul_y + self.height - 1, ul_x + self.width - 1, lr_c_char)