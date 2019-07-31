#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import logging

import qplotutils.ui.resources_rc

__author__ = "Philipp Baust"
__copyright__ = "Copyright 2019, Philipp Baust"
__credits__ = []
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philipp Baust"
__email__ = "philipp.baust@gmail.com"
__status__ = "Development"

# . Default logging level for all modules.
LOG_LEVEL = logging.WARNING

#: MIME type for drag and drop of docks.
MIME_TYPE = "application/x-dockbench"


# DEBUG = False
# """ Enables debug visualisations. """


class Configuration:
    """ Global states and settings, shared as a borg object. """

    __shared_state = None

    def __init__(self):
        """ Constructor. """
        if not Configuration.__shared_state:
            Configuration.__shared_state = self.__dict__

            self.__debug = False
            self.__debug__layout = False

        else:
            self.__dict__ = Configuration.__shared_state

    @property
    def debug(self):
        """ Enables / disbales general debugging. """
        return self.__debug

    @debug.setter
    def debug(self, value):
        self.__debug = value

    @property
    def debug_layout(self):
        """ Enable / disable layout debuging frames. """
        return self.__debug__layout

    @debug_layout.setter
    def debug_layout(self, value):
        self.__debug__layout = value


#: Global configuration for qplotutils (e.g. disable/enable debug visualization)
CONFIG = Configuration()


class QPlotUtilsException(Exception):
    pass
