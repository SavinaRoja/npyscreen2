# -*- coding: utf-8 -*-

__all__ = ['Form', 'get_theme', 'set_theme', 'TraditionalForm']

from .form import Form, get_theme, set_theme

from .traditional import TraditionalForm

import logging
log = logging.getLogger('npyscreen2.forms')