# -*- coding: utf-8 -*-
from . import paths
from . import pluginstore
from .config import Configuration

TEST_CONFIG = Configuration([])
TEST_CONFIG.read_defaults([paths.data('defaults.cfg')])


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


def get_plugin_instance(path, *extra_args):
    plugins = pluginstore.PluginStore([])
    plugin_info = plugins.parse_plugin(path)
    TEST_CONFIG.read_defaults(
        plugin_info.default_config_file, map_sections=[
            ('Defaults', plugin_info.config_section)])

    args = tuple(extra_args) + (plugin_info, TEST_CONFIG)
    return plugin_info.plugin_class(*args)
