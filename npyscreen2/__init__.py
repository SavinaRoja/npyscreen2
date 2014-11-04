# -*- coding: utf-8 -*-

"""
npyscreen2 is mostly an experiment to see what I could do refactoring npyscreen
if backwards compatibility was not a concern.

A lot of the fundamental curses code, along with some of the base Form and
Widget methods come from the original npyscreen. Containers are my own
development (not that it's a terribly original idea), and I have made some heavy
modifications in many areas to create the new API design. A handful of changes
have been motivated simply by PEP8 conformance.

npyscreen author: Nicholas Cole
npyscreen2 author: Paul Barton (SavinaRoja)
"""

from .safe_wrapper import wrapper, wrapper_basic

from .app import NPSApp, App, NPSAppAdvanced, AppAdvanced

from .widgets import Widget, NotEnoughSpaceForWidget, BorderBox, TextField

from .containers import Container

from .forms import Form, set_theme, get_theme, TraditionalForm

from .logs import activate_logging, add_rotating_file_handler

import logging
logger = logging.getLogger('npyscreen2')