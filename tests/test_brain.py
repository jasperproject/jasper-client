#!/usr/bin/env python2
# -*- coding: utf-8-*-
import unittest
import tempfile
import mock
from client import brain


class TestBrain(unittest.TestCase):
    def testSortByPriority(self):
        """Does Brain sort modules by priority?"""
        my_brain = brain.Brain()
        priorities = filter(lambda m: hasattr(m, 'PRIORITY'), my_brain.modules)
        target = sorted(priorities, key=lambda m: m.PRIORITY, reverse=True)
        self.assertEqual(target, priorities)

    def testPriority(self):
        """Does Brain correctly send query to higher-priority module?"""
        my_brain = brain.Brain()
        input_text = ["hacker news"]
        hn_module = filter(lambda m: m.__name__ == 'HN', my_brain.modules)[0]
        module, text = my_brain.query(input_text)
        self.assertIs(module, hn_module)
        self.assertEqual(input_text[0], text)

    def testPhraseExtraction(self):
        expected_phrases = ['MOCK']

        mock_module = mock.Mock()
        mock_module.WORDS = ['MOCK']

        with mock.patch('client.brain.Brain.get_modules',
                        classmethod(lambda cls: [mock_module])):
            my_brain = brain.Brain()
            extracted_phrases = my_brain.get_all_phrases()
        self.assertEqual(expected_phrases, extracted_phrases)

    def testKeywordPhraseExtraction(self):
        expected_phrases = ['MOCK']

        my_brain = brain.Brain()

        with tempfile.TemporaryFile() as f:
            # We can't use mock_open here, because it doesn't seem to work
            # with the 'for line in f' syntax
            f.write("MOCK\n")
            f.seek(0)
            with mock.patch('%s.open' % brain.__name__,
                            return_value=f, create=True):
                extracted_phrases = my_brain.get_keyword_phrases()
        self.assertEqual(expected_phrases, extracted_phrases)
