#!/usr/bin/env python
# encoding: utf-8

"""
Test application for npyscreen2 features.

Written by Paul Barton
"""

import npyscreen2
#import logging


class TestApp(npyscreen2.App):
    def on_start(self):
        self.main = self.add_form(TestTraditional,
                                  'MAIN',
                                  framed=True,
#                                  max_height=30, max_width=40,
#                                  preserve_instantiation_dimensions=True,
                                  cycle_widgets=True)


class TestTraditional(npyscreen2.TraditionalForm):
    def __init__(self, *args, **kwargs):
        super(TestTraditional, self).__init__(*args, **kwargs)
        for i in range(45):
            self.add_widget(TestWidget, value=str(i), height=1)

    def while_waiting(self):
        self.display()


class TestWidget(npyscreen2.TextField):
    def resize(self):
        self.inflate()


def main():
    npyscreen2.activate_logging()
    npyscreen2.add_rotating_file_handler('npyscreen2.log',
                                         level='debug',
                                         #filtr='npyscreen2.app',
                                         #filtr='npyscreen2.forms.traditional',
                                         #filtr='npyscreen2.containers',
                                         #filtr='npyscreen2.widgets.widget',
                                         max_bytes=100000000,  # 100MB
                                         backup_count=5,
                                         mode='w')
    app = TestApp(keypress_timeout_default=1)
    app.run()


if __name__ == '__main__':
    main()