# -*- coding: utf-8 -*-
import logging
import os
import ConfigParser as configparser

from . import paths


class Configuration(object):
    def __init__(self):
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

        new_configfile = paths.config('profile.cfg')

        # Read config
        self._logger.debug("Trying to read config file: '%s'", new_configfile)
        self._cp = configparser.RawConfigParser()
        try:
            self._cp.read(new_configfile)
        except OSError:
            self._logger.error("Can't open config file: '%s'", new_configfile)
            raise
        except configparser.Error:
            self._logger.error("Unable to parse config file: '%s'",
                               new_configfile)
            raise

    def get(self, *args):
        if len(args) == 2:
            (section, option) = args
        elif len(args) == 1:
            (section, option) = ("General", args[0])
        else:
            raise ValueError('Invalid number of arguments')
        try:
            value = self._cp.get(section, option)
        except configparser.Error:
            value = None
        return value
