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

    def ask(self, question):
        """
            Asks a questions and then returns the response

            Arguments:
            question -- the question to ask
        """
        self.say(question)
        return self.active_listen()


def get_plugin_instance(plugin_class, *extra_args):
    info = type('', (object,), {
        'name': 'pluginunittest',
        'translations': {
            'en-US': gettext.NullTranslations()
            }
        })()
    args = tuple(extra_args) + (info, TEST_PROFILE)
    return plugin_class(*args)
