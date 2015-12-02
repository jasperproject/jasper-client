# -*- coding: utf-8 -*-
import copy
import logging
from client import plugin
from . import mpdclient


class MPDControlPlugin(plugin.SpeechHandlerPlugin):
    def __init__(self, *args, **kwargs):
        super(MPDControlPlugin, self).__init__(*args, **kwargs)

        self._logger = logging.getLogger(__name__)

        try:
            server = self.profile['mpdclient']['server']
        except KeyError:
            server = 'localhost'

        try:
            port = int(self.profile['mpdclient']['port'])
        except (KeyError, ValueError) as e:
            port = 6600
            if isinstance(e, ValueError):
                self._logger.warning(
                    "Configured port is invalid, using %d instead",
                    port)

        self._mpdserver = server
        self._mpdport = port

    def get_phrases(self):
        return ["MUSIC", "SPOTIFY"]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, by telling a joke.

        Arguments:
            text -- user-input, typically transcribed speech
            mic -- used to interact with the user (for both input and output)
        """
        self._logger.debug("Preparing to start music module")
        try:
            mpdwrapper = mpdclient.MPDClient(server=self._mpdserver,
                                             port=self._mpdport)
        except:
            self._logger.error("Couldn't connect to MPD server", exc_info=True)
            mic.say("I'm sorry. It seems that Spotify is not enabled. " +
                    "Please read the documentation to learn how to " +
                    "configure Spotify.")
            return

        mic.say("Please give me a moment, I'm loading your Spotify playlists.")

        # FIXME: Make this configurable
        persona = 'JASPER'

        self._logger.debug("Starting music mode")
        music_mode = MusicMode(persona, mic, mpdwrapper)
        music_mode.handle_forever()
        self._logger.debug("Exiting music mode")

        return

    def is_valid(self, text):
        """
        Returns True if the input is related to jokes/humor.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(phrase in text.upper() for phrase in self.get_phrases())


# The interesting part
class MusicMode(object):

    def __init__(self, PERSONA, mic, mpdwrapper):
        self._logger = logging.getLogger(__name__)
        self.persona = PERSONA
        # self.mic - we're actually going to ignore the mic they passed in
        self.music = mpdwrapper

        # index spotify playlists into new dictionary and language models
        phrases = ["STOP", "CLOSE", "PLAY", "PAUSE", "NEXT", "PREVIOUS",
                   "LOUDER", "SOFTER", "LOWER", "HIGHER", "VOLUME",
                   "PLAYLIST"]
        phrases.extend(self.music.get_soup_playlist())

        music_stt_engine = mic.active_stt_engine.get_instance('music', phrases)

        self.mic = copy.copy(mic)
        self.mic.active_stt_engine = music_stt_engine

    def delegate_input(self, input):

        command = input.upper()

        # check if input is meant to start the music module
        if "PLAYLIST" in command:
            command = command.replace("PLAYLIST", "")
        elif "STOP" in command:
            self.mic.say("Stopping music")
            self.music.stop()
            return
        elif "PLAY" in command:
            self.mic.say("Playing %s" % self.music.current_song())
            self.music.play()
            return
        elif "PAUSE" in command:
            self.mic.say("Pausing music")
            # not pause because would need a way to keep track of pause/play
            # state
            self.music.stop()
            return
        elif any(ext in command for ext in ["LOUDER", "HIGHER"]):
            self.mic.say("Louder")
            self.music.volume(interval=10)
            self.music.play()
            return
        elif any(ext in command for ext in ["SOFTER", "LOWER"]):
            self.mic.say("Softer")
            self.music.volume(interval=-10)
            self.music.play()
            return
        elif "NEXT" in command:
            self.mic.say("Next song")
            self.music.play()  # backwards necessary to get mopidy to work
            self.music.next()
            self.mic.say("Playing %s" % self.music.current_song())
            return
        elif "PREVIOUS" in command:
            self.mic.say("Previous song")
            self.music.play()  # backwards necessary to get mopidy to work
            self.music.previous()
            self.mic.say("Playing %s" % self.music.current_song())
            return

        # SONG SELECTION... requires long-loading dictionary and language model
        # songs = self.music.fuzzy_songs(query = command.replace("PLAY", ""))
        # if songs:
        #     self.mic.say("Found songs")
        #     self.music.play(songs = songs)

        #     print("SONG RESULTS")
        #     print("============")
        #     for song in songs:
        #         print("Song: %s Artist: %s" % (song.title, song.artist))

        #     self.mic.say("Playing %s" % self.music.current_song())

        # else:
        #     self.mic.say("No songs found. Resuming current song.")
        #     self.music.play()

        # PLAYLIST SELECTION
        playlists = self.music.fuzzy_playlists(query=command)
        if playlists:
            self.mic.say("Loading playlist %s" % playlists[0])
            self.music.play(playlist_name=playlists[0])
            self.mic.say("Playing %s" % self.music.current_song())
        else:
            self.mic.say("No playlists found. Resuming current song.")
            self.music.play()

        return

    def handle_forever(self):

        self.music.play()
        self.mic.say("Playing %s" % self.music.current_song())

        while True:

            self.mic.wait_for_keyword(self.persona)
            self.music.pause()
            input = self.mic.active_listen()[0]

            if input:
                if "close" in input.lower():
                    self.mic.say("Closing Spotify")
                    return
                self.delegate_input(input)
            else:
                self.mic.say("Pardon?")
                self.music.play()
