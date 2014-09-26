# -*- coding: utf-8-*-
import logging
from notifier import Notifier
from musicmode import *
from brain import Brain
from mpd import MPDClient


class Conversation(object):

    def __init__(self, persona, mic, profile):
        self._logger = logging.getLogger(__name__)
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile)
        self.notifier = Notifier(profile)

    def delegateInput(self, texts):
        """A wrapper for querying brain."""

        # check if input is meant to start the music module
        for text in texts:
            if any(x in text.upper() for x in ["SPOTIFY", "MUSIC"]):
                self._logger.debug("Preparing to start music module")
                # check if mpd client is running
                try:
                    client = MPDClient()
                    client.timeout = None
                    client.idletimeout = None
                    client.connect("localhost", 6600)
                except:
                    self._logger.critical("Can't connect to mpd client, cannot start music mode.", exc_info=True)
                    self.mic.say(
                        "I'm sorry. It seems that Spotify is not enabled. Please read the documentation to learn how to configure Spotify.")
                    return

                self._logger.debug("Starting music mode")
                music_mode = MusicMode(self.persona, self.mic)
                music_mode.handleForever()
                self._logger.debug("Exiting music mode")
                return

        self.brain.query(texts)

    def handleForever(self):
        """Delegates user input to the handling function when activated."""
        self._logger.info("Starting to handle conversation with keyword '%s'.", self.persona)
        while True:
            # Print notifications until empty
            notifications = self.notifier.getAllNotifications()
            for notif in notifications:
                self._logger.info("Got notification: '%s'", str(notif))

            self._logger.debug("Started listening for keyword '%s'", self.persona)
            threshold, transcribed = self.mic.passiveListen(self.persona)
            self._logger.debug("Stopped listening for keyword '%s'", self.persona)

            if not transcribed or not threshold:
                self._logger.info("Nothing has been said or transcribed.")
                continue
            self._logger.info("Keyword '%s' has been said!", self.persona)

            self._logger.debug("Started to listen actively with threshold: %r", threshold)
            input = self.mic.activeListenToAllOptions(threshold)
            self._logger.debug("Stopped to listen actively with threshold: %r", threshold)
            
            if input:
                self.delegateInput(input)
            else:
                self.mic.say("Pardon?")
