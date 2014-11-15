# -*- coding: utf-8 -*-

from . import Container
from ..widgets import TextField
#from ..widgets.input_handler import exit_edit_method

import logging

log = logging.getLogger('npyscreen2.containers.titledfield')


class TitledField(Container):

    def __init__(self,
                 form,
                 parent,
                 title_theme='LABEL',
                 title_width=None,
                 title_value='',
                 field_theme='DEFAULT',
                 field_value='',
                 field_class=TextField,
                 editable=True,
                 field_feed=None,
                 *args,
                 **kwargs):
        self.field_feed = field_feed
        self.field_class = field_class
        super(TitledField, self).__init__(form,
                                          parent,
                                          editable=editable,
                                          *args,
                                          **kwargs)

        #A title is of fixed length, if not supplied then it will be set to the
        #length of the the title_text
        if title_width is None:
            title_width = len(title_value) + 1

        self.title = self.add_widget(TextField,
                                     color=title_theme,
                                     value=title_value,
                                     editable=False,
                                     width=title_width,
                                     auto_manage=False,
                                     relx=self.relx + self.left_margin,
                                     rely=self.rely)

        self.field = self.add_widget(self.field_class,
                                     color=field_theme,
                                     #relx=self.relx + self.title.width + self.left_margin,
                                     #rely=self.rely,
                                     auto_manage=False,
                                     editable=True,
                                     value=field_value,
                                     feed=self.field_feed)

    def set_up_exit_condition_handlers(self):
        self.how_exited_handlers = {'down': self.end_edit_with_condition,
                                    'right': self.end_edit_with_condition,
                                    'up': self.end_edit_with_condition,
                                    'left': self.end_edit_with_condition,
                                    'escape': self.end_edit_with_condition,
                                    True: self.end_edit_with_condition,
                                    'mouse': self.end_edit_with_condition,
                                    False: self.end_edit_with_condition,
                                    None: self.end_edit_with_condition}

    def end_edit_with_condition(self):
        self.editing = False
        self.how_exited = self.contained[self.edit_index].how_exited

    def resize(self):
        self.title.multi_set(relx=self.relx + self.left_margin,
                             rely=self.rely,
                             max_width=self.width,
                             max_height=self.height)

        self.field.multi_set(relx=self.relx + self.left_margin + self.title.width,
                             rely=self.rely,
                             max_height=self.height,
                             max_width=self.width - self.right_margin - self.title.width)
