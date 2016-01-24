# -*- coding: utf-8 -*-
import logging
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
        #  self.notifier = Notifier(profile)

    def greet(self):
        if 'first_name' in self.profile:
            salutation = (self.gettext("How can I be of service, %s?")
                          % self.profile["first_name"])
        else:
            salutation = self.gettext("How can I be of service?")
        self.mic.say(salutation)

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.debug('Starting to handle conversation.')
        while True:
            # Print notifications until empty
            """notifications = self.notifier.get_all_notifications()
            for notif in notifications:
                self._logger.info("Received notification: '%s'", str(notif))"""

            input = self.mic.listen()

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
            else:
                self.mic.say(self.gettext("Pardon?"))
