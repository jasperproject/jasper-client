# -*- coding: utf-8 -*-
import logging
import os

from . import parser
from .. import paths


class Configuration(object):
    def __init__(self, filenames):
        self._logger = logging.getLogger(__name__)
        self._data = {}

        # Create config dir if it does not exist yet
        if not os.path.exists(paths.CONFIG_PATH):
            try:
                os.makedirs(paths.CONFIG_PATH)
            except OSError:
                self._logger.error("Could not create config dir: '%s'",
                                   paths.CONFIG_PATH, exc_info=True)
                raise

        # Check if config dir is writable
        if not os.access(paths.CONFIG_PATH, os.W_OK):
            self._logger.critical("Config dir %s is not writable. Jasper " +
                                  "won't work correctly.",
                                  paths.CONFIG_PATH)

        self._cp = parser.ConfigParser()
        self._defaults = parser.ConfigParser()

        self._cp.read(filenames)

    def read_defaults(self, *args, **kwargs):
        self._defaults.read(*args, **kwargs)

    def get(self, *args):
        if len(args) == 2:
            (section, option) = args
        elif len(args) == 1:
            (section, option) = ("General", args[0])
        else:
            raise ValueError('Invalid number of arguments')
        try:
            value = self._cp.get(section, option)
        except parser.configparser.Error:
            try:
                value = self._defaults.get(section, option)
            except parser.configparser.Error:
                self._logger.warning("Can't find default value for option " +
                                     "'%s' in section '%s'.", option, section)
                value = None
            else:
                self._logger.debug("Option '%s' in section '%s' is " +
                                   "missing, using default value (%r).",
                                   option, section, value)

        return value
