# -*- coding: utf-8 -*-
import mpd
import re
import difflib


def reconnect(func, *default_args, **default_kwargs):
    """
        Reconnects before running
    """

    def wrap(self, *default_args, **default_kwargs):
        try:
            self.client.connect(self.server, self.port)
        except:
            pass

        # sometimes not enough to just connect
        try:
            return func(self, *default_args, **default_kwargs)
        except:
            self.client = mpd.MPDClient()
            self.client.timeout = None
            self.client.idletimeout = None
            self.client.connect(self.server, self.port)

            return func(self, *default_args, **default_kwargs)

    return wrap


class Song(object):
    def __init__(self, id, title, artist, album):

        self.id = id
        self.title = title
        self.artist = artist
        self.album = album


class MPDClient(object):
    def __init__(self, server="localhost", port=6600):
        """
            Prepare the client and music variables
        """
        self.server = server
        self.port = port

        # prepare client
        self.client = mpd.MPDClient()
        self.client.timeout = None
        self.client.idletimeout = None
        self.client.connect(self.server, self.port)

        # gather playlists
        self.playlists = [x["playlist"] for x in self.client.listplaylists()]

        # gather songs
        self.client.clear()
        for playlist in self.playlists:
            self.client.load(playlist)

        self.songs = []  # may have duplicates
        # capitalized strings
        self.song_titles = []
        self.song_artists = []

        soup = self.client.playlist()
        for i in range(0, len(soup) / 10):
            index = i * 10
            id = soup[index].strip()
            title = soup[index + 3].strip().upper()
            artist = soup[index + 2].strip().upper()
            album = soup[index + 4].strip().upper()

            self.songs.append(Song(id, title, artist, album))

            self.song_titles.append(title)
            self.song_artists.append(artist)

    @reconnect
    def play(self, songs=False, playlist_name=False):
        """
            Plays the current song or accepts a song to play.

            Arguments:
            songs -- a list of song objects
            playlist_name -- user-defined, something like "Love Song Playlist"
        """
        if songs:
            self.client.clear()
            for song in songs:
                try:  # for some reason, certain ids don't work
                    self.client.add(song.id)
                except:
                    pass

        if playlist_name:
            self.client.clear()
            self.client.load(playlist_name)

        self.client.play()

    @reconnect
    def current_song(self):
        item = self.client.playlistinfo(int(self.client.status()["song"]))[0]
        result = "%s by %s" % (item["title"], item["artist"])
        return result

    @reconnect
    def volume(self, level=None, interval=None):

        if level:
            self.client.setvol(int(level))
            return

        if interval:
            level = int(self.client.status()['volume']) + int(interval)
            self.client.setvol(int(level))
            return

    @reconnect
    def pause(self):
        self.client.pause()

    @reconnect
    def stop(self):
        self.client.stop()

    @reconnect
    def next(self):
        self.client.next()
        return

    @reconnect
    def previous(self):
        self.client.previous()
        return

    def get_soup(self):
        """
        Returns the list of unique words that comprise song and artist titles
        """

        soup = []

        for song in self.songs:
            song_words = song.title.split(" ")
            artist_words = song.artist.split(" ")
            soup.extend(song_words)
            soup.extend(artist_words)

        title_trans = ''.join(chr(c) if chr(c).isupper() or chr(c).islower()
                              else '_' for c in range(256))
        soup = [x.decode('utf-8').encode("ascii", "ignore").upper().translate(
                title_trans).replace("_", "") for x in soup]
        soup = [x for x in soup if x != ""]

        return list(set(soup))

    def get_soup_playlist(self):
        """
        Returns the list of unique words that comprise playlist names
        """

        soup = []

        for name in self.playlists:
            soup.extend(name.split(" "))

        title_trans = ''.join(chr(c) if chr(c).isupper() or chr(c).islower()
                              else '_' for c in range(256))
        soup = [x.decode('utf-8').encode("ascii", "ignore").upper().translate(
                title_trans).replace("_", "") for x in soup]
        soup = [x for x in soup if x != ""]

        return list(set(soup))

    def get_soup_separated(self):
        """
        Returns the list of PHRASES that comprise song and artist titles
        """

        title_soup = [song.title for song in self.songs]
        artist_soup = [song.artist for song in self.songs]

        soup = list(set(title_soup + artist_soup))

        title_trans = ''.join(chr(c) if chr(c).isupper() or chr(c).islower()
                              else '_' for c in range(256))
        soup = [x.decode('utf-8').encode("ascii", "ignore").upper().translate(
                title_trans).replace("_", " ") for x in soup]
        soup = [re.sub(' +', ' ', x) for x in soup if x != ""]

        return soup

    def fuzzy_songs(self, query):
        """
        Returns songs matching a query best as possible on either artist
        field, etc
        """

        query = query.upper()

        matched_song_titles = difflib.get_close_matches(query,
                                                        self.song_titles)
        matched_song_artists = difflib.get_close_matches(query,
                                                         self.song_artists)

        # if query is beautifully matched, then forget about everything else
        strict_priority_title = [x for x in matched_song_titles if x == query]
        strict_priority_artists = [
            x for x in matched_song_artists if x == query]

        if strict_priority_title:
            matched_song_titles = strict_priority_title
        if strict_priority_artists:
            matched_song_artists = strict_priority_artists

        matched_songs_bytitle = [
            song for song in self.songs if song.title in matched_song_titles]
        matched_songs_byartist = [
            song for song in self.songs if song.artist in matched_song_artists]

        matches = list(set(matched_songs_bytitle + matched_songs_byartist))

        return matches

    def fuzzy_playlists(self, query):
        """
                returns playlist names that match query best as possible
        """
        query = query.upper()
        lookup = {n.upper(): n for n in self.playlists}
        results = [lookup[r] for r in difflib.get_close_matches(query, lookup)]
        return results
