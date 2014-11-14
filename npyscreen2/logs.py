# -*- coding: utf-8 -*-
"""
"""

import logging
import logging.handlers
import sys

STANDARD_FORMAT = '%(name)s [%(levelname)s] %(message)s'
MESSAGE_ONLY_FORMAT = '%(message)s'


def get_level(level_string):
    """
    Returns an appropriate logging level integer from a string name
    """
    levels = {'debug': logging.DEBUG, 'info': logging.INFO,
              'warning': logging.WARNING, 'error': logging.ERROR,
              'critical': logging.CRITICAL}
    try:
        level = levels[level_string.lower()]
    except KeyError:
        sys.exit('{0} is not a recognized logging level'.format(level_string))
    else:
        return level


def activate_logging(level=None):
    log = logging.getLogger('npyscreen2')
    if level is None:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(get_level(level))


def add_rotating_file_handler(filename,
                              frmt=None,
                              level=None,
                              filtr=None,
                              max_bytes=0,
                              backup_count=0,
                              mode='a'):
    log = logging.getLogger('npyscreen2')
    handler = logging.handlers.RotatingFileHandler(filename,
                                                   maxBytes=max_bytes,
                                                   backupCount=backup_count,
                                                   encoding='utf-8',
                                                   mode=mode)

    if level is None:
        handler.setLevel(logging.WARNING)
    else:
        handler.setLevel(get_level(level))

    if filtr is not None:
        handler.addFilter(logging.Filter(filtr))

    if frmt is None:
        handler.setFormatter(logging.Formatter(STANDARD_FORMAT))
    else:
        handler.setFormatter(logging.Formatter(frmt))

    log.addHandler(handler)

#def deactivate_logging():
    #log = logging.getLogger('npyscreen2')
