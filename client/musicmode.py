"""
    Manages the conversation
"""

import os
from mic import Mic
import g2p
from music import *


class MusicMode:

    def __init__(self, PERSONA, mic):
        self.persona = PERSONA
        # self.mic - we're actually going to ignore the mic they passed in
        self.music = Music()

        # index spotify playlists into new dictionary and language models
        original = self.music.get_soup_playlist(
        ) + ["STOP", "CLOSE", "PLAY", "PAUSE",
             "NEXT", "PREVIOUS", "LOUDER", "SOFTER", "LOWER", "HIGHER", "VOLUME", "PLAYLIST"]
        pronounced = g2p.translateWords(original)
        zipped = zip(original, pronounced)
        lines = ["%s %s" % (x, y) for x, y in zipped]

        with open("dictionary_spotify.dic", "w") as f:
            f.write("\n".join(lines) + "\n")

        with open("sentences_spotify.txt", "w") as f:
            f.write("\n".join(original) + "\n")
            f.write("<s> \n </s> \n")
            f.close()

        # make language model
        os.system(
            "text2idngram -vocab sentences_spotify.txt < sentences_spotify.txt -idngram spotify.idngram")
        os.system(
            "idngram2lm -idngram spotify.idngram -vocab sentences_spotify.txt -arpa languagemodel_spotify.lm")

        # create a new mic with the new music models
        self.mic = Mic(
            "languagemodel.lm", "dictionary.dic", "languagemodel_persona.lm",
            "dictionary_persona.dic", "languagemodel_spotify.lm", "dictionary_spotify.dic")

    def delegateInput(self, input):

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

        #     print "SONG RESULTS"
        #     print "============"
        #     for song in songs:
        #         print "Song: %s Artist: %s" % (song.title, song.artist)

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

    def handleForever(self):

        self.music.play()
        self.mic.say("Playing %s" % self.music.current_song())

        while True:

            try:
                threshold, transcribed = self.mic.passiveListen(self.persona)
            except:
                continue

            if threshold:

                self.music.pause()

                input = self.mic.activeListen(MUSIC=True)

                if "close" in input.lower():
                    self.mic.say("Closing Spotify")
                    return

                if input:
                    self.delegateInput(input)
                else:
                    self.mic.say("Pardon?")
                    self.music.play()

if __name__ == "__main__":
    """
        Indexes the Spotify music library to dictionary_spotify.dic and languagemodel_spotify.lm
    """

    musicmode = MusicMode("JASPER", None)
    music = musicmode.music

    original = music.get_soup() + ["STOP", "CLOSE", "PLAY",
                                   "PAUSE", "NEXT", "PREVIOUS", "LOUDER", "SOFTER"]
    pronounced = g2p.translateWords(original)
    zipped = zip(original, pronounced)
    lines = ["%s %s" % (x, y) for x, y in zipped]

    with open("dictionary_spotify.dic", "w") as f:
        f.write("\n".join(lines) + "\n")

    with open("sentences_spotify.txt", "w") as f:
        f.write("\n".join(original) + "\n")
        f.write("<s> \n </s> \n")
        f.close()

    with open("sentences_spotify_separated.txt", "w") as f:
        f.write("\n".join(music.get_soup_separated()) + "\n")
        f.write("<s> \n </s> \n")
        f.close()

    # make language model
    os.system(
        "text2idngram -vocab sentences_spotify.txt < sentences_spotify_separated.txt -idngram spotify.idngram")
    os.system(
        "idngram2lm -idngram spotify.idngram -vocab sentences_spotify.txt -arpa languagemodel_spotify.lm")

    print "Language Model and Dictionary Done"
