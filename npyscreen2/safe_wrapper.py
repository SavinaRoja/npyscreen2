# -*- coding: utf-8 -*-

"""
Provides wrappers for application routine functions for the initialization and
breakdown of curses.
"""

import curses
import locale
import os
import subprocess
import sys
import warnings

import logging
logger = logging.getLogger('npyscreen2.safe_wrapper')


NEVER_RUN_INITSCR = True
SCREEN = None


def wrapper_basic(call_function):
    #set the locale properly
    locale.setlocale(locale.LC_ALL, '')
    return curses.wrapper(call_function)


def wrapper(call_function, fork=None, reset=True):
    global NEVER_RUN_INITSCR
    if fork:
        wrapper_fork(call_function, reset=reset)
    elif fork is False:
        wrapper_no_fork(call_function)
    else:
        if NEVER_RUN_INITSCR:
            wrapper_no_fork(call_function)
        else:
            wrapper_fork(call_function, reset=reset)


def wrapper_fork(call_function, reset=True):
    pid = os.fork()
    if pid:
        # Parent
        os.waitpid(pid, 0)
        if reset:
            external_reset()
    else:
        locale.setlocale(locale.LC_ALL, '')
        SCREEN = curses.initscr()
        try:
            curses.start_color()
        except:
            pass
        SCREEN.keypad(1)
        curses.noecho()
        curses.cbreak()
        curses.def_prog_mode()
        curses.reset_prog_mode()
        _return_code = call_function(SCREEN)  # assigned but not used
        SCREEN.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        sys.exit(0)


def external_reset():
    subprocess.call(['reset', '-Q'])


def wrapper_no_fork(call_function, reset=False):
    global NEVER_RUN_INITSCR
    if not NEVER_RUN_INITSCR:
        warnings.warn('''Repeated calls of endwin may cause a memory leak. Use \
wrapper_fork to avoid.''')
    global SCREEN
    return_code = None
    if NEVER_RUN_INITSCR:
        NEVER_RUN_INITSCR = False
        locale.setlocale(locale.LC_ALL, '')
        SCREEN = curses.initscr()
        try:
            curses.start_color()
        except:
            pass
        curses.noecho()
        curses.cbreak()
        SCREEN.keypad(1)

    curses.noecho()
    curses.cbreak()
    SCREEN.keypad(1)

    try:
        return_code = call_function(SCREEN)
    finally:
        SCREEN.keypad(0)
        curses.echo()
        curses.nocbreak()
        #Calling endwin() and then refreshing seems to cause a memory leak.
        curses.endwin()
        if reset:
            external_reset()
    return return_code
