from notifier import Notifier
from musicmode import *
from brain import Brain
from mpd import MPDClient

class Conversation(object):

    def __init__(self, persona, mic, profile):
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile)
        self.notifier = Notifier(profile)

    def delegateInput(self, text):
        """A wrapper for querying brain."""

        # check if input is meant to start the music module
        if any(x in text.upper() for x in ["SPOTIFY","MUSIC"]):
            # check if mpd client is running
            try:
                client = MPDClient()
                client.timeout = None
                client.idletimeout = None
                client.connect("localhost", 6600)
            except:
                self.mic.say("I'm sorry. It seems that Spotify is not enabled. Please read the documentation to learn how to configure Spotify.")
                return
            
            self.mic.say("Please give me a moment, I'm loading your Spotify playlists.")
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
                threshold, transcribed = self.mic.passiveListen(self.persona)
            except:
                continue

            if threshold:
                input = self.mic.activeListen(threshold)
                if input:
                    self.delegateInput(input)
                else:
                    self.mic.say("Pardon?")
