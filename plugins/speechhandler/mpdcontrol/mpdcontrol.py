# -*- coding: utf-8 -*-
import difflib
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

        self._music = mpdclient.MPDClient(server=server, port=port)

    def get_phrases(self):
        return ["MUSIC", "SPOTIFY"]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, by telling a joke.

        Arguments:
            text -- user-input, typically transcribed speech
            mic -- used to interact with the user (for both input and output)
        """

        mic.say("Please give me a moment, I'm starting the music mode.")

        phrases = [
            'PLAY', 'PAUSE', 'STOP',
            'NEXT', 'PREVIOUS',
            'LOUDER', 'SOFTER',
            'PLAYLIST',
            'CLOSE', 'EXIT'
        ]

        self._logger.debug('Loading playlists...')
        phrases.extend([pl.upper() for pl in self._music.get_playlists()])

        self._logger.debug('Starting music mode...')
        with mic.special_mode('music', phrases):
            self._logger.debug('Music mode started.')
            mic.say('Music mode started!')
            mode_not_stopped = True
            while mode_not_stopped:
                mic.wait_for_keyword()

                # Pause if necessary
                playback_state = self._music.get_playback_state()
                if playback_state == mpdclient.PLAYBACK_STATE_PLAYING:
                    self._music.pause()
                    texts = mic.active_listen()
                    self._music.play()
                else:
                    texts = mic.active_listen()

                text = ''
                if texts:
                    text = texts[0].upper()

                if not text:
                    mic.say('Pardon?')
                    continue

                mode_not_stopped = self.handle_music_command(text, mic)

        mic.say('Music Mode stopped!')
        self._logger.debug("Music mode stopped.")

    def handle_music_command(self, command, mic):
        if 'PLAYLIST' in command:

            # Find playlist name
            text = command.replace('PLAYLIST', '').strip()
            playlists = self._music.get_playlists()
            playlists_upper = [pl.upper() for pl in playlists]
            matches = difflib.get_close_matches(text, playlists_upper)
            if len(matches) > 0:
                playlist_index = playlists_upper.index(matches[0])
                playlist = playlists[playlist_index]
            else:
                playlist = None

            # Load playlist
            if playlist:
                playback_state = self._music.get_playback_state()
                self._music.load_playlist(playlist)
                mic.say('Playlist %s loaded.' % playlist)
                if playback_state == mpdclient.PLAYBACK_STATE_PLAYING:
                    self._music.play()
            else:
                mic.say("Sorry, I can't find a playlist with that name.")
        elif 'STOP' in command:
            self._music.stop()
            mic.say('Music stopped.')
        elif 'PLAY' in command:
            self._music.play()
            song = self._music.get_current_song()
            if song:
                mic.say('Playing %s by %s...' % (song.title, song.artist))
        elif 'PAUSE' in command:
            playback_state = self._music.get_playback_state()
            if playback_state == mpdclient.PLAYBACK_STATE_PLAYING:
                self._music.pause()
                mic.say('Music paused.')
            else:
                mic.say('Music is not playing.')
        elif 'LOUDER' in command:
            mic.say('Increasing volume.')
            self._music.volume(10, relative=True)
        elif 'SOFTER' in command:
            mic.say('Decreasing volume.')
            self._music.volume(-10, relative=True)
        elif any(cmd in command for cmd in ('NEXT', 'PREVIOUS')):
            if 'NEXT' in command:
                mic.say('Next song')
                self._music.play()  # backwards necessary to get mopidy to work
                self._music.next()
            else:
                mic.say('Previous song')
                self._music.play()  # backwards necessary to get mopidy to work
                self._music.previous()
            song = self._music.get_current_song()
            if song:
                mic.say('Playing %s by %s...' % (song.title, song.artist))
        elif any(cmd in command for cmd in ('CLOSE', 'EXIT')):
            return False

        return True

    def is_valid(self, text):
        """
        Returns True if the input is related to jokes/humor.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(phrase in text.upper() for phrase in self.get_phrases())
