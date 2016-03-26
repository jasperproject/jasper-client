# -*- coding: utf-8 -*-
import unittest
import tempfile
import mock
from jasper import testutils
from jasper import brain


class ExamplePlugin(object):
    def __init__(self, phrases, priority=0):
        self.phrases = phrases
        self.priority = priority
        self.info = type('', (object,), {'name': 'foo'})()

    def get_phrases(self):
        return self.phrases

    def get_priority(self):
        return self.priority

    def is_valid(self, text):
        return (text in self.phrases)


class TestBrain(unittest.TestCase):
    def setUp(self):
        self.config = testutils.TestConfiguration()

    def testPriority(self):
        """Does Brain sort modules by priority?"""
        my_brain = brain.Brain(self.config)

        plugin1 = ExamplePlugin(['MOCK1'], priority=1)
        plugin2 = ExamplePlugin(['MOCK1'], priority=999)
        plugin3 = ExamplePlugin(['MOCK2'], priority=998)
        plugin4 = ExamplePlugin(['MOCK1'], priority=0)
        plugin5 = ExamplePlugin(['MOCK2'], priority=-3)

        for plugin in (plugin1, plugin2, plugin3, plugin4, plugin5):
            my_brain.add_plugin(plugin)

        expected_order = [plugin2, plugin3, plugin1, plugin4, plugin5]
        self.assertEqual(expected_order, my_brain.get_plugins())

        input_texts = ['MOCK1']
        plugin, output_text = my_brain.query(input_texts)
        self.assertIs(plugin, plugin2)
        self.assertEqual(input_texts[0], output_text)

        input_texts = ['MOCK2']
        plugin, output_text = my_brain.query(input_texts)
        self.assertIs(plugin, plugin3)
        self.assertEqual(input_texts[0], output_text)

    def testPluginPhraseExtraction(self):
        expected_phrases = ['MOCK1', 'MOCK2']

        my_brain = brain.Brain(self.config)

        my_brain.add_plugin(ExamplePlugin(['MOCK2']))
        my_brain.add_plugin(ExamplePlugin(['MOCK1']))

        extracted_phrases = my_brain.get_plugin_phrases()

        self.assertEqual(expected_phrases, extracted_phrases)

    def testStandardPhraseExtraction(self):
        expected_phrases = ['MOCK']

        my_brain = brain.Brain(self.config)

        with tempfile.TemporaryFile() as f:
            # We can't use mock_open here, because it doesn't seem to work
            # with the 'for line in f' syntax
            f.write("MOCK\n")
            f.seek(0)
            with mock.patch('%s.open' % brain.__name__,
                            return_value=f, create=True):
                extracted_phrases = my_brain.get_standard_phrases()
        self.assertEqual(expected_phrases, extracted_phrases)
