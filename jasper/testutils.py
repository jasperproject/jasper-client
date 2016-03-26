# -*- coding: utf-8 -*-
import os.path
from . import paths
from . import pluginstore
from . import config


class TestConfiguration(config.Configuration):
    def __init__(self):
        config.Configuration.__init__(self)
        self.read_defaults([paths.data('defaults.cfg')])

    def set(self, section, option, value):
        if value is None:
            if self._cp.has_section(section) and \
                    self._cp.has_option(section, option):
                self._cp.remove_option(section, option)
        else:
            if not self._cp.has_section(section):
                self._cp.add_section(section)
            self._cp.set(section, option, value)

    def set_from_dict(self, data):
        for section in data.keys():
            for option, value in data[section].items():
                self.set(section, option, value)


class TestMic(object):
    def __init__(self, inputs=[]):
        self.inputs = inputs
        self.idx = 0
        self.outputs = []

    def wait_for_keyword(self, keyword="JASPER"):
        return

    def active_listen(self, timeout=3):
        if self.idx < len(self.inputs):
            self.idx += 1
            return [self.inputs[self.idx - 1]]
        return [""]

    def say(self, phrase):
        self.outputs.append(phrase)


def get_plugin_instance(path, extra_args=[], extra_config={}):
    plugins = pluginstore.PluginStore([])
    plugin_info = plugins.parse_plugin(path)

    config = TestConfiguration()
    config.read_defaults(
        plugin_info.default_config_file, map_sections=[
            ('Defaults', plugin_info.config_section)])
    config.read(os.path.join(path, 'test.cfg'))
    config.set_from_dict(extra_config)

    args = tuple(extra_args) + (plugin_info, config)
    return plugin_info.plugin_class(*args)
