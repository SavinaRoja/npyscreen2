# -*- coding: utf-8 -*-

import curses
from functools import wraps


import logging
log = logging.getLogger('npyscreen2.widgets.input_handler')

__all__ = ['exit_edit_method', 'InputHandler']


def exit_edit_method(func):
    """
    This functions serves as a decorator for Widget methods intended to end the
    edit loop of the widget.

    Currently, this function automates the setting of the `Widget.editing`
    attribute to False, as well as setting `Widget.how_exited` to whatever
    value is returned by the method function.

    A good method may do whatever it likes, so long as it returns a good value
    for `self.how_exited`.
    """
    @wraps(func)
    def wrapper(self, inpt=None):
        self.editing = False
        self.how_exited = func(self, inpt)
    return wrapper


class InputHandler(object):
    """
    An object that can handle user input
    """

    def handle_input(self, inpt):
        """
        Returns True if input has been dealt with, and no further action needs
        taking.

        First attempts to look up a method in self.input_handers (which is a
        dictionary), then runs the methods in self.complex_handlers (if any),
        which is an array of form (test_func, dispatch_func).

        If test_func(input) returns true, then dispatch_func(input) is called.
        Check to see if parent can handle. No further action taken after that
        point.
        """
        log.debug('handle_input called on inpt={0}'.format(inpt))

        if inpt in self.handlers:
            log.debug('inpt in handlers, calling method {0}'.format(self.handlers[inpt]))
            self.handlers[inpt](inpt)
            return True

        try:
            unctrl_inpt = curses.ascii.unctrl(inpt)
        except TypeError:
            unctrl_inpt = None
        else:
            log.debug('unctrl_inpt={0}'.format(unctrl_inpt))

        if unctrl_inpt and (unctrl_inpt in self.handlers):
            self.handlers[unctrl_inpt](inpt)
            return True

        #When would this ever be False? complex_handlers is created during
        #Widget instantiation
        for test, handler in self.complex_handlers:
            if test(inpt) is not False:
                handler(inpt)
                return True
        #if not hasattr(self, 'complex_handlers'):
            #return False
        #else:
            #for test, handler in self.complex_handlers:
                #if test(inpt) is not False:
                    #handler(inpt)
                    #return True

        #This recursion should be able to travel from a Widget up to the Form
        #and then end
        if not self.is_form():
            #If the current Widget is not a form, then recurse to parent
            if self.parent.handle_input(inpt):
                return True

        #Everything has failed
        return False

    def set_up_handlers(self):
        """
        This function should be called somewhere during object initialisation
        (which all library-defined widgets do). You might like to override this
        in your own definition, but in most cases the `add_handlers` or
        `add_complex_handlers` methods are what you want.
        """
        self.handlers = {curses.ascii.NL: self.h_exit_down,
                         curses.ascii.CR: self.h_exit_down,
                         #curses.ascii.TAB: self.h_exit_down,
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

    def add_handlers(self, handler_dictionary):
        """
        Update the dictionary of simple handlers.  Pass in a dictionary with
        keyname (eg "^P" or curses.KEY_DOWN) as the key, and the function that
        key should call as the values
        """
        self.handlers.update(handler_dictionary)

    def add_complex_handlers(self, handlers_list):
        """
        add complex handlers: format of the list is pairs of
        (test_function, callback) sets
        """

        for pair in handlers_list:
            assert len(pair) == 2
        self.complex_handlers.extend(handlers_list)

    def remove_complex_handler(self, test_function):
        _new_list = []
        for pair in self.complex_handlers:
            if not pair[0] == test_function:
                _new_list.append(pair)
        self.complex_handlers = _new_list

### Handler methods ###
#Prefix of "h_" is just a convention for readability
#Handler methods must be registered to be used, see set_up_handlers; these are
#mapped to specified input values and called from handle_input. Each handler
#method should accept an input value as an argument, whether or not it is going
#to use it.

#See exit_edit_method in this module for more details. In brief, these are
#handlers intended to break the edit loop, setting self.editing=False and
#self.how_exited to a string indicating the condition of exit. To define such
#a method, any action may be taken, so long as the self.how_exited value is
#returned

    @exit_edit_method
    def h_exit_down(self, inpt=None):
        return 'down'

    @exit_edit_method
    def h_exit_right(self, inpt=None):
        return 'right'

    @exit_edit_method
    def h_exit_up(self, inpt=None):
        return 'up'

    @exit_edit_method
    def h_exit_left(self, inpt=None):
        return 'left'

    @exit_edit_method
    def h_exit_escape(self, inpt=None):
        return 'escape'

    @exit_edit_method
    def h_exit_ascend(self, inpt=None):
        return 'ascend'

    @exit_edit_method
    def h_exit_descend(self, inpt=None):
        return 'descend'

    #@exit_edit_method
    #Since this method does not quite fit the standard exit model, the decorator
    #is not appropriate. I should consider if this appropriately named
    def h_exit_mouse(self, inpt=None):
        mouse_event = self.parent.safe_get_mouse_event()
        if mouse_event and self.interested_in_mouse_event(mouse_event):
            self.handle_mouse_event(mouse_event)
        else:
            if mouse_event:
                curses.ungetmouse(*mouse_event)
                ch = self.parent.curses_pad.getch()
                assert ch == curses.KEY_MOUSE
            self.editing = False
            self.how_exited = 'mouse'
