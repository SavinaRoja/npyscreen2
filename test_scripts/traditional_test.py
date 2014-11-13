#!/usr/bin/env python
# encoding: utf-8

"""
Test application for npyscreen2 features.

Written by Paul Barton
"""

import npyscreen2
import curses
from time import strftime
import logging

l = logging.getLogger('npyscreen2.test')

class TestApp(npyscreen2.App):
    def on_start(self):
        self.main = self.add_form(TestTraditional,
                                  'MAIN',
                                  framed=True)


class TestTraditional(npyscreen2.TraditionalForm):
    def __init__(self, *args, **kwargs):
        super(TestTraditional, self).__init__(left_margin=1, *args, **kwargs)
        self.grid = self.add_widget(npyscreen2.GridContainer,
                                    rows=4,
                                    cols=5,
                                    container_select=True,
                                    preserve_instantiation_dimensions=False,
                                    hide_partially_visible=False)
        l.debug('rely={}, relx={}'.format(self.grid.rely, self.grid.relx))
        for i in range(self.grid.rows * self.grid.cols):
            g = self.grid.add_widget(BorderGrid, rows=3, cols=3, margin=1)
            for i in range(9):
                g.add_widget(npyscreen2.TextField, value=str(i), editable=True)


#    def while_waiting(self):
#        self.display()

class BorderGrid(npyscreen2.GridContainer):
    def __init__(self, form, parent, *args, **kwargs):
        super(BorderGrid, self).__init__(form, parent, container_editable_as_widget=True, *args, **kwargs)
        self.border = self.add(npyscreen2.BorderBox,
                               widget_id='border',
                               rely=0,
                               relx=0,
                               preserve_instantiation_dimensions=False,
                               auto_manage=False,
                               max_height=self.max_height,
                               max_width=self.max_width, editable=True)
    def resize(self):
        self.border.multi_set(rely=self.rely,
                              relx=self.relx,
                              max_height=self.max_height,
                              max_width=self.max_width)
        super(BorderGrid, self).resize()

    def pre_edit(self):
        l.debug('pre_edit called, setting container_selected=True')
        self.container_selected = True

class TestWidget(npyscreen2.BorderBox):
    pass
#    def resize(self):
#        self.inflate()



def main():
    npyscreen2.activate_logging()
    npyscreen2.add_rotating_file_handler('npyscreen2.log',
                                         level='debug',
                                         #filtr='npyscreen2.app',
                                         #filtr='npyscreen2.forms.traditional',
                                         #filtr='npyscreen2.containers',
                                         #filtr='npyscreen2.widgets.widget',
                                         #filtr='npyscreen2.containers.container',
                                         #filtr='npyscreen2.containers.gridcontainer',
                                         #filtr='npyscreen2.test',
                                         #filtr='npyscreen2.widgets.input_handler',
                                         max_bytes=100000000,  # 100MB
                                         backup_count=5,
                                         mode='w')
    app = TestApp(keypress_timeout_default=1)
    app.run()


if __name__ == '__main__':
    main()
