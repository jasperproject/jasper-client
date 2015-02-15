# -*- coding: utf-8-*-
"""
Config module

Usage:

from jasperconf import Config as conf
firstname = conf.get("firstname")
# Alternative:
# firstname = conf.get(["firstname"])
conf.set(["keys","GOOGLE_SPEECH"], value="ABCDEF" )
google_api_key = conf.get(["keys", "GOOGLE_SPEECH"])
"""
import os
import copy
import logging
from abc import ABCMeta, abstractmethod

import jasperpath
import yaml


class AbstractConfig(object):
    """
    Base class which acts as an interface for custom Config classes.
    """
    __metaclass__ = ABCMeta
    FILE_EXT = None
    DEFAULTS_FILE = None
    STANDARD_CONFIG_FILE = None

    def __init__(self, fname="", load_defaults=True, autosave=False):
        """
        The Constructor. Calls AbstractConfig.load().
        Arguments:
            fname -- If given, load file fname, otherwise use
                     STANDARD_CONFIG_FILE
            load_defaults -- If config value not present, try to return default
                             value from DEFAULTS_FILE (default: True)
            autosave -- If True, automatically save config file during calls of
                        AbstractConfig.set(). (default: False)
        """
        self._logger = logging.getLogger(__name__)
        self._config_file = fname if fname else self.STANDARD_CONFIG_FILE
        self.autosave = autosave
        self.load_defaults = load_defaults
        self.load(fname=self._config_file)

    @abstractmethod
    def load(self, fname):
        """
        Loads the config file 'fname'
        """
        pass

    @abstractmethod
    def get(self, path):
        """
        Returns config value specified by 'path' or None, if not found.
        """
        pass

    @abstractmethod
    def set(self, path, value=None):
        """
        Sets config value specified by 'path' to 'value'.
        """
        pass

    @abstractmethod
    def to_dict(self):
        """
        Converts config into a dict like the one returned by yaml.safe_load()
        Used for backwards compatibility with existing client modules.
        """
        pass

    @abstractmethod
    def save(self, output_file=""):
        """
        Writes the current configuration to 'output_file' if given, otherwise
        writes it to the current config file
        """
        pass

    def sanitize_path(self, path):
        """
        Makes sure that path if not malformatted
        """
        if not path:
            raise ValueError("Path must not be empty")
        if isinstance(path, str):
            path = [path]
        if "" in path:
            raise ValueError("Path must not contain empty strings")
        for component in path:
            if type(component) is not str:
                raise TypeError("Path must contain strings only")
        return path


class YamlConfig(AbstractConfig):
    FILE_EXT = "yml"
    DEFAULTS_FILE = jasperpath.data(os.extsep.join(['profile_defaults',
                                                    FILE_EXT]))
    STANDARD_CONFIG_FILE = jasperpath.config(os.extsep.join(['profile',
                                                             FILE_EXT]))

    def load(self, fname):
        self._config = self._load_yaml(fname)
        self._defaults = self._load_yaml(self.DEFAULTS_FILE)

    def get(self, path):
        path = self.sanitize_path(path)
        value = self._get_value(self._config, path)
        if value is None and self.load_defaults:
            value = self._get_value(self._defaults, path)
        return value

    def set(self, path, value=None):
        path = self.sanitize_path(path)
        conf = self._config
        for component in path[:-1]:
            if component not in conf.keys():
                conf[component] = {}
            conf = conf[component]
        if self.load_defaults and value == self._get_value(self._defaults,
                                                           path):
            if path[-1] in conf:
                conf.pop(path[-1])
        else:
            conf[path[-1]] = value
        if self.autosave:
            self.save()

    def to_dict(self):
        return dict(self._defaults.items() + self._config.items())

    def save(self, output_file=""):
        if not output_file:
            output_file = self._config_file
        with open(output_file, "w") as f:
            return yaml.dump(self._config, f, default_flow_style=False)

    def _load_yaml(self, fname):
        try:
            with open(fname, 'r') as f:
                content = yaml.safe_load(f)
        except IOError:
            self._logger.warning("Unable to open '%s', using empty config.",
                                 fname, exc_info=True)
            content = {}
        else:
            if content is None:
                self._logger.warning("File '%s' seems to be empty.", fname)
                content = {}
        self._logger.debug("File '%s' loaded and parsed.", fname)
        return content

    def _get_value(self, conf, path):
        for component in path:
            if component in conf:
                conf = conf[component]
            else:
                return None
        return copy.copy(conf)

DEFAULT_CONFIG_TYPE = YamlConfig

# Used for backward compatibility
old_config_file = os.path.join(jasperpath.LIB_PATH, os.extsep.join(
    ['profile', YamlConfig.FILE_EXT]))
if (os.path.exists(old_config_file) and
   not os.path.exists(YamlConfig.STANDARD_CONFIG_FILE)):
    logger = logging.getLogger(__name__)
    logger.warning("Using deprecated profile location: '%s'", old_config_file)
    YamlConfig.STANDARD_CONFIG_FILE = old_config_file

# Singleton
Config = DEFAULT_CONFIG_TYPE()
