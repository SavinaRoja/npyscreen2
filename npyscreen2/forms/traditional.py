# -*- coding: utf-8 -*-
"""
The aim of this module is to replicate the traditional form styles from
npyscreen. They may also serve as references for designing new forms.
"""

from . import Form
from ..widgets import BorderBox

import logging
log = logging.getLogger('npyscreen2.forms.traditional')


class TraditionalForm(Form):
    """
    This class emulates the traditional Forms from npyscreen by possessing the
    following traits:
     * Newly added widgets through add_widget are added in a vertical stack
     * An uneditable Title widget may be placed at the top of the screen
     * An uneditable Footer widget may be placed on the bottom of the screen
     * A Button is placed in the bottom right corner of the Form
     * The Form has the following border options: framed, top_bar, bottom_bar

    To mimic different resizing modes, refer to the mega-comment in the base
    Form class for discussion of options.
    """
    def __init__(self,
                 framed=False,  # Trumps top_bar and bottom_bar
                 top_bar=False,
                 bottom_bar=False,
                 top_margin=1,
                 right_margin=2,
                 left_margin=2,
                 bottom_margin=1,
                 *args,
                 **kwargs):
        super(TraditionalForm, self).__init__(right_margin=right_margin,
                                              bottom_margin=bottom_margin,
                                              top_margin=top_margin,
                                              left_margin=left_margin,
                                              *args,
                                              **kwargs)

        if framed:
            self._top_bar = True
            self._bottom_bar = True
            self._left_bar = True
            self._right_bar = True
        else:
            self._top_bar = top_bar
            self._bottom_bar = bottom_bar
            self._left_bar = False
            self._right_bar = False

        self._latest_rely = self.rely + self.top_margin
        self._latest_relx = self.relx + self.left_margin

        self.border = BorderBox(self,
                                self,
                                rely=0,
                                relx=0,
                                preserve_instantiation_dimensions=False,
                                top=self._top_bar,
                                bottom=self._bottom_bar,
                                left=self._left_bar,
                                right=self._right_bar,
                                max_height=self.max_height,
                                max_width=self.max_width,
                                height=self.max_height,
                                width=self.max_width)

    def next_rely_relx(self):
        try:
            last_widget = self.contained[-1]
        except IndexError:
            return self._latest_rely, self._latest_relx
        else:
            self._latest_rely += last_widget.height
            return self._latest_rely, self._latest_relx

    def resize(self):
        self.border.max_height = self.max_height
        self.border.max_width = self.max_width
        self.border.resize()

    def update(self):
        self.border._update()
