# -*- coding: utf-8 -*-

__all__ = ['Container', 'GridContainer', 'SmartContainer']

from itertools import islice

import logging
log = logging.getLogger('npyscreen2.containers')


class Indexable(object):
    """
    Recipe for a generator iterator which supports indexing and slicing.

    Provides concise means for operations on contained Widgets for use in
    Containers.

    Aside from convenience, should offer performance benefits to Containers with
    large numbers of Widgets.
    """
    def __init__(self, it):
        self.it = iter(it)

    def __iter__(self):
        for elt in self.it:
            yield elt

    def __getitem__(self, index):
        try:
            return next(islice(self.it, index, index + 1))
        except TypeError:
            return list(islice(self.it, index.start, index.stop, index.step))

from .container import Container

from .gridcontainer import GridContainer

from .smartcontainer import SmartContainer

from .titledfield import TitledField