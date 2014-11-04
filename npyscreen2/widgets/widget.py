# -*- coding: utf-8 -*-

import copy
import sys
import curses
import curses.ascii
import weakref
from .. import global_options as GlobalOptions

from functools import wraps
import locale

from .input_handler import InputHandler
from .line_printer import LinePrinter


import logging
log = logging.getLogger('npyscreen2.widgets.widget')

#What does this offer?
ALLOW_NEW_INPUT = True


__all__ = ['Widget', 'NotEnoughSpaceForWidget']


class NotEnoughSpaceForWidget(Exception):
    pass


class Widget(InputHandler, LinePrinter):

    def __init__(self,
                 form,
                 parent,
                 relx=0,
                 rely=0,
                 value=None,
                 feed=None,
                 width=None,
                 height=None,
                 max_height=None,
                 max_width=None,
                 editable=True,
                 hidden=False,
                 color='DEFAULT',
                 check_value_change=True,
                 check_cursor_move=True,
                 preserve_instantiation_dimensions=True,
                 interested_in_mouse_even_when_not_editable=False,
                 **kwargs):

        try:
            self.form = weakref.proxy(form)
        except TypeError:
            self.form = form

        try:
            self.parent = weakref.proxy(parent)
        except TypeError:
            self.parent = parent

        self.check_value_change = check_value_change
        self.check_cursor_move = check_cursor_move
        self.cursor_position = None
        self.hidden = hidden
        self.editable = editable
        self.value = value
        self._feed = None
        if feed is not None:
            self.feed = feed

        self.preserve_instantiation_dimensions =\
             preserve_instantiation_dimensions

        self.max_height = max_height
        self.max_width = max_width

        self.requested_width = width
        self.width = width

        self.requested_height = height
        self.height = height

        self.relx = relx
        self.rely = rely

        self.color = color

        self.encoding = 'utf-8'
        self.editing = False
        self.interested_in_mouse_even_when_not_editable =\
             interested_in_mouse_even_when_not_editable

        if GlobalOptions.ASCII_ONLY or locale.getpreferredencoding() == 'US-ASCII':
            self._force_ascii = True
        else:
            self._force_ascii = False

        self.set_up_handlers()

    def _resize(self, inpt=None):
        """
        This method will be called when the terminal is resized.

        This is an internal method and should only be modified if one wishes to
        change the fundamental behavior of Widget resizing. If changes
        """
        self.resize()
        #Is there really nothing to do here? It seems like everything is taken
        #care of by the property logic...
        #TODO: If async happens, when_resized should be a candidate
        self.when_resized()

    def resize(self):
        """
        Widgets should override this to control what should happen when they are
        resized.
        """
        pass

    def when_resized(self):
        """
        This method is called after the widget's resizing procedures are
        complete. Override this method if one wishes to add post-resize action.
        """
        pass

    def clear(self, usechar=' '):
        """
        Blank the screen area used by this widget, ready for redrawing
        """
        for y in range(self.rely, self.rely + self.height - 1):
            if self.do_colors():
                self.addstr(y, self.relx, usechar * (self.width),
                            self.form.theme_manager.find_pair(self,
                                                              self.form.color))
            else:
                self.addstr(y, self.relx, usechar * (self.width))

    #How much need is there for updating without clearing first?
    def _update(self, clear=True):
        """
        How should object display itself on the screen. Define here, but do not
        actually refresh the curses display, since this should be done as little
        as possible.  This base widget puts nothing on screen.
        """
        if clear:
            self.clear()
        if self.hidden:
            #self.clear()
            return True

        self.update()

    def update(self):
        """
        Override this method to customize how a Widget updates and represents
        itself on the screen.
        """
        pass

    def display(self, clear=True):
        """
        Do an update of the object AND refresh the screen.
        """
        self._update(clear=clear)
        self.form.refresh()

    def do_colors(self):
        """
        Returns True if the widget should try to paint in coloour.
        """
        if curses.has_colors() and not GlobalOptions.DISABLE_ALL_COLORS:
            return True
        else:
            return False

    def edit(self):
        """
        Allow the user to edit the widget: ie. start handling keypresses.
        """
        log.debug('{0}.edit method called'.format(self.__class__))
        self.editing = True
        self._pre_edit()
        self.edit_loop()
        self._post_edit()

    def pre_edit(self):
        """
        Override this function to add actions to occur prior to the edit loop.
        """
        pass

    def _pre_edit(self):
        self.highlight = True
        self.how_exited = False
        log.debug('{0}._pre_edit method called'.format(self.__class__))

    def post_edit(self):
        """
        Override this function to add actions to occur after the edit loop.
        """
        pass

    def _post_edit(self):
        log.debug('{0}._post_edit method called'.format(self.__class__))
        self.highlight = 0
        self._update()

    def edit_loop(self):
        if not self.parent.editing:
            i_set_parent_editing = True
            self.parent.editing = True
        else:
            i_set_parent_editing = False
        while self.editing and self.parent.editing:
            self.display()
            self.get_and_use_key_press()
        if i_set_parent_editing:
            self.parent.editing = False

        if self.editing:
            self.editing = False
            self.how_exited = True

    def _get_ch(self):
        #try:
        #    # Python3.3 and above - returns unicode
        #    ch = self.form.curses_pad.get_wch()
        #    self._last_get_ch_was_unicode = True
        #except AttributeError:

        #For now, disable all attempts to use get_wch(), but everything that
        #follows could be in the except clause above.

        #Try to read utf-8 if possible.
        _stored_bytes = []
        self._last_get_ch_was_unicode = True
        global ALLOW_NEW_INPUT
        if ALLOW_NEW_INPUT == True and locale.getpreferredencoding() == 'UTF-8':
            ch = self.form.curses_pad.getch()
            if ch <= 127:
                rtn_ch = ch
                self._last_get_ch_was_unicode = False
                return rtn_ch
            elif ch <= 193:
                rtn_ch = ch
                self._last_get_ch_was_unicode = False
                return rtn_ch
            #if we are here, we need to read 1, 2 or 3 more bytes.
            #all of the subsequent bytes should be in the range 128 - 191,
            #but we'll risk not checking...
            elif 194 <= ch <= 223:
                    # 2 bytes
                    _stored_bytes.append(ch)
                    _stored_bytes.append(self.form.curses_pad.getch())
            elif 224 <= ch <= 239:
                    # 3 bytes
                    _stored_bytes.append(ch)
                    _stored_bytes.append(self.form.curses_pad.getch())
                    _stored_bytes.append(self.form.curses_pad.getch())
            elif 240 <= ch <= 244:
                    # 4 bytes
                    _stored_bytes.append(ch)
                    _stored_bytes.append(self.form.curses_pad.getch())
                    _stored_bytes.append(self.form.curses_pad.getch())
                    _stored_bytes.append(self.form.curses_pad.getch())
            elif ch >= 245:
                #probably a control character
                self._last_get_ch_was_unicode = False
                return ch

            if sys.version_info[0] >= 3:
                ch = bytes(_stored_bytes).decode('utf-8', errors='strict')
            else:
                ch = ''.join([chr(b) for b in _stored_bytes])
                ch = ch.decode('utf-8')
        else:
            ch = self.form.curses_pad.getch()
            self._last_get_ch_was_unicode = False

        #This line should not be in the except clause.
        return ch

    def get_and_use_key_press(self):
        curses.raw()
        curses.cbreak()
        curses.meta(1)
        self.form.curses_pad.keypad(1)
        if self.form.keypress_timeout:
            curses.halfdelay(self.form.keypress_timeout)
            ch = self._get_ch()
            if ch == -1:
                log.debug('calling {0}.while_waiting'.format(self.form))
                return self.form.while_waiting()
        else:
            self.form.curses_pad.timeout(-1)
            ch = self._get_ch()
        if ch == curses.ascii.ESC:
            #self.form.curses_pad.timeout(1)
            self.form.curses_pad.nodelay(1)
            ch2 = self.form.curses_pad.getch()
            if ch2 != -1:
                ch = curses.ascii.alt(ch2)
            self.form.curses_pad.timeout(-1)  # back to blocking mode
            #curses.flushinp()

        self.handle_input(ch)
        if self.check_value_change:
            self.when_check_value_changed()
        if self.check_cursor_move:
            self.when_check_cursor_moved()

    def interested_in_mouse_event(self, mouse_event):
        if not self.editable and not self.interested_in_mouse_even_when_not_editable:
            return False
        mouse_id, x, y, z, bstate = mouse_event
        x += self.form.show_from_x
        y += self.form.show_from_y
        if self.relx <= x <= self.relx + self.width-1 + self.form.show_atx:
            if self.rely  <= y <= self.rely + self.height-1 + self.form.show_aty:
                return True
        return False

    def handle_mouse_event(self, mouse_event):
        # mouse_id, x, y, z, bstate = mouse_event
        pass

    def interpret_mouse_event(self, mouse_event):
        mouse_id, x, y, z, bstate = mouse_event
        x += self.form.show_from_x
        y += self.form.show_from_y
        rel_y = y - self.rely - self.form.show_aty
        rel_x = x - self.relx - self.form.show_atx
        return (mouse_id, rel_x, rel_y, z, bstate)

    def when_check_value_changed(self):
        """
        Check whether the widget's value has changed and call
        when_valued_edited if so.
        """
        try:
            if self.value == self._old_value:
                return False
        except AttributeError:
            self._old_value = copy.deepcopy(self.value)
            self.when_value_edited()
        #Value must have changed:
        self._old_value = copy.deepcopy(self.value)
        self.when_value_edited()
        if hasattr(self, 'parent_widget'):
            self.parent_widget.when_value_edited()
        return True

    def when_value_edited(self):
        """
        Called when the user edits the value of the widget. Will usually also be
        called the first time that the user edits the widget.
        """
        pass

    def when_check_cursor_moved(self):
        cursor = self.cursor_position
        #if hasattr(self, 'cursor_line'):
            #cursor = self.cursor_line
        #elif hasattr(self, 'cursor_position'):
            #cursor = self.cursor_position
        #elif hasattr(self, 'edit_cell'):
            #cursor = copy.copy(self.edit_cell)
        #else:
            #return None
        try:
            if self._old_cursor == cursor:
                return False
        except AttributeError:
            pass
        #Value must have changed:
        self._old_cursor = cursor
        self.when_cursor_moved()
        self.parent.when_check_cursor_moved()

    def when_cursor_moved(self):
        """
        Called when the cursor moves.
        """
        pass

    @property
    def feed(self):
        """
        The method for updating the LiveWidget's value. Customize your widget by
        setting this to a function that returns the desired value from a live
        data source.
        """
        def _feed_wrapper(f):
            @wraps(f)
            def wrapper(*args, **kwds):
                self.value = f(*args, **kwds)
            return wrapper
        return _feed_wrapper(self._feed)

    @feed.setter
    def feed(self, func):
        if not callable(func):
            raise ValueError('LiveWidget.feed must be assigned a callable')
        self._feed = func

