# -*- coding: utf-8-*-
import logging
import pkgutil
import jasperpath


class Brain(object):

    def __init__(self):
        """
        Instantiates a new Brain object, which cross-references user
        input with a list of modules. Note that the order of brain.modules
        matters, as the Brain will return the first module
        that accepts a given input.
        """

        self.modules = self.get_modules()
        self._logger = logging.getLogger(__name__)

    @classmethod
    def get_modules(cls):
        """
        Dynamically loads all the modules in the modules folder and sorts
        them by the PRIORITY key. If no PRIORITY is defined for a given
        module, a priority of 0 is assumed.
        """

        logger = logging.getLogger(__name__)
        locations = [jasperpath.PLUGIN_PATH]
        logger.debug("Looking for modules in: %s",
                     ', '.join(["'%s'" % location for location in locations]))
        modules = []
        for finder, name, ispkg in pkgutil.walk_packages(locations):
            try:
                loader = finder.find_module(name)
                mod = loader.load_module(name)
            except:
                logger.warning("Skipped module '%s' due to an error.", name,
                               exc_info=True)
            else:
                if hasattr(mod, 'WORDS'):
                    logger.debug("Found module '%s' with words: %r", name,
                                 mod.WORDS)
                    modules.append(mod)
                else:
                    logger.warning("Skipped module '%s' because it misses " +
                                   "the WORDS constant.", name)
        modules.sort(key=lambda mod: mod.PRIORITY if hasattr(mod, 'PRIORITY')
                     else 0, reverse=True)
        return modules

    def get_phrases_from_module(self, module):
        """
        Gets phrases from a module.

        Arguments:
            module -- a module reference

        Returns:
            The list of phrases in this module.
        """
        return module.WORDS if hasattr(module, 'WORDS') else []

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

        for module in self.modules:
            phrases.extend(self.get_phrases_from_module(module))

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
        for module in self.modules:
            for text in texts:
                if module.is_valid(text):
                    self._logger.debug("'%s' is a valid phrase for module " +
                                       "'%s'", text, module.__name__)
                    return (module, text)
        self._logger.debug("No module was able to handle any of these " +
                           "phrases: %r", texts)
        return (None, None)
