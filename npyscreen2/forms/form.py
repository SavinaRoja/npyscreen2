# -*- coding: utf-8 -*-

import curses
import curses.panel
import struct
import sys
import termios
import weakref

from .. import global_options
from .. import pmfuncs
from .. import theme_managers

from ..containers import Container

#For more complex method of getting the size of screen
try:
    import fcntl
except ImportError:
    # Win32 platforms do not have fcntl
    pass

import logging
log = logging.getLogger('npyscreen2.forms.form')


APPLICATION_THEME_MANAGER = None

__all__ = ['Form', 'get_theme', 'set_theme']


def set_theme(theme):
    global APPLICATION_THEME_MANAGER
    APPLICATION_THEME_MANAGER = theme()


def get_theme():
    return APPLICATION_THEME_MANAGER


class Form(Container):
    """
    The Form class is an extension of the Container class (which is in turn an
    extension of the Widget class). An application may use more than one Form,
    but only one Form will be active at any given time and serves as the root
    Container of the application and should consume the entirety of the terminal
    window.

    Though it might be technically possible to nest Forms within Forms, just as
    Containers may nest in Containers, this is not supported.

    The primary distinguishing characteristic between Forms and Containers is
    that Forms possess screen management functions and special traits befitting
    their special status as root Widget and loop object.
    """

    #A Form's dimensions are not constrained to the physical size of the screen,
    #though the default (so long as max_height/width are not used during
    #instantiation) mode is such. If the dimensions are specified, then the
    #max dimensions will not be automatically adjusted to screen size in the
    #base Form implementation. Customization of the Form's resize method could
    #make many resizing schemes possible.
    #
    #To fully understand Form sizing, it is important to keep in mind the
    #distinction between how max_height/width and height/width are controlled.
    #
    #Let's start with max_height/width. If a form is not instantiated with a
    #max_height/width, then that attribute will automatically track with the
    #physical window size. As this attribute controls the size of the Form's
    #curses_pad, this means that the curses_pad will only track with the window
    #so long as the Form is not instantiated with specified max_height/width.
    #
    #Now about height/width. These follow the rules of Widgets. If instantiated
    #with height/width values along with preserve_instantiation_dimensions, then
    #Form.height/width will be given by the lesser of the instance dimension and
    #its maximum. If not instantiated with specified height/width values or
    #preserve_instantiation_dimensions, then Form.height/width will be give by
    #the lesser of the dimension and its maximum.
    #
    #I would wager that more often than not, if someone wishes to create an
    #interface using a form of a specific size, then they should be quite able
    #to do so by setting max_height/width at instantiation and then managing
    #the contained Widgets/Containers per those attributes. Referring to a
    #Form's height/width attributes directly can probably most often be avoided
    #altogether. This is a potential pitfall to be wary of though, make sure
    #that you are using the one you intend. If modification of the height/width
    #is needed, then make sure to avoid
    #setting preserve_instantiation_dimensions=True and add a call to inflate
    #or set height/width to max_height/width (or whatever you need) during your
    #Form's resize method.
    #
    #I can conceive of a scenario in which someone wishes for the height/width
    #values to be automatically sized to the window at the start, but then
    #disallow resizing after that. In this case, you can set either or both of
    #Form.auto_max_height and Form.auto_max_width to False to prevent their
    #resizing. This could be readily added in an extending override of __init__:
    #    class AutoInitNoResizeForm(Form):
    #        def __init__(self, *args, **kwargs):
    #            super(AutoInitNoResizeForm, self).__init__(*args, **kwargs)
    #            self.auto_max_height = False
    #            self.auto_max_width = False

    def __init__(self,
                 name=None,
                 parent_app=None,
                 min_height=24,
                 min_width=80,
                 max_height=None,
                 max_width=None,
                 color='FORMDEFAULT',
                 keypress_timeout=None,
                 #widget_list=None,
                 #cycle_widgets=False,
                 *args,
                 **kwargs):

        if max_height is None:
            self.auto_max_height = True
            max_height = self.max_physical()[0]
        else:
            self.auto_max_height = False

        if max_width is None:
            self.auto_max_width = True
            max_width = self.max_physical()[1]
        else:
            self.auto_max_width = False

        #Attention! Widgets sets self.form and self.parent as weakrefs of their
        #first instantiation arguments. Since Forms inherit from Widgets this
        #means that Form.form and Form.parent will be weakrefs to self; as a
        #consequence, inherited methods from Widget and Container that refer to
        #self.form or self.parent should still work
        super(Form, self).__init__(self,  # self.form -> self
                                   self,  # self.parent -> self
                                   #rely=0,
                                   #relx=0,
                                   max_height=max_height,
                                   max_width=max_width,
                                   *args,
                                   **kwargs)

        self.name = name
        self.parent_app = weakref.proxy(parent_app)
        self.min_height = min_height
        self.min_width = min_width

        #Indicates that the entire pad is visible on screen
        #self.ALL_SHOWN = False

        global APPLICATION_THEME_MANAGER
        if APPLICATION_THEME_MANAGER is None:
            self.theme_manager = theme_managers.ThemeManager()
        else:
            self.theme_manager = APPLICATION_THEME_MANAGER

        self.keypress_timeout = keypress_timeout

        self.show_from_y = 0
        self.show_from_x = 0
        self.show_aty = 0
        self.show_atx = 0

        self.create_pad()

    def set_up_handlers(self):
        self.complex_handlers = []
        self.handlers = {curses.KEY_RESIZE: self._resize}

    def create_pad(self):
        #Safety margin by adding 1; avoids issues, like putting a character in
        #the bottom right corner which causes an error as scrolling is not set
        pad_height = self.max_height + 1
        pad_width = self.max_width + 1

        if self.min_height > self.max_height:
            pad_height = self.min_height
        if self.min_width > self.max_width:
            pad_width = self.min_width

        self.pad_height = pad_height
        self.pad_width = pad_width

        log.debug('''\
creating new curses_pad: pad_height={0}, form.max_height={1}, \
form.min_height={2}; pad_width={3}, form.max_width={4}, form.min_width={5}\
'''.format(pad_height, self.max_height, self.min_height,
           pad_width, self.max_width, self.min_width))

        #self.area = curses.newpad(self.lines, self.columns)
        self.curses_pad = curses.newpad(pad_height, pad_width)
        #self.max_y, self.max_x = self.lines, self.columns
        #self.max_y, self.max_x = self.curses_pad.getmaxyx()

    def create(self):
        """
        Called at the end of Form instantiation. Overriding this method is a
        good way to add Widgets/Containers to the form as it is created.
        """
        pass

    def max_physical(self):
        """
        Returns the height and width of the physical screen.
        """
        #On OS X newwin does not correctly get the size of the screen.
        #let's see how big we could be: create a temp screen
        #and see the size curses makes it.  No good to keep, though
        try:
            max_y, max_x = struct.unpack('hh',
                                         fcntl.ioctl(sys.stderr.fileno(),
                                                     termios.TIOCGWINSZ,
                                                     'xxxx'))
            if (max_y, max_x) == (0, 0):
                raise ValueError
        except (ValueError, NameError):
            max_y, max_x = curses.newwin(0, 0).getmaxyx()

        #return safe values, i.e. slightly smaller.
        #I think the -1 is to account for 0-index: e.g. 10th columnn is col[9]
        #If this is the case, I may want to remove this subtraction
        #return (max_y - 1, max_x - 1)
        log.info('''\
max_physical reports; height/lines={0}, width/cols={1}'''.format(max_y, max_x))
        return (max_y, max_x)

    def exit_editing(self, *args, **keywords):
        self.editing = False
        try:
            self._widgets__[self.editw].entry_widget.editing = False
        except:
            pass
        try:
            self._widgets__[self.editw].editing = False
        except:
            pass

    def resize(self):
        pass

    def _resize(self, inpt=None):
        #This logic is arranged to ensure at most one call to max_physical
        if self.auto_max_height and self.auto_max_width:
            self.max_height, self.max_width = self.max_physical()
        elif self.auto_max_height:
            self.max_height = self.max_physical()[0]
        elif self.auto_max_width:
            self.max_width = self.max_physical()[1]

        self.height = self.max_height
        self.width = self.max_width

        self.create_pad()
        self.resize()
        #Originally there was a call to parent_app.resize, I am not sure if this
        #is useful, but it can be added again if desired
        for widget in self.contained:
            widget._resize()
        self._after_resizing_contained()
        self.DISPLAY()

    def DISPLAY(self):
        #As far as I can tell, this method is only used during _resize and it
        #clears everything and only displays the widget currently being edited
        #I'm not sure if this is the desired effect.
        #self.curses_pad.redrawwin()  # Touches window, so draws again on refresh
        self.erase()  # Window is completely cleared
        self.display()
        #self.display(clear=False)
        if self.editing and self.edit_index is not None:
            self.contained[self.edit_index].display()

    def _update(self, clear=True):
        if curses.has_colors() and not global_options.DISABLE_ALL_COLORS:
            self.curses_pad.attrset(0)
            color_attribute = self.theme_manager.find_pair(self, self.color)
            self.curses_pad.bkgdset(' ', color_attribute)
            self.curses_pad.attron(color_attribute)
        if clear:
            self.curses_pad.clear()
        #if self.hidden:
            #return True

        self.update()

        for contained in self.contained:
            if contained.hidden:
                continue
            contained._update(clear=clear)

    def refresh(self):
        pmfuncs.hide_cursor()
        max_y, max_x = self.max_physical()
        self.curses_pad.move(0, 0)

        #Since we can have panels larger than the screen let's allow for
        #scrolling them

        #Getting strange errors on OS X, with curses sometimes crashing at this
        #point. Suspect screen size not updated in time. This try: seems to
        #solve it with no ill effects.
        try:
            #self.curses_pad.refresh(self.show_from_y,
                                    #self.show_from_x
                                    #self.show_aty,
                                    #self.show_atx,
                                    #max_y - 1,
                                    #max_x - 1)
            #It seems to me that by using show_from_y/x as a sort of index
            #rectifier to be applied to contained widgets, I have essentially
            #virtualized a lot of the curses pad stuff...
            self.curses_pad.refresh(0,
                                    0,
                                    0,
                                    0,
                                    max_y - 1,
                                    max_x - 1)
        except curses.error:
            pass

        #if self.show_from_y is 0 and self.show_from_x is 0 and \
        #(max_y >= self.pad_height) and (max_x >= self.pad_width):
            #self.ALL_SHOWN = True

        #else:
            #self.ALL_SHOWN = False

    def erase(self):
        self.curses_pad.erase()
        self.refresh()

    def clear(self, usechar=' '):
        self.curses_pad.erase()

    def while_waiting(self):
        pass

    def activate(self):
        """
        This method is called whenever the Form is set by the parent application
        to be the active Form. Override this to provide any action needed for
        the activation of a Form; occurs immediately before `edit`.
        """
        pass

    def deactivate(self):
        """
        This method is called whenever the Form completes its `edit` method as
        the active Form for an application. Override this to provide any form
        teardown actions required.
        """
        pass

    def is_form(self):
        return True