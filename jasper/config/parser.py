# -*- coding: utf-8 -*-
import logging
import ConfigParser as configparser


class ConfigParser(configparser.RawConfigParser, object):
    def __init__(self, *args, **kwargs):
        super(ConfigParser, self).__init__(*args, **kwargs)
        self._logger = logging.getLogger(__name__)

    def read(self, filenames):
        if isinstance(filenames, str):
            filenames = [filenames]
        parsed_successfully = []
        for filename in filenames:
            try:
                result = super(ConfigParser, self).read(filename)
            except configparser.Error:
                self._logger.error("Unable to parse file: '%s'", filename)
            else:
                parsed_successfully.extend(result)
        for filename in parsed_successfully:
            self._logger.debug("Successfully parsed file: '%s'", filename)
        return parsed_successfully
