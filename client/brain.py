# -*- coding: utf-8-*-
import logging
import os
import sys
import pkgutil
import importlib


def logError():
    logger = logging.getLogger('jasper')
    fh = logging.FileHandler('jasper.log')
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.error('Failed to execute module', exc_info=True)


class Brain(object):

    def __init__(self, mic, profile):
        """
        Instantiates a new Brain object, which cross-references user
        input with a list of modules. Note that the order of brain.modules
        matters, as the Brain will cease execution on the first module
        that accepts a given input.

        Arguments:
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
        """

        self.mic = mic
        self.profile = profile
        self.modules = self.get_modules()

    @classmethod
    def get_modules(cls):
        """
        Dynamically loads all the modules in the modules folder and sorts
        them by the PRIORITY key. If no PRIORITY is defined for a given
        module, a priority of 0 is assumed.
        """

        module_locations = [os.path.join(os.path.dirname(__file__), 'modules')]
        module_names = [name for loader, name, ispkg in pkgutil.iter_modules(module_locations)]
        modules = []
        for name in module_names:
            mod = importlib.import_module("modules.%s" % name)
            if hasattr(mod, 'WORDS'):                
                modules.append(mod)
        modules.sort(key=lambda mod: mod.PRIORITY if hasattr(mod,'PRIORITY') else 0, reverse=True)
        return modules

    def query(self, text):
        """
        Passes user input to the appropriate module, testing it against
        each candidate module's isValid function.

        Arguments:
        text -- user input, typically speech, to be parsed by a module
        """
        for module in self.modules:
            if module.isValid(text):

                try:
                    module.handle(text, self.mic, self.profile)
                    break
                except:
                    logError()
                    self.mic.say(
                        "I'm sorry. I had some trouble with that operation. Please try again later.")
                    break
