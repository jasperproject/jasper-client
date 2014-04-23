import logging
from modules import *


def logError():
    logger = logging.getLogger('jasper')
    fh = logging.FileHandler('jasper.log')
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.error('Failed to execute module', exc_info=True)


class Brain(object):

    def __init__(self, sender, receiver, profile):
        """
        Instantiates a new Brain object, which cross-references user
        input with a list of modules. Note that the order of brain.modules
        matters, as the Brain will cease execution on the first module
        that accepts a given input.

        Arguments:
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
        """
        self.sender = sender
        self.receiver = receiver
        self.profile = profile
        self.modules = [
            Gmail, Notifications, Birthday, Weather, HN, News, Time, Joke, Life]
        self.modules.append(Unclear)

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
                    module.handle(text, self.sender, self.receiver, self.profile)
                    break
                except:
                    logError()
                    self.sender.say(
                        "I'm sorry. I had some trouble with that operation. Please try again later.")
                    break
