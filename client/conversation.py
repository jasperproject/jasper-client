# -*- coding: utf-8-*-
import logging
from notifier import Notifier
from brain import Brain


class Conversation(object):

    def __init__(self, persona, mic, profile):
        self._logger = logging.getLogger(__name__)
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile)
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
                self.brain.query(input)
            else:
                self.mic.say("Pardon?")
