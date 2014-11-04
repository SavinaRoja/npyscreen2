# -*- coding: utf-8 -*-

import curses
import weakref

from . import safe_wrapper

import logging
log = logging.getLogger('npyscreen2.app')


class NPSApp(object):
    """
    This class is intended to make it easier to program applications with many
    screens:

    1. The programmer should not now select which 'Form' to display himself.
       Instead, he should set the `NEXT_ACTIVE_FORM` class variable. See the
       `register_form` method for details.

       Doing this will avoid accidentally exceeding the maximum recursion depth.
       Forms themselves should be placed under the management of the class using
       the `add_form` or `add_form_class` methods.

       NB.  * Applications should therefore use this mechanism in preference to
       calling the `edit` method of any form. *

    2. Forms that are managed by this class can access a proxy to the parent
       application through their `parent_app` attribute, which is created by
       this class.

    3. a) Optionally, Forms managed by this class may be given an `activate`
       method, which will be called instead of their `edit` loop

       b) If not given an `activate` method, any `after_editing` method which a
       form possesses will be called after `edit` has exited. 3b is the
       preferred method to change NEXT_ACTIVE_FORM

    4. The method `on_in_main_loop`is called after each screen has exited. This
       may be overridden.

    5. This method should be able to see which screen was last active using the
       `self._LAST_NEXT_ACTIVE_FORM` attribute, which is only set just before
       eachscreen is displayed.

    6. Unless you override the attribute `STARTING_FORM`, the first form to be
       called should be named 'MAIN'

    7. Do override the on_start and on_clean_exit functions if you wish.

    """

    STARTING_FORM = "MAIN"

    def __init__(self, keypress_timeout_default=None):
        log.info('Instantiating NPSApp')
        self.keypress_timeout_default = keypress_timeout_default
        log.debug('NPSApp.keypress_timeout_default set to: {0}'.format(self.keypress_timeout_default))
        self._FORM_VISIT_LIST = []
        self.NEXT_ACTIVE_FORM = self.__class__.STARTING_FORM
        self._LAST_NEXT_ACTIVE_FORM = None
        self._Forms = {}

    def __remove_argument_call_main(self, screen, enable_mouse=True):
        if enable_mouse:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
        del screen
        return self.main()

    def run(self, fork=None):
        log.info('NPSApp.run called; fork={0}'.format(fork))
        """
        Run application. Calls Mainloop (`main` method) wrapped properly.
        """
        if fork is None:
            return safe_wrapper.wrapper(self.__remove_argument_call_main)
        else:
            return safe_wrapper.wrapper(self.__remove_argument_call_main,
                                        fork=fork)

    def add_form_class(self, form_class, form_id, *args, **kwargs):
        log.debug('''NPSApp.add_form_class called: form_class={}, form_id={}, \
args={}, kwargs={}'''.format(form_class, form_id, args, kwargs))
        self._Forms[form_id] = [form_class, args, kwargs]

    def add_form(self, form_class, form_id, *args, **kwargs):
        """
        Create a form of the given class. form_id should be a string which will
        niquely identify the form. *args and **kwargs will be passed to the Form
        constructor. Forms created in this way are handled entirely by the
        NPSAppManaged class.
        """
        log.debug('''NPSApp.add_form called: form_id={0}, form_class={1} \
args={2}, kwargs={3}'''.format(form_id, form_class, args, kwargs))
        form = form_class(parent_app=self,
                          keypress_timeout=self.keypress_timeout_default,
                          *args,
                          **kwargs)
        self.register_form(form, form_id)
        return weakref.proxy(form)

    def register_form(self, form, form_id):
        """
        form_id should be a string which should uniquely identify the form.
        fm should be a Form.
        """
        #fm.parent_app = weakref.proxy(self)
        self._Forms[form_id] = form
        log.debug('New form registered: self._Forms={0}'.format(self._Forms))

    def remove_form(self, form_id):
        log.debug('NPSApp Removing form: form_id={0}'.format(form_id))
        del self._Forms[form_id].parent_app
        del self._Forms[form_id]

    def get_form(self, name):
        f = self._Forms[name]
        try:
            return weakref.proxy(f)
        except:
            return f

    def set_next_form(self, form_id):
        """
        Set the form that will be selected when the current one exits.
        """
        log.debug('NPSApp.set_next_form called; form_id={0}'.format(form_id))
        self.NEXT_ACTIVE_FORM = form_id

    def switch_form(self, form_id):
        """
        Immediately switch to the form specified by form_id.
        """
        self._THISFORM.editing = False
        self.set_next_form(form_id)
        self.switch_form_now()

    def switch_form_now(self):
        self._THISFORM.editing = False
        try:
            self._THISFORM.contained[self._THISFORM.edit_index].editing = False
        except (AttributeError, IndexError):
            pass
        #Following is necessary to stop two keypresses being needed for
        #titlefields
        #try:
            #self._THISFORM._widgets__[self._THISFORM.editw].entry_widget.editing = False
        #except (AttributeError, IndexError):
            #pass

    def remove_last_form_from_history(self):
        self._FORM_VISIT_LIST.pop()
        self._FORM_VISIT_LIST.pop()

    def switch_form_previous(self, backup=STARTING_FORM):
        self.set_next_form_previous()
        self.switch_form_now()

    def set_next_form_previous(self, backup=STARTING_FORM):
        try:
            if self._THISFORM.FORM_NAME == self._FORM_VISIT_LIST[-1]:
                #Remove the current form. if it is at the end of the list
                self._FORM_VISIT_LIST.pop()
            #No action if it looks as if someone has already set the next form
            if self._THISFORM.FORM_NAME == self.NEXT_ACTIVE_FORM:
                #Switch to the previous form if one exists
                self.set_next_form(self._FORM_VISIT_LIST.pop())
        except IndexError:
            self.set_next_form(backup)

    def get_history(self):
        return self._FORM_VISIT_LIST

    def reset_history(self):
        self._FORM_VISIT_LIST = []

    def main(self):
        """
        This function starts the application. It is usually called indirectly
        through the `run` method.
        You should not override this function, but override the
        `on_in_main_loop`, `on_start` and `on_clean_exit` methods instead, if
        you need to modify the application's behaviour.

        When this method is called, it will activate the form named by the class
        variable STARTING_FORM. By default this Form will be called 'MAIN'.

        When that form exits (user selecting an ok button or the like), the form
        named by object variable NEXT_ACTIVE_FORM will be activated.

        If NEXT_ACTIVE_FORM is None, the main() loop will exit.

        The following will then occur for the selected Form: its `activate`
        method will be called, its `edit` method will be called, then its
        `deactivate` method will be called. `activate` may be overidden to
        enable actions that must be done prior to editing the form and
        `deactivate` does likewise for after the editing. An application that
        must connect to a database when a form becomes active and then close
        the connection when the form is done would benefit from these methods.

        Note that NEXT_ACTIVE_FORM is a string that is the name of the form that
        was specified when `add_form` or `register_form` was called.
        """

        self.on_start()
        while self.NEXT_ACTIVE_FORM is not None:
            self._LAST_NEXT_ACTIVE_FORM = self._Forms[self.NEXT_ACTIVE_FORM]
            self.LAST_ACTIVE_FORM_NAME = self.NEXT_ACTIVE_FORM
            try:
                Fm, a, k = self._Forms[self.NEXT_ACTIVE_FORM]
                self._THISFORM = Fm( parent_app = self, *a, **k )
            except TypeError:
                self._THISFORM = self._Forms[self.NEXT_ACTIVE_FORM]
            self._THISFORM.FORM_NAME = self.NEXT_ACTIVE_FORM
            self.ACTIVE_FORM_NAME = self.NEXT_ACTIVE_FORM
            if len(self._FORM_VISIT_LIST) > 0:
                if self._FORM_VISIT_LIST[-1] != self.NEXT_ACTIVE_FORM:
                    self._FORM_VISIT_LIST.append(self.NEXT_ACTIVE_FORM)
            else:
                self._FORM_VISIT_LIST.append(self.NEXT_ACTIVE_FORM)
            self._THISFORM._resize()
            self._THISFORM.activate()
            self._THISFORM.edit()
            self._THISFORM.deactivate()

            self.on_in_main_loop()
        self.on_clean_exit()

    def on_in_main_loop(self):
        """
        Called between each screen while the application is running. Not called
        before the first screen. Override at will.
        """
        pass

    def on_start(self):
        """
        Override this method to perform any initialisation.
        """
        pass

    def on_clean_exit(self):
        """
        Override this method to perform any cleanup when application is exiting
        without error.
        """
        pass


class NPSAppAdvanced(NPSApp):
    """
    EXPERIMENTAL and NOT for use.  This class of application will eventually
    replace the standard method of user input handling and deal with everything
    at the application level.
    """

    def _main_loop(self):
        pass

App = NPSApp
AppAdvanced = NPSAppAdvanced