# -*- coding: utf-8 -*-

import curses

from . import Widget

import logging
log = logging.getLogger('npyscreen2.widgets.textfield')


class TextField(Widget):
    """
    The TextField class will most likely serve as the general basis for most
    widgets that display text to the screen. The value attribute should always
    be a string.

    A TextField intended to be static (display text only and not interact with
    the user), should be instantiated with `editable=False`.
    """

    def __init__(self,
                 form,
                 parent,
                 value='',
                 show_cursor=False,
                 cursor_bold=False,
                 cursor_color='CURSOR',
                 cursor_highlight_color='CURSOR_HIGHLIGHT',
                 cursor_underline=False,
                 cursor_empty_character=' ',
                 runoff_left=':',
                 runoff_right=':',
                 #wrap_lines=False,  # Line wrapping is a nightmare for later
                 start_cursor_at_end=True,
                 highlight_whole_widget=False,  # not used yet
                 *args,
                 **kwargs):

        super(TextField, self).__init__(form,
                                        parent,
                                        value=value,
                                        *args,
                                        **kwargs)

        self.runoff_left = runoff_left
        self.runoff_right = runoff_right

        self.highlight_whole_widget = highlight_whole_widget  # not used yet

        self.cursor_bold = cursor_bold
        self.cursor_color = cursor_color
        self.cursor_highlight_color = cursor_highlight_color
        self.cursor_underline = cursor_underline
        self.cursor_empty_character = cursor_empty_character

        self._begin_at = 0

        self.update()

    def set_up_handlers(self):
            super(TextField, self).set_up_handlers()

            #For OS X
            #del_key = curses.ascii.alt('~')

            self.handlers.update({curses.KEY_LEFT: self.h_cursor_left,
                                  curses.KEY_RIGHT: self.h_cursor_right,
                                  curses.KEY_DC: self.h_delete_right,
                                  curses.ascii.DEL: self.h_delete_left,
                                  curses.ascii.BS: self.h_delete_left,
                                  curses.KEY_BACKSPACE: self.h_delete_left,
                                  curses.KEY_HOME: self.h_home,
                                  curses.KEY_END: self.h_end,
                                  curses.ascii.NL: self.h_exit_down,
                                  curses.ascii.CR: self.h_exit_down,
                                  curses.ascii.TAB: self.h_exit_down,
                                  #mac os x curses reports DEL as escape oddly
                                  #no solution yet
                                  "^K": self.h_erase_right,
                                  "^U": self.h_erase_left,
                                  })

            self.complex_handlers.extend((
                            (self.t_input_isprint, self.h_addch),
                            # (self.t_is_ck, self.h_erase_right),
                            # (self.t_is_cu, self.h_erase_left),
                            ))

    def _pre_edit(self):
        super(TextField, self)._pre_edit()
        #self.bold = True
        #Explicitly setting the behavior for an unset cursor_position
        if self.cursor_position is None:
            self.cursor_position = len(self.value)

    def _post_edit(self):
        super(TextField, self)._post_edit()
        #self.bold = False
        #Cause the widget to forget where the cursor was, and reset the begin
        self.cursor_position = None
        self.begin_at = 0

    def printable_value(self):
        if self.editable:
            max_string_length = self.max_width - 1
        else:
            max_string_length = self.max_width
        val = self.value[self.begin_at:]
        if len(val) > max_string_length:
            val = val[:max_string_length] + self.runoff_right
        return val
        #return self.value[self.begin_at:][:max_string_length]

    def resize(self):
        self.height = 1
        self.width = self.max_width

    def update(self):
        if self.cursor_position is not None:
            if self.cursor_position < self.begin_at:
                self.begin_at = self.cursor_position
            while self.cursor_position > self.begin_at + self.max_width - 1:
                self.begin_at += 1

        self.addstr(self.rely, self.relx, self.printable_value())

        if self.editing:
            self.print_cursor()

        if self.begin_at > 0:
            self.addch(self.rely, self.relx, self.runoff_left)

    def print_cursor(self):
        # This needs fixing for Unicode multi-width chars.

        # Cursors do not seem to work on pads.
        #self.parent.curses_pad.move(self.rely, self.cursor_position - self.begin_at)
        # let's have a fake cursor
        #_cur_loc_x = self.cursor_position - self.begin_at + self.relx
        # The following two lines work fine for ascii, but not for unicode
        #char_under_cur = self.parent.curses_pad.inch(self.rely, _cur_loc_x)
        #self.parent.curses_pad.addch(self.rely, self.cursor_position - self.begin_at + self.relx, char_under_cur, curses.A_STANDOUT)
        #The following appears to work for unicode as well.
        try:
            char_under_cur = self.value[self.cursor_position]
        except IndexError:
            char_under_cur = self.cursor_empty_character

        attr = 0
        if self.cursor_bold:
            attr |= curses.A_BOLD
        if self.cursor_underline:
            attr |= curses.A_UNDERLINE

        if self.do_colors():
            if self.highlight:
                attr |= self.form.theme_manager.find_pair(self, self.cursor_highlight_color)
            else:
                attr |= self.form.theme_manager.find_pair(self,
                                                          self.cursor_color)
        else:
            attr |= curses.A_REVERSE

        self.addstr(self.rely,
                    self.relx + self.cursor_position - self.begin_at,
                    char_under_cur,
                    attr)


    def h_addch(self, inpt):
        if self.editable:
            #self.value = self.value[:self.cursor_position] + curses.keyname(input) \
            #   + self.value[self.cursor_position:]
            #self.cursor_position += len(curses.keyname(input))

            #workaround for the metamode bug:
            if self._last_get_ch_was_unicode == True and isinstance(self.value, bytes):
                #probably dealing with python2.
                #note: I am pretty much assuming npyscreen2 will be python3 only
                ch_adding = inpt
                self.value = self.value.decode()
            elif self._last_get_ch_was_unicode == True:
                ch_adding = inpt
            else:
                try:
                    ch_adding = chr(inpt)
                except TypeError:
                    ch_adding = input
            self.value = self.value[:self.cursor_position] + ch_adding \
                + self.value[self.cursor_position:]
            self.cursor_position += len(ch_adding)

            # or avoid it entirely:
            #self.value = self.value[:self.cursor_position] + curses.ascii.unctrl(input) \
            #   + self.value[self.cursor_position:]
            #self.cursor_position += len(curses.ascii.unctrl(input))

    def h_cursor_left(self, inpt):
        self.cursor_position -= 1

    def h_cursor_right(self, inpt):
        self.cursor_position += 1

    def h_delete_left(self, inpt):
        if self.editable and self.cursor_position > 0:
            self.value = self.value[:self.cursor_position - 1] + \
                         self.value[self.cursor_position:]
        self.cursor_position -= 1
        self.begin_at -= 1
        self.display()

    def h_delete_right(self, inpt):
        if self.editable:
            self.value = self.value[:self.cursor_position] + \
                         self.value[self.cursor_position + 1:]
        self.display()

    def h_erase_left(self, inpt):
        if self.editable:
            self.value = self.value[self.cursor_position:]
            self.cursor_position = 0

    def h_erase_right(self, inpt):
        if self.editable:
            self.value = self.value[:self.cursor_position]
            self.cursor_position = len(self.value)
            self.begin_at = 0

    def h_home(self, inpt):
        self.cursor_position = 0

    def h_end(self, inpt):
        self.cursor_position = len(self.value)

    def t_input_isprint(self, inpt):
        """
        An example of a complex handler; returns True if the most recently
        gotten character input is a printable unicode character.
        """
        if self._last_get_ch_was_unicode and inpt not in '\n\t\r':
            return True
        if curses.ascii.isprint(inpt) and \
           (chr(inpt) not in '\n\t\r'):
            return True
        else:
            return False

    def handle_mouse_event(self, mouse_event):
        #mouse_id, x, y, z, bstate = mouse_event
        #rel_mouse_x = x - self.relx - self.parent.show_atx
        mouse_id, rel_x, rel_y, z, bstate = self.interpret_mouse_event(mouse_event)
        self.cursor_position = rel_x + self.begin_at
        self.display()

    @property
    def begin_at(self):
        return self._begin_at

    @begin_at.setter
    def begin_at(self, val):
        if val < 0:
            val = 0
        self._begin_at = val