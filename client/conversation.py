from notifier import Notifier
from musicmode import *
from brain import Brain


class Conversation(object):

    def __init__(self, persona, sender, receiver, profile):
        self.persona = persona
        self.sender = sender
        self.receiver = receiver
        self.profile = profile
        self.brain = Brain(sender, receiver, profile)
        self.notifier = Notifier(profile)

    def delegateInput(self, text):
        """A wrapper for querying brain."""

        # check if input is meant to start the music module
        if any(x in text.upper() for x in ["SPOTIFY","MUSIC"]):
            self.sender.say("Please give me a moment, I'm loading your Spotify playlists.")
            music_mode = MusicMode(self.persona, self.mic)
            music_mode.handleForever()
            return


        self.brain.query(text)

    def handleForever(self):
        """Delegates user input to the handling function when activated."""
        while True:

            # Print notifications until empty
            notifications = self.notifier.getAllNotifications()
            for notif in notifications:
                print notif

            try:
                threshold, transcribed = self.receiver.passiveListen(self.persona)
            except KeyboardInterrupt:
                break
            except:
                continue

            if threshold:
                input = self.receiver.activeListen(threshold)
                if input:
                    self.delegateInput(input)
                else:
                    self.sender.say("Pardon?")

        self.notifier.shutdown()
