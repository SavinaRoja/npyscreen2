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
                                        editable=editable
                                        *args,
                                        **kwargs)
        self._top = top
        self._bottom = bottom
        self._left = left
        self._right = right
        self._use_margins = use_margins

        log.debug('''BorderBox initiatied with: top={0}, bottom={1}, left={2}, \
right={3}, use_margins={4}'''.format(top, bottom, left, right, use_margins))

    def resize(self):
        if not self.preserve_instantiation_dimensions:
            self.inflate()  # Expand to available max dimensions
        log.debug('''BorderBox: rely={0}, relx={1}, height={2}, width={3}, \
max_height={4}, max_width={5}'''.format(self.rely, self.relx, self.height,
                                        self.width, self.max_height,
                                        self.max_width))

    def update(self):
        vbar_length = self.height
        hbar_length = self.width
        ul_y, ul_x = self.rely, self.relx
        if self._use_margins:
            hbar_length -= (self.left_margin + self.right_margin)
            vbar_length -= (self.top_margin + self.bottom_margin)
            ul_y += self.top_margin
            ul_x += self.left_margin
        #Draw the bars
        if self._top:
            self.hline(ul_y, ul_x,
                       curses.ACS_HLINE, hbar_length)
        if self._bottom:
            self.hline(ul_y + self.height - 1, ul_x,
                       curses.ACS_HLINE, hbar_length)
        if self._left:
            self.vline(ul_y, ul_x,
                       curses.ACS_VLINE, vbar_length)
        if self._right:
            self.vline(ul_y, ul_x + self.width - 1,
                       curses.ACS_VLINE, vbar_length)

        #Draw the corners
        if self._top and self._left:
            self.addch(ul_y, ul_x,
                       curses.ACS_ULCORNER)
        if self._top and self._right:
            self.addch(ul_y, ul_x + self.width - 1,
                       curses.ACS_URCORNER)
        if self._bottom and self._left:
            self.addch(ul_y + self.height - 1, ul_x,
                       curses.ACS_LLCORNER)
        if self._bottom and self._right:
            self.addch(ul_y + self.height - 1, ul_x + self.width - 1,
                       curses.ACS_LRCORNER)
