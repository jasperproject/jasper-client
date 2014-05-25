import logging
from os import listdir


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

        def get_modules():
            """
            Dynamically loads all the modules in the modules folder and sorts
            them by the PRIORITY key. If no PRIORITY is defined for a given
            module, a priority of 0 is assumed.
            """

            folder = 'modules'

            def get_module_names():
                module_names = [m.replace('.py', '')
                                for m in listdir(folder) if m.endswith('.py')]
                module_names = map(lambda s: folder + '.' + s, module_names)
                return module_names

            def import_module(name):
                mod = __import__(name)
                components = name.split('.')
                for comp in components[1:]:
                    mod = getattr(mod, comp)
                return mod

            def get_module_priority(m):
                try:
                    return m.PRIORITY
                except:
                    return 0

            modules = map(import_module, get_module_names())
            modules = filter(lambda m: hasattr(m, 'WORDS'), modules)
            modules.sort(key=get_module_priority, reverse=True)
            return modules

        self.mic = mic
        self.profile = profile
        self.modules = get_modules()

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
