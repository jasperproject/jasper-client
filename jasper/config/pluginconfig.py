# -*- coding: utf-8 -*-


class PluginConfig(object):
    def __init__(self, config, section):
        self._config = config
        self._section = section

    def get(self, option):
        return self._config.get(self._section, option)

    def getint(self, option):
        return self._config.getint(self._section, option)

    def getfloat(self, option):
        return self._config.getfloat(self._section, option)

    def getbool(self, option):
        return self._config.getbool(self._section, option)

    def getpath(self, option):
        return self._config.getpath(self._section, option)

    def get_global(self, section, option):
        if section.startswith('Plugin '):
            return None
        return self._config.get(section, option)
