# -*- coding: utf-8-*-
"""
A drop-in replacement for the Mic class used during unit testing.
Designed to take pre-arranged inputs as an argument and store any
outputs for inspection. Requires a populated profile (profile.yml).
"""


class Mic:

    def __init__(self, inputs):
        self.inputs = inputs
        self.idx = 0
        self.outputs = []

    def wait_for_keyword(self, keyword="JASPER"):
        return

    def active_listen(self, timeout=3):
        input = self.inputs[self.idx]
        self.idx += 1
        return [input]

    def say(self, phrase, OPTIONS=None):
        self.outputs.append(phrase)
