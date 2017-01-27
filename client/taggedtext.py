#!/usr/bin/env python2
# -*- coding: utf-8-*-
import unittest


class TaggedText(unicode):
    def __new__(cls, u, tags):
        return unicode.__new__(cls, u)

    def __init__(self, u, tags):
        super(self.__class__, self).__init__(u)
        self._tags = tags

    @property
    def tags(self):
        return self._tags


class TestTaggedText(unittest.TestCase):

    def test_unicode(self):
        """Does TaggedText behave like a normal unicode string"""
        t = TaggedText("hello world", {})
        self.assertEqual(t, "hello world")
        self.assertIn("world", t)

    def test_tags(self):
        """Does TaggedText allow access to tags"""
        t = TaggedText("hello world", {})
        self.assertEqual(t.tags, {})

    def test_immutability(self):
        """Does TaggedText disallow assignment"""
        t = TaggedText("hello world", {})
        with self.assertRaises(AttributeError):
            t.tags = {}
