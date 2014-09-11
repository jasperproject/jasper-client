# -*- coding: utf-8-*-
"""
A Speaker handles audio output from Jasper to the user

Speaker methods:
    say - output 'phrase' as speech
    play - play the audio in 'filename'
    is_available - returns True if the platform supports this implementation
"""
import os
import re
import sys
import json
import tempfile
import subprocess
from abc import ABCMeta, abstractmethod

import pyaudio
import wave
try:
    import mad
    import gtts
except ImportError:
    pass

class AbstractSpeaker(object):
    """
    Generic parent class for all speakers
    """

    __metaclass__ = ABCMeta
    
    @classmethod
    @abstractmethod
    def is_available(cls):
        return True

    @abstractmethod
    def say(self, phrase, *args):
        pass

    def play(self, filename, chunksize=1024):
        f = wave.open(filename, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)

        data = f.readframes(chunksize)
        while data:
            stream.write(data)
            data = f.readframes(chunksize)

        stream.stop_stream()
        stream.close()
        p.terminate()

class AbstractMp3Speaker(AbstractSpeaker):
    """
    Generic class that implements the 'play' method for mp3 files
    """
    @classmethod
    def is_available(cls):
        return (super(AbstractMp3Speaker, cls).is_available() and 'mad' in sys.modules.keys())

    def play_mp3(cls, filename):
        f = mad.MadFile(filename)
        p = pyaudio.PyAudio()
        # open stream
        stream = p.open(format=p.get_format_from_width(pyaudio.paInt32),
                        channels=2,
                        rate=f.samplerate(),
                        output=True)
        
        data = f.read()
        while data:
            stream.write(data)
            data = f.read()

        stream.stop_stream()
        stream.close()
        p.terminate()

class eSpeakSpeaker(AbstractSpeaker):
    """
    Uses the eSpeak speech synthesizer included in the Jasper disk image
    Requires espeak to be available
    """

    SLUG = "espeak-tts"

    @classmethod
    def is_available(cls):
        return (super(eSpeakSpeaker, cls).is_available() and subprocess.call(['which','espeak']) == 0)

    def say(self, phrase, voice='default+m3', pitch_adjustment=40, words_per_minute=160):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = ['espeak', '-v', voice,
                         '-p', pitch_adjustment,
                         '-s', words_per_minute,
                         '-w', fname,
                         phrase]
        cmd = [str(x) for x in cmd]
        subprocess.call(cmd)
        self.play(fname)
        os.remove(fname)

class saySpeaker(AbstractSpeaker):
    """
    Uses the OS X built-in 'say' command
    """

    SLUG = "osx-tts"

    @classmethod
    def is_available(cls):
        return (super(saySpeaker, cls).is_available() and subprocess.call(['which','say']) == 0)

    def say(self, phrase):
        cmd = ['say', str(phrase)]
        subprocess.call(cmd)

    def play(self, filename):
        cmd = ['afplay', str(filename)]
        subprocess.call(cmd)

class picoSpeaker(AbstractSpeaker):
    """
    Uses the svox-pico-tts speech synthesizer
    Requires pico2wave to be available
    """

    SLUG = "pico-tts"

    @classmethod
    def is_available(cls):
        return (super(picoSpeaker, cls).is_available() and subprocess.call(['which','pico2wave']) == 0)

    @property
    def languages(self):
        cmd = ['pico2wave', '-l', 'NULL',
                            '-w', '/dev/null',
                            'NULL']
        with tempfile.SpooledTemporaryFile() as f:
            subprocess.call(cmd, stderr=f)
            f.seek(0)
            output = f.read()
        pattern = re.compile(r'Unknown language: NULL\nValid languages:\n((?:[a-z]{2}-[A-Z]{2}\n)+)')
        matchobj = pattern.match(output)
        if not matchobj:
            raise RuntimeError("pico2wave: valid languages not detected")
        langs = matchobj.group(1).split()
        return langs

    def say(self, phrase, language="en-US"):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = ['pico2wave', '--wave', fname]
        if language:
            if language not in self.languages:
                raise ValueError("Language '%s' not supported by '%s'", language, cmd[0])
            cmd.extend(['-l',language])
        cmd.append(phrase)

        subprocess.call(cmd)
        self.play(fname)
        os.remove(fname)

class googleSpeaker(AbstractMp3Speaker):
    """
    Uses the Google TTS online translator
    Requires pymad and gTTS to be available
    """

    SLUG = "google-tts"

    @classmethod
    def is_available(cls):
        return (super(googleSpeaker, cls).is_available() and 'gtts' in sys.modules.keys())

    @property
    def languages(self):
        langs = ['af', 'sq', 'ar', 'hy', 'ca', 'zh-CN', 'zh-TW', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'fi', 'fr', 'de',
                 'el', 'ht', 'hi', 'hu', 'is', 'id', 'it', 'ja', 'ko', 'la', 'lv', 'mk', 'no', 'pl', 'pt', 'ro', 'ru',
                 'sr', 'sk', 'es', 'sw', 'sv', 'ta', 'th', 'tr', 'vi', 'cy']
        return langs

    def say(self, phrase, language='en'):
        if language not in self.languages:
            raise ValueError("Language '%s' not supported by '%s'", language, cmd[0])
        tts = gtts.gTTS(text=phrase, lang=language)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmpfile = f.name
        tts.save(tmpfile)
        self.play_mp3(tmpfile)
        os.remove(tmpfile)

TTS_ENGINES = [googleSpeaker, picoSpeaker, eSpeakSpeaker, saySpeaker]

def newSpeaker():
    """
    Returns:
        A speaker implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    tts_engine = None

    # Try to get tts_engine from config
    if os.path.exists('profile.yml'):
        with open('profile.yml', 'r') as f:
            profile = yaml.safe_load(f)
            if 'tts_engine' in profile:
                tts_engine = profile['tts_engine']
    
    # Default values if config file does not exist or option not set
    if not tts_engine:
        if platform.system() == 'darwin':
            tts_engine = 'osx-tts'
        else:
            tts_engine = 'espeak-tts'
    
    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and engine.SLUG == tts_engine, TTS_ENGINES)
    if len(selected_engines) == 0:
        raise ValueError("No TTS engine found for slug '%s'" % tts_engine)
    else:
        if len(selected_engines) > 1:
            print("WARNING: Multiple TTS engines found for slug '%s'. This is most certainly a bug." % tts_engine)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError("TTS engine '%s' is not available (due to missing dependencies, missing dependencies, etc.)" % tts_engine)
        return engine()
