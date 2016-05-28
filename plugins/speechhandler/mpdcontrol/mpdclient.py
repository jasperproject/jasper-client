# -*- coding: utf-8 -*-
import collections
import contextlib
import logging
import socket
import mpd

Song = collections.namedtuple('Song', ['id', 'title', 'artist', 'album'])

PLAYBACK_STATE_PLAYING = 1
PLAYBACK_STATE_PAUSED = 2
PLAYBACK_STATE_STOPPED = 3


class MPDClient(object):
    def __init__(self, server="localhost", port=6600):
        """
            Prepare the client and music variables
        """
        self._server = server
        self._port = port

        self._logger = logging.getLogger(__name__)

        # Caching
        self._playlists = None

    @contextlib.contextmanager
    def connection(self):
        # prepare client
        client = mpd.MPDClient()
        client.timeout = None
        client.idletimeout = None
        try:
            client.connect(self._server, self._port)
            yield client
        except (mpd.ConnectionError, socket.error) as e:
            if isinstance(e, socket.error):
                message = "%s (Errno: %d)" % (e.strerror, e.errno)
            else:
                message = e.message
            self._logger.warning(
                'Connection error while trying to access server %s:%d: %s',
                self._server, self._port, message)
            raise RuntimeError('Connection failed')
        finally:
            try:
                client.close()
            except Exception:
                pass
            try:
                client.disconnect()
            except Exception:
                pass

    def get_playlists(self):
        if self._playlists is not None:
            return self._playlists

        with self.connection() as conn:
            self._playlists = [x["playlist"] for x in conn.listplaylists()]
        return self._playlists

    def get_current_song(self):
        with self.connection() as conn:
            try:
                status = conn.status()
                self._logger.debug('MPD status: %r', status)
                index = int(status['song'])
            except KeyError:
                item = None
            else:
                item = conn.playlistinfo(index)[0]

        if item:
            return Song(id=item['id'],
                        title=item['title'],
                        artist=item['artist'],
                        album=item['album'])

        return None

    def get_playback_state(self):
        with self.connection() as conn:
            status = conn.status()
            state = status['state']
        if state == 'play':
            return PLAYBACK_STATE_PLAYING
        elif state == 'pause':
            return PLAYBACK_STATE_PAUSED
        elif state == 'stop':
            return PLAYBACK_STATE_STOPPED
        else:
            raise RuntimeError('Unknown playback state!')

    def play(self):
        state = self.get_playback_state()
        if state == PLAYBACK_STATE_STOPPED:
            with self.connection() as conn:
                conn.play()
        elif state == PLAYBACK_STATE_PAUSED:
            with self.connection() as conn:
                conn.pause(0)

    def pause(self):
        state = self.get_playback_state()
        if state == PLAYBACK_STATE_PLAYING:
            with self.connection() as conn:
                conn.pause(1)

    def stop(self):
        state = self.get_playback_state()
        if state != PLAYBACK_STATE_STOPPED:
            with self.connection() as conn:
                conn.stop()

    def next(self):
        with self.connection() as conn:
            conn.next()

    def previous(self):
        with self.connection() as conn:
            conn.previous()

    def load_playlist(self, playlist):
        with self.connection() as conn:
            conn.clear()
            conn.load(playlist)

    def volume(self, volume, relative=False):
        with self.connection() as conn:
            if relative:
                orig_volume = int(conn.status()['volume'])
                volume += orig_volume
            if volume > 100:
                volume = 100
            elif volume < 0:
                volume = 0
            conn.setvol(volume)
