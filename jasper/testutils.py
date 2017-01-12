# -*- coding: utf-8 -*-
import gettext

TEST_PROFILE = {
    'prefers_email': False,
    'timezone': 'US/Eastern',
    'phone_number': '012344321',
    'weather': {
        'location': 'New York',
        'unit': 'Fahrenheit'
    }
}


class TestTTI(object):
    def __init__(self):
        pass


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


def get_genericplugin_instance(plugin_class, *extra_args):
    info = type('', (object,), {
        'name': 'pluginunittest',
        'translations': {
            'en-US': gettext.NullTranslations()
            }
        })()
    args = (info, TEST_PROFILE)+tuple(extra_args)
    return plugin_class(*args)


def get_plugin_instance(plugin_class, *extra_args):
    return get_genericplugin_instance(plugin_class, TestTTI(), TestMic())
