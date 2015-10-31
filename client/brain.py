# -*- coding: utf-8 -*-
import logging
import jasperpath


class Brain(object):
    def __init__(self):
        """
        Instantiates a new Brain object, which cross-references user
        input with a list of modules. Note that the order of brain.modules
        matters, as the Brain will return the first module
        that accepts a given input.
        """

        self._plugins = []
        self._logger = logging.getLogger(__name__)

    def add_plugin(self, plugin):
        self._plugins.append(plugin)
        self._plugins = sorted(
            self._plugins, key=lambda p: p.get_priority(), reverse=True)

    def get_plugins(self):
        return self._plugins

    def get_keyword_phrases(self):
        """
        Gets the keyword phrases from the keywords file in the jasper data dir.

        Returns:
            A list of keyword phrases.
        """
        phrases = []

        with open(jasperpath.data('keyword_phrases'), mode="r") as f:
            for line in f:
                phrase = line.strip()
                if phrase:
                    phrases.append(phrase)

        return phrases

    def get_all_phrases(self):
        """
        Gets phrases from all modules.

        Returns:
            A list of phrases in all modules plus additional phrases passed to
            this function.
        """
        phrases = []

        for plugin in self._plugins:
            phrases.extend(plugin.get_phrases())

        return sorted(list(set(phrases)))

    def query(self, texts):
        """
        Passes user input to the appropriate module, testing it against
        each candidate module's isValid function.

        Arguments:
        text -- user input, typically speech, to be parsed by a module

        Returns:
            A tuple containing a text and the module that can handle it
        """
        for plugin in self._plugins:
            for text in texts:
                if plugin.is_valid(text):
                    self._logger.debug("'%s' is a valid phrase for module " +
                                       "'%s'", text, plugin.info.name)
                    return (plugin, text)
        self._logger.debug("No module was able to handle any of these " +
                           "phrases: %r", texts)
        return (None, None)
