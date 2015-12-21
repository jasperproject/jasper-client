# -*- coding: utf-8 -*-
import logging
import ConfigParser as configparser


class ConfigParser(configparser.RawConfigParser, object):
    def __init__(self, *args, **kwargs):
        super(ConfigParser, self).__init__(*args, **kwargs)
        self._logger = logging.getLogger(__name__)

    def read(self, filenames, map_sections=[]):
        if isinstance(filenames, str):
            filenames = [filenames]
        parsed_successfully = []
        for filename in filenames:
            try:
                if not map_sections:
                    result = super(ConfigParser, self).read(filename)
                else:
                    result = self._read_sections(filename, map_sections)
            except configparser.Error:
                self._logger.error("Unable to parse file: '%s'", filename)
            else:
                parsed_successfully.extend(result)
        for filename in parsed_successfully:
            self._logger.debug("Successfully parsed file: '%s'", filename)
        return parsed_successfully

    def _read_sections(self, filename, map_sections):
        self._logger.debug("Mapping sections %r from '%s'",
                           map_sections, filename)
        cp = configparser.RawConfigParser()
        result = cp.read(filename)
        i = 0
        for src, dst in map_sections:
            if not cp.has_section(src):
                continue
            if not self.has_section(dst):
                self.add_section(dst)
            for option, value in cp.items(src):
                self.set(dst, option, value)
                i += 1
        if i == 0:
            result = []
        return result
