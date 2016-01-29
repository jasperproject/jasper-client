# -*- coding: utf-8 -*-
import logging
from time import sleep
from . import paths
from . import i18n
#  from notifier import Notifier


class Conversation(i18n.GettextMixin):
    def __init__(self, mic, brain, profile):
        translations = i18n.parse_translations(paths.data('locale'))
        i18n.GettextMixin.__init__(self, translations, profile)
        self._logger = logging.getLogger(__name__)
        self.mic = mic
        self.profile = profile
        self.brain = brain
        self.translations = {

        }
        self.suspended = False
        #  self.notifier = Notifier(profile)

    def greet(self):
        if 'first_name' in self.profile:
            salutation = (self.gettext("How can I be of service, %s?")
                          % self.profile["first_name"])
        else:
            salutation = self.gettext("How can I be of service?")
        self.mic.say(salutation)

    def handleInput(self, input):
        if input:
            plugin, text = self.brain.query(input)
            if plugin and text:
                try:
                    plugin.handle(text, self.mic)
                except Exception:
                    self._logger.error('Failed to execute module',
                                       exc_info=True)
                    self.mic.say(self.gettext(
                        "I'm sorry. I had some trouble with that " +
                        "operation. Please try again later."))
                else:
                    self._logger.debug("Handling of phrase '%s' by " +
                                       "module '%s' completed", text,
                                       plugin.info.name)
                    return True
        else:
            self.mic.say(self.gettext("Pardon?"))

        return False

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.debug('Starting to handle conversation.')
        while True:
            if not self.suspended:
                input = self.mic.listen()

            if not self.suspended:
                self.handleInput(input)

            if self.suspended:
                sleep(0.25)

    def suspend(self):
        """
        Suspends converstation handling
        """
        self._logger.debug('Suspending handling conversation.')
        self.suspended = True
        self.mic.cancel_listen()
    
    def resume(self):
        """
        Resumes converstation handling
        """
        self._logger.debug('Resuming handling conversation.')
        self.suspended = False
