#!/usr/bin/env python
# encoding: utf-8

"""
Test application for npyscreen2 features.

Written by Paul Barton
"""

import npyscreen2
import curses
from time import strftime

class TestApp(npyscreen2.App):
    def on_start(self):
        self.main = self.add_form('MAIN', TestTraditional, framed=True, cycle_widgets=True)

class TestTraditional(npyscreen2.TraditionalForm):
    def __init__(self, *args, **kwargs):
        super(TestTraditional, self).__init__(*args, **kwargs)
        self.add_widget(TestWidget, value='spam is good what do you think? I could do this all the damn day')

    def resize(self):
        for i in self.contained:
            i.max_height = self.max_height - 3
            i.max_width = self.max_width - 3

class TestWidget(npyscreen2.TextField):

    def resize(self):
        self.inflate()


def main():
    npyscreen2.activate_logging()
    npyscreen2.add_rotating_file_handler('npyscreen2.log',
                                         level='debug',
                                         #filtr='npyscreen2.app',
                                         #filtr='npyscreen2.forms.traditional',
#                                         filtr='npyscreen2.widgets.widget',
                                         max_bytes=100000000,  # 100MB
                                         backup_count=5,)
    app = TestApp(keypress_timeout_default=1)
    app.run()


if __name__ == '__main__':
    main()