#Let's discuss dimension and position policy for Widgets and, by extension,
#Containers; I'll simply refer to both as Widgets in the following text.
#
#  A well-behaved Widget will not modify its own rely/relx attributes, this is
#  the job of its parent Container or Form.
#
#  A well-behaved Widget will not modify its own max_height/max_width
#  attributes, this is also the job of its parent Container or Form.
#
#  A Widget is free to modify its own height/width attributes, and it shall not
#  expect these values to be modified by its parent Container or Form. When a
#  resize event occurs the parent should alter the max_height/max_width of its
#  children and the Widget should adjust height/width according in its own
#  resize method.
#
#  A Widget may be instantiated with height/width values which it will retain
#  in the attributes requested_height/requested_width. These values should not
#  be modified post-instantiation by either the Widget or its parent Container
#  or Form. If the Widget keyword argument preserve_instantiation_dimensions is
#  set to True, then the Widget will report height/width according to
#  requested_height/requested_width (unless trumped by max_height/max_width,
#  refer below).
#
#  A Widget's height/width attributes will not report a value greater than
#  max_height/max_width.

    def inflate(self):
        """
        A convenient method for setting `height` and `width` to `max_height` and
        `max_width` respectively. It does nothing else; often useful in the
        `resize` method of Widgets meant to fill their allocated space.

        It does not respect self.preserve_instantiation_dimensions, so only call
        it when appropriate.
        """
        self.height = self.max_height
        self.width = self.max_width

    #TODO: Determine if it is necessary to enforce size checks before updates
    #It may be that resizing while widgets are being edited could cause trouble
    @property
    def max_height(self):
        return self._max_height

    @max_height.setter
    def max_height(self, val):
        """
        max_height should never be allowed to extend past the available screen
        area.
        """
        if val is None:
            val = 0
        self._max_height = val

    @property
    def max_width(self):
        return self._max_width

    @max_width.setter
    def max_width(self, val):
        """
        max_width should never be allowed to extend past the available screen
        area.
        """
        if val is None:
            val = 0
        self._max_width = val

    @property
    def height(self):
        """
        If self.preserve_instantiation_dimensions is True, this property will
        check if the Widget was instantiated with dimensions, requested_height,
        and use that value instead of _height.

        If max_height is lesser than the effective height value, then max_height
        will be returned instead.
        """
        if self.preserve_instantiation_dimensions and self.requested_height is not None:
            h = self.requested_height
        else:
            h = self._height
        if h > self.max_height:
            return self.max_height
        else:
            return h

    @height.setter
    def height(self, val):
        if val is None:
            val = 0
        self._height = val

    @property
    def width(self):
        """
        If self.preserve_instantiation_dimensions is True, this property will
        check if the Widget was instantiated with dimensions, requested_width,
        and use that value instead of _width.

        If max_width is lesser than the effective width value, then max_width
        will be returned instead.
        """
        if self.preserve_instantiation_dimensions and self.requested_width is not None:
            w = self.requested_width
        else:
            w = self._width
        if w > self.max_width:
            return self.max_width
        else:
            return w

    @width.setter
    def width(self, val):
        if val is None:
            val = 0
        self._width = val

    def is_form(self):
        """
        Am I a Form?
        """
        return False

    def parent_borders(self, margins=True):
        #parent_y_top
        p_y_t = self.parent.rely
        #parent_y_bottom
        p_y_b = self.parent.rely + self.parent.height - 1
        #parent_x_left
        p_x_l = self.parent.relx
        #parent_x_right
        p_x_r = self.parent.relx + self.parent.width - 1
        #These are index values
        return p_y_t, p_y_b, p_x_l, p_x_r

    def addch(self, y, x, ch, attr=None):
        """
        Paint character ch at (y, x) with attributes attr, overwriting any
        character previously painted at that location. If attr is not used, then
        it will use the current default for the curses pad.

        Note: A character means a C character (an ASCII code), rather than a
        Python character (a string of length 1). (This note is true whenever the
        documentation mentions a character.) The built-in ord() is handy for
        conveying strings to codes.
        """
        #Do nothing if either of the indices are outside the parent borders
        p_y_t, p_y_b, p_x_l, p_x_r = self.parent_borders()
        log.debug('addch called: y={}, x={}, ch={}'.format(y, x, ch))
        log.debug('p_y_t={}, p_y_b={}, p_x_l={}, p_x_r={}'.format(p_y_t, p_y_b, p_x_l, p_x_r))
        if y < p_y_t or y > p_y_b:
            return False
        elif x < p_x_l or x > p_x_r:
            return False
        #try:
        if attr is None:
            if sys.version_info[:3] == (3, 4, 0):
                self.form.curses_pad.addch(x, y, ch)
            else:
                self.form.curses_pad.addch(y, x, ch)
        else:
            if sys.version_info[:3] == (3, 4, 0):
                self.form.curses_pad.addch(x, y, ch, attr)
            else:
                self.form.curses_pad.addch(y, x, ch, attr)
        #except curses.error:
            #log.warning('addch failed! y={}, x={}, ch={} attr={}'.format(y, x, ch, attr))

    def addstr(self, y, x, string, attr=None):
        """
        Paint the string string at (y, x) with attributes attr, overwriting
        anything previously on the display.
        """

        p_y_t, p_y_b, p_x_l, p_x_r = self.parent_borders()
        if y < p_y_t or y > p_y_b:
            return False

        #try:
        if attr is None:
            self.form.curses_pad.addstr(y, x, string[:self.max_width])
        else:
            self.form.curses_pad.addstr(y, x, string[:self.max_width], attr)
        #except curses.error:
            #log.warning('addstr failed! y={}, x={}, string={}, attr={}'.format(y, x, string, attr))
            #log.warning('self.max_height={} self.max_width={}'.format(self.max_height, self.max_width))

    #def addnstr(self, y, x, string, n, attr=None):
        #"""
        #Paint at most n characters of the string str at (y, x) with attributes
        #attr, overwriting anything previously on the display.
        #"""
        #if attr is None:
            #self.form.curses_pad.addstr(y, x, string, n)
        #else:
            #self.form.curses_pad.addstr(y, x, string, n, attr)

    def hline(self, y, x, ch, n):
        #if n == 0:
            #return False
        try:
            self.form.curses_pad.hline(y, x, ch, n)
        except curses.error:
            pass

    def vline(self, y, x, ch, n):
        #if n == 0:
            #return False
        try:
            self.form.curses_pad.vline(y, x, ch, n)
        except curses.error:
            pass