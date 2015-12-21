# -*- coding: utf-8 -*-
import logging
import os
import shutil
import yaml

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

        # FIXME: For backwards compatibility, move old config file to newly
        #        created config dir
        old_configfile = os.path.join(paths.PKG_PATH, 'profile.yml')
        new_configfile = paths.config('profile.yml')
        if os.path.exists(old_configfile):
            if os.path.exists(new_configfile):
                self._logger.warning("Deprecated profile file found: '%s'. " +
                                     "Please remove it.", old_configfile)
            else:
                self._logger.warning("Deprecated profile file found: '%s'. " +
                                     "Trying to copy it to new location '%s'.",
                                     old_configfile, new_configfile)
                try:
                    shutil.copy2(old_configfile, new_configfile)
                except shutil.Error:
                    self._logger.error("Unable to copy config file. " +
                                       "Please copy it manually.",
                                       exc_info=True)
                    raise

        # Read config
        self._logger.debug("Trying to read config file: '%s'", new_configfile)
        try:
            with open(new_configfile, "r") as f:
                self._data = yaml.safe_load(f)
        except OSError:
            self._logger.error("Can't open config file: '%s'", new_configfile)
            raise
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as e:
            self._logger.error("Unable to parse config file: %s %s",
                               e.problem.strip(), str(e.problem_mark).strip())
            raise

    def get(self, *args):
        if len(args) == 2:
            (section, option) = args
        elif len(args) == 1:
            (section, option) = (None, args[0])
        else:
            raise ValueError('Invalid number of arguments')
        try:
            if not section:
                value = self._data[option]
            else:
                value = self._data[section][option]
        except KeyError:
            value = None
        return value
