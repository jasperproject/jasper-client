# -*- coding: utf-8 -*-
import logging
import os

from . import parser
from .. import paths


def str_to_bool(value):
    if any([x in value.lower() for x in ('yes', 'y', 'true', 'ok')]):
        return True
    return False


def str_to_path(value):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(value)))


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

    def get(self, section, option):
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

        if value is not None:
            value_list = [x.strip() for x in value.splitlines() if x.strip()]
            if len(value_list) > 1:
                value = value_list
            elif len(value_list) == 1:
                value = value_list[0]
            else:
                value = None
        return value

    def _get_conv(self, conv_func, section, option):
        value = self.get(section, option)
        if value is None:
            return None
        try:
            if isinstance(value, list):
                converted_value = [conv_func(x) for x in value]
            else:
                converted_value = conv_func(value)
        except Exception:
            self._logger.warning("Option '%s' in section '%s' has an invalid" +
                                 " value.", option, section)
            converted_value = None
        return converted_value

    def getint(self, *args, **kwargs):
        return self._get_conv(int, *args, **kwargs)

    def getfloat(self, *args, **kwargs):
        return self._get_conv(float, *args, **kwargs)

    def getbool(self, *args, **kwargs):
        return self._get_conv(str_to_bool, *args, **kwargs)

    def getpath(self, *args, **kwargs):
        return self._get_conv(str_to_path, *args, **kwargs)
