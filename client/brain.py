# -*- coding: utf-8 -*-
import logging
from . import paths


class Brain(object):
    def __init__(self, config):
        """
        Instantiates a new Brain object, which cross-references user
        input with a list of modules. Note that the order of brain.modules
        matters, as the Brain will return the first module
        that accepts a given input.
        """

        self._plugins = []
        self._notifier = None
        self._logger = logging.getLogger(__name__)
        self._config = config

    def add_plugin(self, plugin):
        self._plugins.append(plugin)
        self._plugins = sorted(
            self._plugins, key=lambda p: p.get_priority(), reverse=True)

    def get_plugins(self):
        return self._plugins

    def set_notifier(self, notifier):
        """
        Helper method to set the brain notifier object.
        """
        self._notifier = notifier

    def get_notifier(self):
        """
        Helper method to get the brain notifier object.
        """
        return self._notifier

    def get_standard_phrases(self):
        """
        Gets the standard phrases (i.e. phrases that occur frequently in
        normal conversations) from a file in the jasper data dir.

        Returns:
            A list of standard phrases.
        """
        try:
            language = self._config['language']
        except KeyError:
            language = None
        if not language:
            language = 'en-US'

        phrases = []

        with open(paths.data('standard_phrases', "%s.txt" % language),
                  mode="r") as f:
            for line in f:
                phrase = line.strip()
                if phrase:
                    phrases.append(phrase)

        return phrases

    def get_plugin_phrases(self):
        """
        Gets phrases from all plugins.

        Returns:
            A list of phrases from all plugins.
        """
        phrases = []

        for plugin in self._plugins:
            phrases.extend(plugin.get_phrases())

        return sorted(list(set(phrases)))

    def get_all_phrases(self):
        """
        Gets a combined list consisting of standard phrases and plugin phrases.

        Returns:
            A list of phrases.
        """
        return self.get_standard_phrases() + self.get_plugin_phrases()

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
