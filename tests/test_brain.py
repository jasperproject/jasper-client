#!/usr/bin/env python2
# -*- coding: utf-8-*-
import unittest
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
