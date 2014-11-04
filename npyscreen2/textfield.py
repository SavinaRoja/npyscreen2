# -*- coding: utf-8 -*-

from . import widget


class TextField(widget.Widget):

    def __init__(self, *args, **kwargs):
        super(TextField, self).__init__(*args, **kwargs)
        if self.value is None:
            self.value = ''