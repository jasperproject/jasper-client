# -*- coding: utf-8 -*-
import difflib
import logging
from jasper import plugin
from . import mpdclient


class MPDControlPlugin(plugin.SpeechHandlerPlugin):
    def __init__(self, *args, **kwargs):
        super(MPDControlPlugin, self).__init__(*args, **kwargs)

        self._logger = logging.getLogger(__name__)

        server = self.config.get('mpdcontrol', 'server')
        port = int(self.config.get('mpdcontrol', 'port'))

        self._music = mpdclient.MPDClient(server=server, port=port)

    def get_phrases(self):
        return [self.gettext('MUSIC'), self.gettext('SPOTIFY')]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, by telling a joke.

        Arguments:
            text -- user-input, typically transcribed speech
            mic -- used to interact with the user (for both input and output)
        """

        _ = self.gettext  # Alias for better readability

        mic.say(_("Please give me a moment, I'm starting the music mode."))

        phrases = [
            _('PLAY'), _('PAUSE'), _('STOP'),
            _('NEXT'), _('PREVIOUS'),
            _('LOUDER'), _('SOFTER'),
            _('PLAYLIST'),
            _('CLOSE'), _('EXIT')
        ]

        self._logger.debug('Loading playlists...')
        phrases.extend([pl.upper() for pl in self._music.get_playlists()])

        self._logger.debug('Starting music mode...')
        with mic.special_mode('music', phrases):
            self._logger.debug('Music mode started.')
            mic.say(_('Music mode started!'))
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
                    mic.say(_('Pardon?'))
                    continue

                mode_not_stopped = self.handle_music_command(text, mic)

        mic.say(_('Music Mode stopped!'))
        self._logger.debug("Music mode stopped.")

    def handle_music_command(self, command, mic):
        _ = self.gettext  # Alias for better readability

        if _('PLAYLIST').upper() in command:
            # Find playlist name
            text = command.replace(_('PLAYLIST'), '').strip()
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
                mic.say(_('Playlist %s loaded.') % playlist)
                if playback_state == mpdclient.PLAYBACK_STATE_PLAYING:
                    self._music.play()
            else:
                mic.say(_("Sorry, I can't find a playlist with that name."))
        elif _('STOP').upper() in command:
            self._music.stop()
            mic.say(_('Music stopped.'))
        elif _('PLAY').upper() in command:
            self._music.play()
            song = self._music.get_current_song()
            if song:
                mic.say(_('Playing {song.title} by {song.artist}...').format(
                    song=song))
        elif _('PAUSE').upper() in command:
            playback_state = self._music.get_playback_state()
            if playback_state == mpdclient.PLAYBACK_STATE_PLAYING:
                self._music.pause()
                mic.say(_('Music paused.'))
            else:
                mic.say(_('Music is not playing.'))
        elif _('LOUDER').upper() in command:
            mic.say(_('Increasing volume.'))
            self._music.volume(10, relative=True)
        elif _('SOFTER').upper() in command:
            mic.say(_('Decreasing volume.'))
            self._music.volume(-10, relative=True)
        elif any(cmd.upper() in command for cmd in (
                _('NEXT'), _('PREVIOUS'))):
            if _('NEXT').upper() in command:
                mic.say(_('Next song'))
                self._music.play()  # backwards necessary to get mopidy to work
                self._music.next()
            else:
                mic.say(_('Previous song'))
                self._music.play()  # backwards necessary to get mopidy to work
                self._music.previous()
            song = self._music.get_current_song()
            if song:
                mic.say(_('Playing {song.title} by {song.artist}...').format(
                    song=song))
        elif any(cmd.upper() in command for cmd in (_('CLOSE'), _('EXIT'))):
            return False

        return True

    def is_valid(self, text):
        """
        Returns True if the input is related to jokes/humor.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(phrase in text.upper() for phrase in self.get_phrases())
