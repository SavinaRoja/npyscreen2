# -*- coding: utf-8 -*-

"""
"""

from . import Container

#import curses

import logging
log = logging.getLogger('npyscreen2.containers.smartcontainer')

__all__ = ['SmartContainer']


class SmartContainer(Container):
    """
    The SmartContainer will have the ability to use various rectangle packing
    algorithms to dynamically arrange widgets (as they may be added or removed)
    and possibly minimize empty space.

    The scheme attribute controls which packing algorithm the SmartContainer
    will use.

    The following schemes are available:
        ffdh-top  :  First-Fit Decreasing Height (from the top)
        ffdh-bottom  :  First-Fit Decreasing Height (from the bottom)

    As a general rule, this Container treats the sizes of the contained widgets
    as static (or independent) and does not control or adjust their sizes. It
    will do its best to arrange their locations so that they fit on the screen
    without changing the dimensions.
    """

    def __init__(self,
                 form,
                 parent,
                 scheme='ffdh-top',
                 hide_partially_visible=True,
                 *args,
                 **kwargs):

        self.scheme_map = {'ffdh-top': self.ffdh_top,
                           'ffdh-bottom': self.ffdh_bottom,
                           }
        self.scheme = scheme
        log.debug('SmartContainer.scheme is {}'.format(self.scheme))

        super(SmartContainer, self).__init__(form,
                                             parent,
                                             hide_partially_visible=hide_partially_visible,
                                             *args,
                                             **kwargs)

    def add_widget(self, *args, **kwargs):

        w = super(SmartContainer, self).add_widget(*args, **kwargs)

        self.resize()
        return w

    def resize(self):
        self.rearrange_widgets()

    def rearrange_widgets(self):
        self.scheme_map[self.scheme]()

    def ffdh_top(self):
        #Re-ordering self.contained by descending height
        self.contained.sort(key=lambda widget: widget.height, reverse=True)

        start_y = self.rely + self.top_margin
        end_y = self.rely + self.height - self.bottom_margin
        start_x = self.relx + self.left_margin
        end_x = self.relx + self.width - self.right_margin
        width = end_x - start_x

        levels = [start_y]
        level_x = {start_y: 0}

        for widget in self.autoables:
            for level in levels:
                if level + widget.height >= end_y:
                    widget.hidden = True
                    widget.relx = self.relx
                    widget.rely = self.rely
                    break
                widget.hidden = False
                x_cur = level_x[level]
                if widget.width <= width - x_cur:
                    widget.rely = level
                    widget.relx = x_cur + start_x
                    if x_cur == 0:
                        new_level = level + widget.height
                        levels.append(new_level)
                        level_x[new_level] = 0
                    level_x[level] += widget.width
                    break

    def ffdh_bottom(self):
        #Re-ordering self.contained by descending height
        self.contained.sort(key=lambda widget: widget.height, reverse=True)

        start_y = self.rely + self.height - self.bottom_margin
        end_y = self.rely + self.top_margin
        start_x = self.relx + self.left_margin
        end_x = self.relx + self.width - self.right_margin
        width = end_x - start_x

        levels = [start_y]
        level_x = {start_y: 0}

        for widget in self.autoables:
            for level in levels:
                if level - widget.height <= end_y:
                    widget.hidden = True
                    widget.relx = self.relx - 1
                    widget.rely = self.rely - 1
                    break
                widget.hidden = False
                x_cur = level_x[level]
                if widget.width <= width - x_cur:
                    widget.rely = level - widget.height
                    widget.relx = x_cur + start_x
                    if x_cur == 0:
                        new_level = level - widget.height
                        levels.append(new_level)
                        level_x[new_level] = 0
                    level_x[level] += widget.width
                    break

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, val):
        if val.lower() in self.scheme_map.keys():
            self._scheme = val
        else:
            raise ValueError('{} not in {}'.format(val, self.scheme_map.keys()))
