# -*- coding: utf-8 -*-

import curses
from itertools import chain
import weakref

from ..widgets import Widget

import logging
log = logging.getLogger('npyscreen2.containers.container')

__all__ = ['Container']


class Container(Widget):

    def __init__(self,
                 form,
                 parent,
                 margin=0,  # Applies to all sides unless they are specified
                 container_select=False,
                 top_margin=None,
                 bottom_margin=None,
                 left_margin=None,
                 right_margin=None,
                 diagnostic=False,
                 cycle_widgets=False,
                 hide_partially_visible=False,
                 *args,
                 **kwargs):
        super(Container, self).__init__(form, self, *args, **kwargs)

        self.contained = []  # Holds Widgets and Containers
        self.contained_map = {}
        self._default_widget_id = 0

        self.diagnostic = diagnostic
        self.hide_partially_visible = hide_partially_visible

        self.cycle_widgets = cycle_widgets
        self.show_from_y, self.show_from_x = 0, 0

        self.margin = margin
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.left_margin = left_margin
        self.right_margin = right_margin

        #When set to None, nothing is selected for editing
        #When set to integer, self.contained[self.edit_index] is being edited
        self.edit_index = None
        #The notion here is the possibility to select the container as a whole
        #as an editing selection. Roughly speaking, this would enable a hold
        #point in the natural recursion of editing so that the Container object
        #as a whole could be manipulated
        self.container_select = container_select

        self.set_up_exit_condition_handlers()

        self.create()

    def add_widget(self,
                   widget_class,
                   widget_id=None,
                   rely=None,
                   relx=None,
                   max_height=None,
                   max_width=None,
                   *args,
                   **kwargs):
        """
        Add a Widget or Container (which is just another sort of Widget) to the
        Container. This will create an instance of `widget_class` along with
        specified args and kwargs.

        The created instance of `widget_class` will be added to `self.contained`
        and positioned on the screen per the Container's rules.

        If the optional `widget_id` keyword argument is used and provided a
        hashable value, then the widget instance will also be placed in the
        `self.contained_map` dictionary.
        """
        log.debug('''Container.add_widget method called: widget_class={0}, \
widget_id={1}, rely={2}, relx={3}, max_height={4}, max_width={5}, args={6}, \
kwargs={7}'''.format(widget_class, widget_id, rely, relx, max_height,
                     max_width, args, kwargs))
        #Should consider scenarios where certain keyword arguments should be
        #inherited from the parent Container unless overridden. I suppose this
        #was the impetus for _passon in some npyscreen library classes
        y, x = self.next_rely_relx()

        if rely is None:
            rely = y

        if relx is None:
            relx = x

        if max_height is None:
            max_height = self.max_height - (self.top_margin + self.bottom_margin)
        if max_width is None:
            max_width = self.max_width - (self.left_margin + self.right_margin)

        widget = widget_class(self.form,
                              self,  # self.parent -> self
                              relx=relx,
                              rely=rely,
                              max_height=max_height,
                              max_width=max_width,
                              *args,
                              **kwargs)

        self.contained.append(widget)
        log.debug('Widget/Container added: contained={0}'.format(self.contained))

        widget_proxy = weakref.proxy(widget)

        if widget_id is not None:
            self.contained_map[widget_id] = widget_proxy
        else:
            self.contained_map[self._default_widget_id] = widget_proxy
            self._default_widget_id += 1

        return widget_proxy

    add = add_widget

    def remove_widget(self, widget=None, widget_id=None):
        """
        `remove_widget` can be used in two ways: the first is to pass in a
        reference to the widget intended to be removed, the second is to pass in
        it's id (registered in `self.contained_map`).

        This method will return True if the widget was found and successfully
        removed, False otherwise. This method will automatically call
        `self.resize` upon a successful removal.
        """
        if widget is None and widget_id is None:
            raise TypeError('remove_widget requires at least one argument')

        #By ID
        if widget_id is not None:
            if widget_id not in self.contained_map:
                return False
            widget = self.contained_map[widget_id]
            self.contained.remove(widget)
            del self.contained_map[widget_id]
            self.resize()
            return True

        #By widget reference
        try:
            self.contained.remove(widget)
        except ValueError:  # Widget not a member in this container
            return False
        else:
            #Looking for values in a dict is weird, but seems necessary
            map_key = None
            for key, val in self.contained_map.items():
                if val == widget:
                    map_key = key
                    break
            if map_key is not None:
                del self.contained_map[map_key]
            self.resize()
            return True

    def next_rely_relx(self):
        """
        This method is used by `add_widget` to determine where a widget should
        initially be placed during instantiation. Returns coordinates rely, relx
        and as a rule, if modified, should never return a value outside the
        bounds of the Container as set by max_height and max_width (margin
        values should also be respected).
        """
        return self.rely + self.top_margin, self.relx + self.left_margin

    #def set_up_handlers(self):
        #self.complex_handlers = []
        #self.handlers = {}

    def set_up_exit_condition_handlers(self):
        """
        Set up handlers for what to do when widgets exit.

        The keys in this base implementation represent a set of standard values
        one is likely to see from Widgets. Support for new ones can of course be
        added. Generally you should override this method with the following
        pattern in order to change mappings or add new ones:

        def set_up_exit_condition_handlers(self):
            super(SubContainer, self).set_up_exit_condition_handlers()
            self.how_exited_handlers.update({'custom': self.custom_handler,
                                             'escape': self.escape_handler})

        As a Widget exits its edit loop, it should set its `how_exited`
        attribute, the value of this attribute is what will be used in lookup.
        """
        self.how_exited_handlers = {'down': self.find_next_editable,
                                    'right': self.find_next_editable,
                                    'up': self.find_previous_editable,
                                    'left': self.find_previous_editable,
                                    'escape': self.do_nothing,
                                    True: self.find_next_editable,
                                    'mouse': self.get_and_use_mouse_event,
                                    False: self.do_nothing,
                                    None: self.do_nothing}
        log.debug('how_exit_handlers initialized: {0}'.format(self.how_exited_handlers))

    def safe_get_mouse_event(self):
        try:
            mouse_event = curses.getmouse()
            return mouse_event
        except curses.error:
            return None

    def get_and_use_mouse_event(self):
        log.debug('{0}.get_and_use_mouse_event called'.format(self.__class__))
        mouse_event = self.safe_get_mouse_event()
        if mouse_event:
            self.use_mouse_event(mouse_event)

    def find_next_editable(self):
        """
        This method should set `self.edit_index` to the next available widget
        for editing.

        If there is no suitable widget for editing, then this method will take
        no action. This method along with `find_previous_editable` should be
        sufficient for Containers where a linear mapping of contained widgets is
        fully sufficient for navigation. For others, such as a grid-styled
        Container, additional handling of `Widget.how_exited` attribute values
        should be employed (such as 'up', 'down', 'left', 'right').

        Override this method as needed. This base implementation is rather
        simple, and takes `self.cycle_widgets` into account. If True, then this
        method will search the list of contained Widgets as though it were a
        circle, rather than a line.
        """
        #Everything after the current index
        search = self.contained[self.edit_index + 1:]
        if self.cycle_widgets:
            #Append everything before the current index
            search = chain(search, self.contained[:self.edit_index])

        for widget in search:
            if widget.editable and not widget.hidden:
                self.edit_index = self.contained.index(widget)
                break

        self.display()

    def find_previous_editable(self):
        """
        This method should set `self.edit_index` to the next available widget
        for editing.

        If there is no suitable widget for editing, then this method will take
        no action. This method along with `find_next_editable` should be
        sufficient for Containers where a linear mapping of contained widgets is
        fully sufficient for navigation. For others, such as a grid-styled
        Container, additional handling of `Widget.how_exited` attribute values
        should be employed (such as 'up', 'down', 'left', 'right').

        Override this method as needed, This base implementation is rather
        simple, and takes `self.cycle_widgets` into account. If True, then this
        method will search the list of contained Widgets as though it were a
        circle, rather than a line.
        """
        #Everything before the current index in reverse order
        search = self.contained[self.edit_index - 1:: -1]
        if self.cycle_widgets:
            #Append everything after the current index in reverse order
            search = chain(search, self.contained[:self.edit_index: -1])

        for widget in search:
            if widget.editable and not widget.hidden:
                self.edit_index = self.contained.index(widget)
                break

        self.display()

    def handle_exiting_widgets(self, condition):
        self.how_exited_handlers[condition]()

    def do_nothing(self, *args, **keywords):
        pass

    def enter_edit_loop(self):
        """
        When entering the edit loop for a Container, it must find which of its
        contained widgets will initially acquire the editing selection. This
        method should return an index value of and editable widget in
        `self.contained`. If no contained Widget is editable, then this method
        should return False.

        This base implementation simply iterates through the contained widgets
        to find the first with its `editable` attribute set to True.

        Override this method if you wish to change the behavior for the start of
        the Container's `edit` method.
        """
        for i, widget in enumerate(self.contained):
            if widget.editable:
                return i
        return None  # None represents an unset editing selection

    #TODO: Develop distinct upper and lower editing loops to handle
    #self.container_select, along with exit handlers for ascent and descent so
    #that it's easier to treat Containers atomically like Widgets
    def edit_loop(self):
        self.display()
        self.edit_index = self.enter_edit_loop()

        self.edit_index = self.enter_edit_loop()
        log.debug('{0}.enter_edit_loop returned: {1}'.format(self.__class__,
                                                             self.edit_index))
        if self.edit_index is None:
            self.editing = False
            return False

        while self.editing:
            #Do check to get editing widget on screen
            selected = self.contained[self.edit_index]
            log.debug('selected for editing: {0}'.format(selected))
            self.while_editing(selected)
            if not self.editing:  # Because this may change in while_editing
                break
            selected.edit()
            selected.display()

            log.debug('After editing, how_exited={0}'.format(selected.how_exited))
            self.handle_exiting_widgets(selected.how_exited)

    def while_editing(self, widget_ref):
        """
        Executed during each iteration of a Container's `edit_loop`, receives
        a reference to the currently selected Widget for editing as the first
        argument, regardless of being needed. Override this as needed.
        """
        pass

    #def edit_loop(self):
        #self.display()
        #while not self.contained[self.edit_index].editable:
            #self.edit_index += 1
            #if self.edit_index > len(self.contained) - 1:
                #self.editing = False
                #return False

        #while self.editing:
            ##Check to ensure that the widget being edited is visible on screen
            ##This code comes from npyscreen and I don't think its truly
            ##generalizable to the new implementation...
            ##If the entire pad is on screen, then it is presumed that the widget
            ##must be visible, which I don't think should actually be True
            #if not self.ALL_SHOWN:
                ##on_screen is meant to adjust the screen so that the selected
                ##widget for editing is visible. Can this be generalized for all
                ##Forms or should it be left up to sub-classes?
                #self.on_screen()
            #self.while_editing(weakref.proxy(self.contained[self.edit_index]))
            #self._during_edit_loop()
            #if not self.editing:
                #break
            #self.contained[self.edit_index].edit()
            #self.contained[self.edit_index].display()

            #self.handle_exiting_widgets(self.contained[self.edit_index].how_exited)

            #if self.edit_index > len(self.contained)-1:
                #self.edit_index = len(self.contained)-1

    def create(self):
        """
        This method is called after instantiation of the Base Container
        """
        pass

    def _resize(self, inpt=None):
        """
        It is taken as a general contract that when a Container is resized then
        it should in turn resize everything it contains whether it is another
        Container or a Widget. Since Containers are in fact a special type of
        Widget, this is not so strange. As such, this base definition of
        `resize` calls the `resize` method of all items in `self.contained`.

        For subclassing Containers, it is advised that this method is left
        unmodified and that the specifics of resizing for that Container be
        placed in `_resize`.
        """
        self.resize()
        for widget in self.contained:
            #As a rule, the Container should constrain the dimensions of its
            #items to its own limits, less margins
            widget.max_height = self.max_height - \
                                (self.top_margin + self.bottom_margin)
            widget.max_width = self.max_width - \
                               (self.left_margin + self.right_margin)
            widget._resize()
        self._after_resizing_contained()

    def resize(self):
        """
        It is the job of `resize` to appropriately modify the `rely` and `relx`
        attributes of each item in `self.contained`. It should also modify the
        `max_height` and `max_width` attributes as appropriate. Rarely, if ever,
        should this method directly set the `height` and `width` attributes of
        its contained Widgets and Containers directly.

        This is the method you should probably be modifying if you are making a
        new Container subclass.

        As this method should generally be encapsulated by `resize`, it should
        not be necessary to call the `resize` method of the items in
        `self.contained`.
        """
        pass

    #A Container should be capable of determining if a Widget fits within the
    #bounds of its available space based on the Widget's position (rely/relx)
    #and dimensions (height/width). If a Widget is wholly outside the Container
    #bounds, then it should be hidden. If a Widget is partially outside the
    #Container bounds, then there are two options: display what fits, or hide
    #the whole thing (same as if fully out of bounds).
    #
    #In the context of the Form as Container, the max_height and max_width
    #correspond to the dimensions of the curses_pad; writing outside of this
    #pad will cause an error. The pad may extend outside of the physical screen
    #and writing to the pad that is not visible on the physical screen will not
    #cause an error. Consequently there is no need to concern ourselves with
    #additional checks of physical screen size for the sake of preventing
    #errors. Though depending on the needs of specific interfaces, checks to
    #the physical screen size may be needed for aesthetic or functional purposes
    #and choosing between the two strategies described above for partially
    #attenuated (by physical screen dimensions) Widgets may be required.
    #
    #This has an impact on how the Container resizing protocol is implemented.
    #After every Widget has resized the Container must re-evaluate which of the
    #Widgets are fully visible and which are not according to their height and
    #width attributes, as these values may change during resize. This leads to
    #the _after_resizing_contained method (which calls after_resizing_contained
    #for extension) which does this check. Additionally, the pad writing
    #methods are equipped with evaluations to ensure they do not write past the
    #space available to them.

    def _after_resizing_contained(self):
        """
        This method is performed by the container after it has finished resizing
        the contained widgets. The internal method, which generally should not
        be overridden, determines which contained Widgets are currently visible
        within the container, and which are not.

        If self.hide_partially_visible is True, then this will set Widgets whose
        bounds are only partly inside the Container to be hidden, otherwise it
        will not modify them.
        """
        #avail_height = self.max_height - (self.top_margin + self.bottom_margin)
        #avail_width = self.max_width - (self.left_margin + self.right_margin)
        #container_y_top
        c_y_t = self.rely + self.top_margin
        #container_y_bottom
        c_y_b = self.rely + self.height - self.bottom_margin - 1
        #container_x_left
        c_x_l = self.relx + self.left_margin
        #container_x_right
        c_x_r = self.relx + self.width - self.left_margin
        for widget in self.contained:
            #widget_y_top, widget_y_bottom
            w_y_t, w_y_b = widget.rely, widget.rely + widget.height - 1
            #widget_x_left, widget_x_right
            w_x_l, w_x_r = widget.relx, widget.relx + widget.width - 1

            #Determines if widget is fully outside of container
            if w_y_t > c_y_b or w_y_b < c_y_t or w_x_l > c_x_r or w_x_r < c_x_l:
                widget.hidden = True  # In which case we hide the widget
            #Determine if widget is fully within container
            elif w_y_t >= c_y_t and w_y_b <= c_y_b and w_x_l >= c_x_l and \
                 w_x_r <= c_x_r:
                pass  # In which case we do nothing
            #Widget is only partly visible if the previous are False
            else:
                if self.hide_partially_visible:
                    widget.hidden = True

        self.after_resizing_contained()

    def after_resizing_contained(self):
        """
        The external method for adding function to be executed after the
        contained widgets have been resized. Override this freely.
        """
        pass

    def feed(self):
        """
        A Container does not have a meaningful value, so a feed method for a
        Container does not behave like a feed method for a LiveWidget. Instead,
        the feed method of a container must call the feed methods for each
        contained Widget or Container that has a feed method.
        """
        for widget in self.contained:
            if widget._feed is not None:
                widget.feed()

    def update(self):
        """
        Modify this method if you wish to add behavior to a Container when it
        is updated. The clearing of the widget area and the calling of contained
        items is handled in `update` which calls this method.
        """
        pass

    def _update(self, clear=True):
        if clear:
            self.clear()

        if self.hidden:
            return True

        self.update()

        #if self.diagnostic:
            #self.parent.curses_pad.addch(self.rely, self.relx, self.diagnostic)

        for contained in self.contained:
            if contained.hidden:
                continue
            contained._update(clear=clear)

    def iter_contained(self):
        """
        A simple generator for iterating over self.contained, may be useful for
        dealing with very large numbers of widgets.
        """
        for widget in self.contained:
            yield widget

    @property
    def margin(self):
        return self._margin

    @margin.setter
    def margin(self, val):
        self._margin = val

    @property
    def top_margin(self):
        #None indicates unset
        if self._top_margin is None:
            return self.margin
        return self._top_margin

    @top_margin.setter
    def top_margin(self, val):
        self._top_margin = val

    @property
    def bottom_margin(self):
        #None indicates unset
        if self._bottom_margin is None:
            return self.margin
        return self._bottom_margin

    @bottom_margin.setter
    def bottom_margin(self, val):
        self._bottom_margin = val

    @property
    def left_margin(self):
        #None indicates unset
        if self._left_margin is None:
            return self.margin
        return self._left_margin

    @left_margin.setter
    def left_margin(self, val):
        self._left_margin = val

    @property
    def right_margin(self):
        #None indicates unset
        if self._right_margin is None:
            return self.margin
        return self._right_margin

    @right_margin.setter
    def right_margin(self, val):
        self._right_margin = val
