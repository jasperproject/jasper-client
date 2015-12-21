# -*- coding: utf-8 -*-
import logging
import os
import ConfigParser as configparser

from . import paths


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

        self._cp = configparser.RawConfigParser()
        self._cp.read(filenames)

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
