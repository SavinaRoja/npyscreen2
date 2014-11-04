#!/usr/bin/env python
# encoding: utf-8

"""
Test application for npyscreen2 features.

Written by Paul Barton
"""

import npyscreen2
import curses


class TestApp(npyscreen2.App):
    def on_start(self):
        self.main = self.add_form('MAIN', TestForm, height=30, width=100)

class TestForm(npyscreen2.Form):
    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.max_box = self.add_widget(npyscreen2.BorderBox, preserve_instantiation_dimensions=False)
        self.set_box = self.add_widget(npyscreen2.BorderBox, preserve_instantiation_dimensions=False)
        self.add_widget(npyscreen2.Widget)
        self.auto_max_height=False
        self.auto_max_width=False
#        self.add_widget(npyscreen2.Widget)

#    def update(self):
#         self.curses_pad.addch(31, 10, 'X', )
#        self.curses_pad.addstr(0, 0, '-' * 236)

    def resize(self):
        self.max_box.max_height = self.max_height
        self.max_box.max_width = self.max_width
        self.set_box.max_height = self.height
        self.set_box.max_width = self.width
        pass


    def post_edit(self):
        self.exit_application()

    def set_up_exit_condition_handlers(self):
        super(TestForm, self).set_up_exit_condition_handlers()
        self.how_exited_handlers['escape'] = self.exit_application

    def exit_application(self):
        curses.beep()
        self.parent_app.set_next_form(None)
        self.editing = False

    #def while_waiting(self):
        #self.display()

class TestWidget(npyscreen2.Widget):
    def resize(self):
        self.inflate()

    def update(self):
        self.addstr(self.rely, self.relx, 'Test of text')


def main():
    npyscreen2.activate_logging()
    npyscreen2.add_rotating_file_handler('npyscreen2.log',
                                         level='debug',
                                         #filtr='npyscreen2.app',
                                         filtr='npyscreen2.forms.form',
                                         max_bytes=100000000,  # 100MB
                                         backup_count=5,)
    app = TestApp(keypress_timeout_default=1)
    app.run()


if __name__ == '__main__':
    main()