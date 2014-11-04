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
                 bold=False,
                 underline=False,
                 standout=True,
                 reverse=False,
                 show_cursor=False,
                 #wrap_lines=False,  # Line wrapping is a nightmare for later
                 start_cursor_at_end=True,
                 highlight_color='CURSOR',
                 highlight_whole_widget=False,
                 *args,
                 **kwargs):
        super(TextField, self).__init__(form,
                                        parent,
                                        value=value,
                                        *args,
                                        **kwargs)

        #Matches a line break
        #self.re_line_break = re.compile('\\r?\\n|\\r')

        #self.wrap_lines = wrap_lines
        self.highlight_color = highlight_color
        self.highlight_whole_widget = highlight_whole_widget

        #Cursor position refers to (lines, columns)
        self.cursor_position = 0

        #These correspond to curses character cell attributes that will be
        #applied to the text display by this widget
        self.bold = bold
        self.underline = underline
        self.standout = standout
        self.reverse = reverse

        self.begin_at = 0

        self.update()

    #def update_values(self):
        #"""
        #This method updates the `values` attribute of TextField.

        #`values` should at all times be a generator function operating on the
        #`value`
        #"""
        #def values_generator():
            #index = 0
            #while True:
                #m = self.re_line_break.search(self.value[index:])
                #if m is None:
                    #yield self.value[index:]
                    #break
                #old_index, index = index, index + m.span()[1]
                #yield self.value[old_index: old_index + m.span()[0]]
        #self.values = values_generator()

    #def lines_to_display_value(self):
        #"""
        #This method returns the number of lines it should take to display the
        #text of self.value
        #"""
        ##Couldn't find a good tool for this, rolling my own
        #lines = 1
        #index = 0
        #while True:
            #m = self.re_line_break.search(self.value[index:])
            #if m is None:
                #break
            #old_index, index = index, index + m.span()[1]
            ##line = text[old_index: old_index + m.span()[0]]
            ##TODO: implement line wrapping
            #lines += 1

        #return lines

    def printable_value(self):
        return self.value[self.begin_at:][:self.max_width]

    def update(self):
        if self.begin_at < 0:
            self.begin_at = 0

        if self.bold:
            self.form.curses_pad.attron(curses.A_BOLD)
        if self.underline:
            self.form.curses_pad.attron(curses.A_UNDERLINE)
        if self.standout:
            self.form.curses_pad.attron(curses.A_STANDOUT)
        if self.reverse:
            self.form.curses_pad.attron(curses.A_REVERSE)

        self.addstr(self.rely, self.relx, self.printable_value())

        self.form.curses_pad.attron(curses.A_BOLD)
        self.form.curses_pad.attron(curses.A_UNDERLINE)
        self.form.curses_pad.attron(curses.A_STANDOUT)
        self.form.curses_pad.attron(curses.A_REVERSE)
        self.form.curses_pad.bkgdset(' ', curses.A_NORMAL)
        self.form.curses_pad.attrset(0)
        if self.editing:
            pass
            #self.print_cursor()
        #for i, line in enumerate(self.values):
            #safe_line = self.safe_string(line)
            #if line == '':
                #safe_line = '----'
            #self.addstr(self.rely + i, self.relx, safe_line)

