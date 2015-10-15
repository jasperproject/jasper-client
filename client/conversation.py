# -*- coding: utf-8-*-
import logging
from notifier import Notifier


class Conversation(object):

    def __init__(self, persona, mic, brain, profile):
        self._logger = logging.getLogger(__name__)
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = brain
        self.notifier = Notifier(profile)

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.info("Starting to handle conversation with keyword '%s'.",
                          self.persona)
        while True:
            # Print notifications until empty
            notifications = self.notifier.get_all_notifications()
            for notif in notifications:
                self._logger.info("Received notification: '%s'", str(notif))

            input = self.mic.listen()

            if input:
                module, text = self.brain.query(input)
                if module and text:
                    try:
                        module.handle(input, self.mic, self.profile)
                    except:
                        self._logger.error('Failed to execute module',
                                           exc_info=True)
                        self.mic.say("I'm sorry. I had some trouble with " +
                                     "that operation. Please try again later.")
                    else:
                        self._logger.debug("Handling of phrase '%s' by " +
                                           "module '%s' completed", text,
                                           module.__name__)
            else:
                self.mic.say("Pardon?")
